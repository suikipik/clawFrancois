# clawdfrancois Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-12

## Active Technologies
- Python 3.11+ (with `from __future__ import annotations` for 3.9 compat) + python-telegram-bot 22.x (existing), openai-whisper CLI (new, external) (002-whisper-voice-transcription)
- Temporary files only (OS temp directory, cleaned up after use) (002-whisper-voice-transcription)
- JSON file (`~/.claude-bridge/sessions.json`) (005-session-persistence)

- Python 3.11+ + python-telegram-bot 22.x (async Telegram Bot API wrapper) (001-mobile-cli-bridge)

## Project Structure

```text
src/
tests/
```

## Commands

cd src && pytest && ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 005-session-persistence: Added Python 3.11+ (with `from __future__ import annotations` for 3.9 compat) + python-telegram-bot 22.x (existing)
- 002-whisper-voice-transcription: Added Python 3.11+ (with `from __future__ import annotations` for 3.9 compat) + python-telegram-bot 22.x (existing), openai-whisper CLI (new, external)

- 001-mobile-cli-bridge: Added Python 3.11+ + python-telegram-bot 22.x (async Telegram Bot API wrapper)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
