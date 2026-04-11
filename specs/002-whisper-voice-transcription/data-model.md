# Data Model: Voice Message Transcription

## Entities

### TranscriptionResult

Represents the outcome of a voice-to-text conversion.

| Field         | Type           | Description                                      |
|---------------|----------------|--------------------------------------------------|
| text          | string         | The transcribed text output                      |
| language      | string or null | Detected language code (e.g., "en", "fr"), if available |
| duration_secs | float          | Duration of the source audio in seconds          |
| success       | boolean        | Whether transcription succeeded                  |
| error_message | string or null | Error description if transcription failed        |

### BridgeConfig (extended)

New fields added to the existing configuration entity.

| Field              | Type   | Default | Description                                           |
|--------------------|--------|---------|-------------------------------------------------------|
| whisper_model      | string | "base"  | Whisper model size (tiny, base, small, medium, large) |
| max_audio_duration | int    | 300     | Maximum voice message duration in seconds             |

## State Transitions

Voice message processing fits into the existing Session state machine:

```
IDLE → (voice message received) → EXECUTING → (transcription) → EXECUTING → (CLI response) → IDLE
                                                    ↓ (failure)
                                                  ERROR → IDLE (on reset)
```

The session enters EXECUTING state when the voice message is received (not after transcription). This prevents concurrent messages during the transcription phase.

## Temporary Data

| Data            | Location           | Lifecycle                                  |
|-----------------|--------------------|--------------------------------------------|
| Audio file      | OS temp directory  | Created on download, deleted after transcription |
| Converted file  | OS temp directory  | Created during format conversion, deleted after transcription |

No persistent data is introduced by this feature. All temporary files are cleaned up in a `finally` block regardless of success or failure.
