# Implementation Plan: Claude Mobile Bridge

**Branch**: `001-mobile-cli-bridge` | **Date**: 2026-04-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-mobile-cli-bridge/spec.md`

## Summary

Build a local bridge service that connects a Telegram bot to the
Claude CLI. The user sends prompts via Telegram; the bridge forwards
them to `claude -p` with streaming JSON output; streamed tokens are
buffered and pushed back to Telegram via message editing, creating a
live terminal-like experience on mobile.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: python-telegram-bot 22.x (async Telegram Bot API wrapper)
**Storage**: Local JSON config file (`~/.claude-bridge/config.json`); no database
**Testing**: pytest + pytest-asyncio
**Target Platform**: macOS, Linux (local machine)
**Project Type**: CLI service (Telegram bot + Claude CLI bridge)
**Performance Goals**: First token visible on Telegram within 5 seconds of prompt submission; message edits at ~1/sec
**Constraints**: Telegram 4096 char message limit; 1 edit/sec rate limit; single-user single-prompt-at-a-time
**Scale/Scope**: Single user, single machine, one active prompt at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Execution | ✅ PASS | CLI runs locally via subprocess. Telegram is transport only — prompts go in, text comes out. No remote execution. |
| II. Security by Default | ✅ PASS | Two-layer auth: pairing secret + Telegram user ID whitelist. Bot rejects unauthenticated messages. Bridge binds to localhost. |
| III. Streaming-First Output | ✅ PASS | Claude CLI invoked with `--output-format stream-json --include-partial-messages`. Tokens buffered and pushed to Telegram via message editing at ~1s intervals. |
| IV. Client-Agnostic Architecture | ✅ PASS | Bridge core (CLI subprocess, token management, streaming buffer) is independent of Telegram. Telegram adapter is a separate module. Future clients plug in without core changes. |
| V. Simplicity and Reuse | ✅ PASS | Telegram Bot API is free, zero mobile-side development. Single external dependency (python-telegram-bot). User opens existing Telegram app. |

**Gate result**: All principles satisfied. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/001-mobile-cli-bridge/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── telegram-bot-commands.md  # Phase 1 output
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── __main__.py          # Entry point: python -m claude_bridge
├── config.py            # BridgeConfig loading and validation
├── bridge.py            # Core CLI bridge: spawn, stream, buffer
├── auth.py              # Token generation, pairing, user whitelist
├── session.py           # Session state management
└── telegram_adapter.py  # Telegram bot handlers and message editing

tests/
├── conftest.py          # Shared fixtures
├── test_config.py       # Config loading tests
├── test_bridge.py       # CLI bridge streaming tests
├── test_auth.py         # Auth and pairing tests
├── test_session.py      # Session state tests
└── test_telegram.py     # Telegram adapter integration tests

config.example.json      # Example configuration file
requirements.txt         # Python dependencies
```

**Structure Decision**: Single project layout. The bridge is a simple
Python package with one external dependency. No frontend, no database,
no monorepo complexity.

## Complexity Tracking

No constitution violations to justify.

## Key Technical Decisions

### D1: Claude CLI Invocation

```bash
claude -p --output-format stream-json --include-partial-messages --bare "<prompt>"
```

- `--bare` skips hooks/plugins for clean subprocess use.
- Stream-json emits one JSON event per line as tokens arrive.
- Parse each line, extract text content, append to buffer.

### D2: Telegram Streaming via Message Editing

- Send initial "Thinking..." message on prompt receipt.
- Buffer tokens from CLI stdout.
- Edit message every ~1 second with accumulated text.
- If text exceeds 4000 chars, send new message, continue there.
- On completion, append `---` marker.
- Catch "message is not modified" errors silently.

### D3: Authentication Flow

1. Bridge generates cryptographic pairing secret at startup.
2. Secret printed to terminal.
3. User sends `/pair <secret>` to bot.
4. Bot adds user's Telegram ID to allowed list.
5. All subsequent messages gated by user ID whitelist.
6. Whitelist persisted to config file for restart survival.

### D4: Module Separation (Client-Agnostic Core)

- `bridge.py`: Async generator that yields text chunks from CLI subprocess. No knowledge of Telegram.
- `session.py`: Manages state (idle/executing/error). No knowledge of Telegram.
- `auth.py`: Token/whitelist logic. No knowledge of Telegram.
- `telegram_adapter.py`: Consumes chunks from bridge, edits Telegram messages. Only module that imports `telegram`.

This separation means adding a web UI or Discord adapter later requires
only a new adapter module — zero changes to core.
