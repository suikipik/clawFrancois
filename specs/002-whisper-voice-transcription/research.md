# Phase 0 Research: Voice Message Transcription

## R1: Audio Format Handling

**Decision**: Accept Telegram's native voice message format (OGG/Opus) and convert to WAV for Whisper compatibility using ffmpeg.

**Rationale**: Telegram voice messages are always OGG/Opus encoded. Whisper accepts WAV, MP3, M4A, FLAC, and other formats natively via ffmpeg. Since Whisper already depends on ffmpeg internally, requiring ffmpeg on the host is not an additional burden. Converting OGG to WAV before transcription is the most reliable path.

**Alternatives considered**:
- Pass OGG directly to Whisper — works in many cases since Whisper uses ffmpeg internally, but explicit conversion is more predictable and debuggable.
- Convert to MP3 — unnecessary lossy re-encode, no benefit over WAV.

## R2: Whisper Integration Approach

**Decision**: Use the Whisper CLI (`whisper` command) rather than importing the Python library directly.

**Rationale**: 
- Keeps the bridge decoupled from Whisper's Python dependencies (torch, numpy, etc.) which are heavy and version-sensitive.
- Aligns with Constitution Principle IV (Client-Agnostic Architecture) — the transcription engine is a pluggable external tool, not a linked library.
- Aligns with Constitution Principle V (Simplicity and Reuse) — use the existing CLI tool rather than wrapping the library.
- Users may have Whisper installed via pip, brew, or compiled from source — the CLI is the common interface.
- Allows future substitution with other speech-to-text CLIs (e.g., whisper.cpp, faster-whisper) without changing bridge code.

**Alternatives considered**:
- Import `whisper` Python package directly — tighter coupling, heavier dependency footprint, harder to swap engines.
- Use a cloud speech-to-text service — violates Constitution Principle I (Local-First Execution).

## R3: Telegram Audio File Download

**Decision**: Use `python-telegram-bot`'s built-in `Voice.get_file()` and `File.download_to_drive()` to download voice messages to a temporary directory.

**Rationale**: The library already provides async file download. Temp files are created in a dedicated directory and cleaned up immediately after transcription. No persistent storage needed.

**Alternatives considered**:
- Manual HTTP download via Telegram Bot API — unnecessary when the library handles it.
- In-memory processing — Whisper CLI requires a file path, so a temp file is necessary.

## R4: Architecture — Where Does Transcription Live?

**Decision**: Create a new `src/transcriber.py` module that handles audio-to-text conversion. The TelegramAdapter calls the transcriber, then feeds the result into the existing prompt pipeline.

**Rationale**: 
- Constitution Principle IV requires that the bridge core be client-agnostic. Transcription is a bridge-level service, not a Telegram-specific one.
- A separate module allows unit testing of transcription independently of Telegram.
- Future clients (Discord, web UI) could also use the same transcriber if they support voice.

**Alternatives considered**:
- Embed transcription logic directly in `telegram_adapter.py` — violates Principle IV, harder to test.
- Add to `bridge.py` — bridge.py is specifically about CLI process management, not pre-processing.

## R5: Maximum Audio Duration

**Decision**: Default to 5 minutes (300 seconds). Configurable via `BridgeConfig`.

**Rationale**: Whisper processes audio in real-time or faster on most machines. A 5-minute clip transcribes in under 2 minutes on CPU, well within acceptable wait time. Telegram's own voice message limit is much higher, so the bridge should set its own boundary.

**Alternatives considered**:
- No limit — risk of extremely long transcription times blocking the session.
- 1 minute limit — too restrictive for natural voice messages.

## R6: Whisper Model Selection

**Decision**: Default to the "base" model. Configurable via `BridgeConfig` with a `whisper_model` field.

**Rationale**: The "base" model balances accuracy and speed for most use cases. Users with GPUs or who need higher accuracy can configure "small", "medium", or "large". Users on constrained hardware can use "tiny".

**Alternatives considered**:
- Default to "tiny" — faster but noticeably less accurate for non-English speech.
- Default to "small" — better accuracy but slower on CPU, poor default for low-end machines.
