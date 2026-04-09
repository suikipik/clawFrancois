# Research: Claude Mobile Bridge

**Date**: 2026-04-09
**Feature**: 001-mobile-cli-bridge

## R1: Claude CLI Invocation & Streaming

**Decision**: Use `claude -p --output-format stream-json --include-partial-messages --bare` for subprocess invocation.

**Rationale**:
- `-p` / `--print`: Non-interactive single-prompt mode, prints and exits.
- `--output-format stream-json`: Emits one JSON event per line as tokens arrive (real-time streaming).
- `--include-partial-messages`: Required alongside `stream-json` to get partial chunks.
- `--bare`: Skips hooks, plugins, LSP, and CLAUDE.md discovery — clean subprocess invocation with no interactive overhead.

**Alternatives considered**:
- `--output-format text`: Plain text, but output is buffered as a single result — no streaming.
- `--output-format json`: Structured but waits for completion — no streaming.
- Piping stdin with `--input-format stream-json`: Overkill for single prompt; better for multi-turn later.

**Other useful flags**:
- `--max-budget-usd <amount>`: Cap API spend per prompt.
- `--no-session-persistence`: Disable session saving for ephemeral bridge calls.
- `-c` / `--continue`: Resume last conversation (future multi-turn support).
- `--tools ""`: Disable all tools if needed for restricted mode.

## R2: Telegram Bot as Client Channel

**Decision**: Use Telegram Bot API via `python-telegram-bot` v22.x with message editing for pseudo-streaming.

**Rationale**:
- Telegram Bot API is free, handles mobile app distribution (user opens Telegram), zero mobile-side development.
- `python-telegram-bot` v22.7 is fully async (Python 3.10+), mature, well-documented.
- User ID whitelist via `filters.User(user_id=[...])` provides simple auth layered on top of the bridge token.
- Message editing (`editMessageText`) creates a pseudo-streaming experience.

**Streaming approach**:
- Buffer incoming tokens from Claude CLI.
- Edit the Telegram message every ~1 second or when buffer grows by 50+ characters.
- Rate limit: ~1 edit/sec/chat to avoid Telegram flood errors.
- Max message length: 4096 UTF-8 characters. If exceeded, send a new message and continue appending there.
- Catch `BadRequest("message is not modified")` silently when content hasn't changed.

**Alternatives considered**:
- `sendMessageDraft` (Bot API 9.5+): Native streaming support, but very new and not yet wrapped by python-telegram-bot. Worth revisiting in v0.2.
- Local web UI: Requires building a frontend; Telegram is zero-frontend.
- Discord bot: Similar approach but user already prefers Telegram.

## R3: Authentication Model

**Decision**: Two-layer auth — Telegram user ID whitelist + bridge startup token for initial pairing.

**Rationale**:
- Telegram user IDs are stable and unique — ideal for a whitelist.
- Bridge generates a one-time pairing token at startup; user sends it to the bot to register their Telegram user ID.
- After pairing, the user ID whitelist gates all subsequent requests — no token needed per message.
- This avoids the UX friction of including a token in every Telegram message.

**Alternatives considered**:
- Token-per-message: Clunky UX in a chat interface.
- No auth beyond Telegram: Insecure — anyone who finds the bot could use it.
- Password-based: Unnecessary complexity.

## R4: Language & Framework

**Decision**: Python 3.11+ with `python-telegram-bot` and `asyncio`.

**Rationale**:
- Python is the fastest path to a working prototype given the ecosystem (telegram library, subprocess, async).
- `asyncio` subprocess support (`asyncio.create_subprocess_exec`) enables non-blocking streaming from Claude CLI.
- Minimal dependencies: `python-telegram-bot` is the only external package needed.

**Alternatives considered**:
- Node.js with `telegraf`: Viable but Python subprocess handling is more straightforward.
- Go: Faster runtime but slower development for a v0.1 prototype.
- Rust: Same tradeoff — overkill for v0.1.
