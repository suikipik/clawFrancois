"""Session state management and prompt execution tracking."""

from __future__ import annotations

import asyncio
import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class SessionState(enum.Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    ERROR = "error"


@dataclass
class PromptExecution:
    prompt_text: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    exit_code: int | None = None
    output_chars: int = 0


class Session:
    def __init__(self, user_id: int, chat_id: int) -> None:
        self.user_id = user_id
        self.chat_id = chat_id
        self.state = SessionState.IDLE
        self.current_process: asyncio.subprocess.Process | None = None
        self.message_id: int | None = None
        self.buffer: str = ""
        self.last_edit_time: datetime | None = None
        self.current_execution: PromptExecution | None = None

    def start_execution(self, prompt_text: str) -> PromptExecution:
        if self.state == SessionState.EXECUTING:
            raise RuntimeError("A prompt is already running")
        self.state = SessionState.EXECUTING
        self.current_execution = PromptExecution(prompt_text=prompt_text)
        self.buffer = ""
        self.message_id = None
        return self.current_execution

    def complete_execution(self, exit_code: int) -> None:
        if self.current_execution:
            self.current_execution.completed_at = datetime.now(timezone.utc)
            self.current_execution.exit_code = exit_code
        self.current_process = None
        self.state = SessionState.IDLE if exit_code == 0 else SessionState.ERROR

    def reset(self) -> None:
        self.state = SessionState.IDLE
        self.current_process = None
        self.current_execution = None
        self.buffer = ""
        self.message_id = None
        self.last_edit_time = None
