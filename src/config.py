"""Bridge configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_CONFIG_PATH = Path.home() / ".claude-bridge" / "config.json"


@dataclass
class BridgeConfig:
    bot_token: str
    pairing_secret: str = ""
    allowed_user_ids: list[int] = field(default_factory=list)
    max_prompt_length: int = 10_000
    edit_interval_ms: int = 1_000
    bind_address: str = "127.0.0.1"
    whisper_model: str = "base"
    max_audio_duration: int = 300

    @classmethod
    def from_file(cls, path: Path | None = None) -> BridgeConfig:
        path = path or _DEFAULT_CONFIG_PATH
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        data = json.loads(path.read_text())
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> BridgeConfig:
        if not data.get("bot_token"):
            raise ValueError("bot_token is required")
        return cls(
            bot_token=data["bot_token"],
            pairing_secret=data.get("pairing_secret", ""),
            allowed_user_ids=data.get("allowed_user_ids", []),
            max_prompt_length=data.get("max_prompt_length", 10_000),
            edit_interval_ms=data.get("edit_interval_ms", 1_000),
            bind_address=data.get("bind_address", "127.0.0.1"),
            whisper_model=data.get("whisper_model", "base"),
            max_audio_duration=data.get("max_audio_duration", 300),
        )

    def save(self, path: Path | None = None) -> None:
        path = path or _DEFAULT_CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "bot_token": self.bot_token,
            "pairing_secret": self.pairing_secret,
            "allowed_user_ids": self.allowed_user_ids,
            "max_prompt_length": self.max_prompt_length,
            "edit_interval_ms": self.edit_interval_ms,
            "bind_address": self.bind_address,
            "whisper_model": self.whisper_model,
            "max_audio_duration": self.max_audio_duration,
        }
        path.write_text(json.dumps(data, indent=2) + "\n")
