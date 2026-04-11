"""Entry point for python -m claude_bridge."""

from __future__ import annotations

import logging
import signal
import sys
from pathlib import Path

from telegram.ext import ApplicationBuilder

from src.auth import AuthManager, generate_pairing_secret
from src.config import BridgeConfig
from src.telegram_adapter import TelegramAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    config_path = Path.home() / ".claude-bridge" / "config.json"

    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    try:
        config = BridgeConfig.from_file(config_path)
    except FileNotFoundError:
        logger.error("Config file not found: %s", config_path)
        logger.error("Copy config.example.json to %s and set your bot_token.", config_path)
        sys.exit(1)
    except ValueError as e:
        logger.error("Invalid config: %s", e)
        sys.exit(1)

    # Generate pairing secret if not set
    if not config.pairing_secret:
        config.pairing_secret = generate_pairing_secret()
        config.save(config_path)

    print(f"\nBridge started. Pairing secret: {config.pairing_secret}")
    print(f'Send "/pair {config.pairing_secret}" to your bot in Telegram.\n')

    auth_manager = AuthManager(config, config_path)

    adapter = TelegramAdapter(
        auth_manager=auth_manager,
        max_prompt_length=config.max_prompt_length,
        edit_interval_ms=config.edit_interval_ms,
    )

    app = ApplicationBuilder().token(config.bot_token).build()
    adapter.register_handlers(app)

    # Graceful shutdown: clean up subprocesses
    def _shutdown_handler(signum, frame):
        logger.info("Shutting down...")
        # The application's stop() will be called by run_polling on signal
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown_handler)

    logger.info("Starting Telegram polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
