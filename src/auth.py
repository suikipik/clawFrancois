"""Authentication: pairing secret generation and user ID whitelist."""

from __future__ import annotations

import secrets
from pathlib import Path

from src.config import BridgeConfig


def generate_pairing_secret(length: int = 12) -> str:
    return secrets.token_urlsafe(length)[:length]


class AuthManager:
    def __init__(self, config: BridgeConfig, config_path: Path | None = None) -> None:
        self._config = config
        self._config_path = config_path
        self._allowed_user_ids: set[int] = set(config.allowed_user_ids)

    @property
    def pairing_secret(self) -> str:
        return self._config.pairing_secret

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self._allowed_user_ids

    def pair(self, user_id: int, secret: str) -> bool:
        if secret != self._config.pairing_secret:
            return False
        self._allowed_user_ids.add(user_id)
        self._persist()
        return True

    def _persist(self) -> None:
        self._config.allowed_user_ids = sorted(self._allowed_user_ids)
        if self._config_path:
            self._config.save(self._config_path)
