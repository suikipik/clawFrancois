# Contract: Transcriber Module

## Module: `src/transcriber.py`

### `transcribe_audio(audio_path: Path) -> TranscriptionResult`

Transcribe an audio file to text using the locally-installed Whisper CLI.

**Input**:
- `audio_path`: Absolute path to the audio file (OGG, WAV, MP3, or any ffmpeg-supported format)

**Output**: `TranscriptionResult` dataclass with fields:
- `text` (str): Transcribed text, stripped of leading/trailing whitespace
- `language` (str | None): Detected language code if available
- `duration_secs` (float): Audio duration in seconds
- `success` (bool): True if transcription produced non-empty text
- `error_message` (str | None): Error description if failed

**Behavior**:
- Runs `whisper <audio_path> --output_format txt --model <model>` as a subprocess
- Reads the `.txt` output file produced by Whisper
- Returns `success=False` with `error_message` if:
  - `whisper` command not found (not installed)
  - Process exits with non-zero code
  - Output file is empty or missing
  - Process times out (configurable, default 120 seconds)
- Cleans up Whisper output files (`.txt`, `.vtt`, `.srt`, `.json`) after reading

### `check_whisper_available() -> bool`

Check whether the Whisper CLI is installed and accessible.

**Output**: `True` if `whisper` is found in PATH, `False` otherwise.

Used by `/status` command to report voice transcription capability.

## Module: `src/telegram_adapter.py` (extended)

### Voice message handler

The existing `MessageHandler` registration is extended to also handle `filters.VOICE` and `filters.AUDIO`.

**Flow**:
1. Check authorization (same as text messages)
2. Check session state (same as text messages)  
3. Validate audio duration against `max_audio_duration`
4. Send "Transcribing..." status message
5. Download audio file to temp directory
6. Call `transcribe_audio()`
7. If successful: display transcribed text, then forward to `run_prompt()`
8. If failed: display error message, reset session
9. Clean up temp audio file in `finally` block

## Module: `src/config.py` (extended)

### New fields in `BridgeConfig`

- `whisper_model: str = "base"` — Whisper model size
- `max_audio_duration: int = 300` — Max audio duration in seconds
