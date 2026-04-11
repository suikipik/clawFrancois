# Implementation Plan: Voice Message Transcription

**Branch**: `002-whisper-voice-transcription` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-whisper-voice-transcription/spec.md`

## Summary

Add voice message support to the Claude Mobile Bridge. When a user sends a voice message in Telegram, the bridge downloads the audio, transcribes it using the locally-installed Whisper CLI, shows the transcribed text to the user, then forwards it to the Claude CLI as a prompt. This extends the existing text-based flow with a new input modality while keeping the architecture client-agnostic.

## Technical Context

**Language/Version**: Python 3.11+ (with `from __future__ import annotations` for 3.9 compat)
**Primary Dependencies**: python-telegram-bot 22.x (existing), openai-whisper CLI (new, external)
**Storage**: Temporary files only (OS temp directory, cleaned up after use)
**Testing**: pytest + pytest-asyncio (existing)
**Target Platform**: macOS, Linux
**Project Type**: CLI tool / Telegram bot
**Performance Goals**: Transcribe a 1-minute voice message within 30 seconds on CPU
**Constraints**: Local-only execution, no cloud services, minimal new dependencies
**Scale/Scope**: Single user, one voice message at a time (serialized via session state)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Local-First Execution | PASS | Whisper runs entirely on the local machine. No audio data leaves the host. |
| II. Security by Default | PASS | Voice messages go through the same auth flow as text. Downloaded audio is temp-only and deleted after use. |
| III. Streaming-First Output | PASS | CLI output still streams after transcription. Transcription itself is batch (inherent to speech-to-text) but a progress indicator is shown. |
| IV. Client-Agnostic Architecture | PASS | Transcription logic lives in a separate `src/transcriber.py` module, not in the Telegram adapter. Future clients can reuse it. |
| V. Simplicity and Reuse | PASS | Uses existing Whisper CLI rather than wrapping the library. One new module, two extended modules. No new infrastructure. |

**Post-Phase 1 re-check**: All principles still hold. The design adds one new module (`transcriber.py`), extends two existing modules (`telegram_adapter.py`, `config.py`), and introduces no new architectural patterns.

## Project Structure

### Documentation (this feature)

```text
specs/002-whisper-voice-transcription/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── transcriber.md   # Transcriber module contract
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py          # (existing)
├── __main__.py          # (existing) — no changes needed
├── config.py            # (extend) — add whisper_model, max_audio_duration fields
├── session.py           # (existing) — no changes needed
├── auth.py              # (existing) — no changes needed
├── bridge.py            # (existing) — no changes needed
├── telegram_adapter.py  # (extend) — add voice/audio message handler
└── transcriber.py       # (NEW) — Whisper CLI wrapper, transcribe_audio(), check_whisper_available()

tests/
├── conftest.py          # (existing) — extend with transcriber fixtures
├── test_transcriber.py  # (NEW) — unit tests for transcriber module
└── test_voice_handler.py # (NEW) — integration tests for voice message flow
```

**Structure Decision**: Single project layout (existing). One new file (`src/transcriber.py`), two new test files. No structural changes to the repository.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
