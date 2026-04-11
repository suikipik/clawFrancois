"""Shared test fixtures for Claude Mobile Bridge."""

import pytest

from src.config import BridgeConfig


@pytest.fixture
def sample_config(tmp_path):
    """Provide a BridgeConfig with test defaults."""
    return BridgeConfig(
        bot_token="test-token-123",
        pairing_secret="testsecret",
        allowed_user_ids=[],
        max_prompt_length=10000,
        edit_interval_ms=1000,
        bind_address="127.0.0.1",
    )
