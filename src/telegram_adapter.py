"""Telegram bot handlers and message editing for streamed output."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.auth import AuthManager
from src.bridge import run_prompt
from src.session import Session, SessionState

logger = logging.getLogger(__name__)

_TELEGRAM_MAX_LENGTH = 4000  # Stay below 4096 limit
_COMPLETION_MARKER = "\n\n---"
_ERROR_MARKER = "\n\n--- (error)"


class TelegramAdapter:
    def __init__(
        self,
        auth_manager: AuthManager,
        max_prompt_length: int = 10_000,
        edit_interval_ms: int = 1_000,
    ) -> None:
        self._auth = auth_manager
        self._max_prompt_length = max_prompt_length
        self._edit_interval_s = edit_interval_ms / 1000.0
        self._sessions: dict[int, Session] = {}
        self._start_time = datetime.now(timezone.utc)

    def _get_or_create_session(self, user_id: int, chat_id: int) -> Session:
        if user_id not in self._sessions:
            self._sessions[user_id] = Session(user_id=user_id, chat_id=chat_id)
        return self._sessions[user_id]

    # -- Command handlers --

    async def handle_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.message.reply_text(
            "Welcome to Claude Mobile Bridge!\n\n"
            "To get started, send the pairing secret from your terminal:\n"
            "/pair <secret>"
        )

    async def handle_pair(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not context.args:
            await update.message.reply_text("Usage: /pair <secret>")
            return

        secret = context.args[0]
        user_id = update.effective_user.id

        if self._auth.pair(user_id, secret):
            await update.message.reply_text(
                "Paired successfully! Send any message as a prompt."
            )
        else:
            await update.message.reply_text("Invalid pairing secret.")

    async def handle_stop(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id
        if not self._auth.is_authorized(user_id):
            await update.message.reply_text(
                "You are not authorized. Send /pair <secret> to connect."
            )
            return

        session = self._sessions.get(user_id)
        if session and session.state == SessionState.EXECUTING and session.current_process:
            try:
                session.current_process.terminate()
            except ProcessLookupError:
                pass
            session.reset()
            await update.message.reply_text("Execution stopped.")
        else:
            await update.message.reply_text("Nothing is running.")

    async def handle_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id
        if not self._auth.is_authorized(user_id):
            await update.message.reply_text(
                "You are not authorized. Send /pair <secret> to connect."
            )
            return

        session = self._sessions.get(user_id)
        state = session.state.value if session else "idle"

        uptime = datetime.now(timezone.utc) - self._start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        import shutil
        cli_available = shutil.which("claude") is not None

        lines = [
            f"State: {state}",
            f"Uptime: {hours}h {minutes}m {seconds}s",
            f"CLI available: {'yes' if cli_available else 'no'}",
        ]
        await update.message.reply_text("\n".join(lines))

    # -- Message handler --

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id

        if not self._auth.is_authorized(user_id):
            await update.message.reply_text(
                "You are not authorized. Send /pair <secret> to connect."
            )
            return

        prompt = update.message.text
        if not prompt:
            return

        if len(prompt) > self._max_prompt_length:
            await update.message.reply_text(
                f"Prompt too long ({len(prompt)} chars). "
                f"Max is {self._max_prompt_length}."
            )
            return

        chat_id = update.effective_chat.id
        session = self._get_or_create_session(user_id, chat_id)

        if session.state == SessionState.EXECUTING:
            await update.message.reply_text(
                "A prompt is already running. Send /stop to cancel it."
            )
            return

        # Reset from error state if needed
        if session.state == SessionState.ERROR:
            session.reset()

        execution = session.start_execution(prompt)

        # Send initial message
        msg = await update.message.reply_text("Thinking...")
        session.message_id = msg.message_id
        accumulated = ""
        last_edit = time.monotonic()

        try:
            async for chunk in run_prompt(prompt, session):
                accumulated += chunk
                execution.output_chars = len(accumulated)

                now = time.monotonic()
                elapsed = now - last_edit
                should_edit = (
                    elapsed >= self._edit_interval_s
                    or len(accumulated) - len(session.buffer) >= 50
                )

                if should_edit:
                    display_text = accumulated
                    if len(display_text) > _TELEGRAM_MAX_LENGTH:
                        # Send current content as final, start new message
                        try:
                            await context.bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=session.message_id,
                                text=session.buffer or accumulated[:_TELEGRAM_MAX_LENGTH],
                            )
                        except BadRequest as e:
                            if "message is not modified" not in str(e).lower():
                                raise

                        # Start new message with overflow content
                        new_msg = await context.bot.send_message(
                            chat_id=chat_id,
                            text=accumulated[len(session.buffer):] if session.buffer else accumulated[_TELEGRAM_MAX_LENGTH:],
                        )
                        session.message_id = new_msg.message_id
                        session.buffer = accumulated
                    else:
                        try:
                            await context.bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=session.message_id,
                                text=display_text,
                            )
                        except BadRequest as e:
                            if "message is not modified" not in str(e).lower():
                                raise

                        session.buffer = accumulated

                    last_edit = now

            # Completion: final edit with marker
            exit_code = execution.exit_code or 0
            marker = _COMPLETION_MARKER if exit_code == 0 else _ERROR_MARKER
            final_text = accumulated + marker

            # Handle overflow for final text
            if len(final_text) > _TELEGRAM_MAX_LENGTH and session.buffer != accumulated:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=session.message_id,
                        text=accumulated[:_TELEGRAM_MAX_LENGTH],
                    )
                except BadRequest as e:
                    if "message is not modified" not in str(e).lower():
                        raise
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=accumulated[_TELEGRAM_MAX_LENGTH:] + marker,
                )
            else:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=session.message_id,
                        text=final_text[:_TELEGRAM_MAX_LENGTH] if len(final_text) > _TELEGRAM_MAX_LENGTH else final_text,
                    )
                except BadRequest as e:
                    if "message is not modified" not in str(e).lower():
                        raise

            session.complete_execution(exit_code)

        except Exception:
            logger.exception("Error during prompt execution")
            session.complete_execution(1)
            try:
                error_text = (accumulated or "Thinking...") + _ERROR_MARKER
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=session.message_id,
                    text=error_text[:_TELEGRAM_MAX_LENGTH],
                )
            except BadRequest:
                pass

    def register_handlers(self, app: Application) -> None:
        app.add_handler(CommandHandler("start", self.handle_start))
        app.add_handler(CommandHandler("pair", self.handle_pair))
        app.add_handler(CommandHandler("stop", self.handle_stop))
        app.add_handler(CommandHandler("status", self.handle_status))
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
