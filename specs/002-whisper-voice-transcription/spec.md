# Feature Specification: Voice Message Transcription

**Feature Branch**: `002-whisper-voice-transcription`
**Created**: 2026-04-11
**Status**: Draft
**Input**: User description: "add a feature to detect audio message and use the local whisper to transcript them into prompt sent to the agent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send a Voice Message as a Prompt (Priority: P1)

A user records a voice message in Telegram and sends it to the bot. The bridge detects that the incoming message is an audio/voice message rather than text. It downloads the audio file, runs it through a local speech-to-text engine, and extracts the transcribed text. The transcription is then forwarded to the Claude CLI as a prompt, exactly as if the user had typed it. The streamed response appears in the Telegram chat as usual.

**Why this priority**: This is the core feature. Without voice-to-text-to-prompt, there is no value delivered. It unlocks hands-free interaction with Claude from mobile.

**Independent Test**: Send a voice message saying "What is the capital of France?" to the bot and verify that Claude responds with an answer about Paris.

**Acceptance Scenarios**:

1. **Given** the bridge is running and the user is authenticated,
   **When** the user sends a voice message in Telegram,
   **Then** the bridge downloads the audio, transcribes it, and forwards the transcription as a prompt to the CLI within 30 seconds for a message under 1 minute long.
2. **Given** the bridge receives a voice message,
   **When** the transcription completes successfully,
   **Then** the bot displays the transcribed text to the user before forwarding it to the CLI, so the user can verify what was understood.
3. **Given** the bridge receives a voice message,
   **When** the transcription completes and is forwarded,
   **Then** the CLI response streams back to the Telegram chat identically to how text prompts work today.

---

### User Story 2 - Transcription Feedback and Confirmation (Priority: P2)

After transcribing the voice message, the bot shows the user the transcribed text before sending it to Claude. This gives the user visibility into what was understood and builds trust in the voice workflow. The transcription is sent automatically (no manual confirmation step) to keep the interaction fast.

**Why this priority**: Without feedback, the user cannot tell if the transcription was accurate. Showing the transcribed text makes the feature trustworthy and debuggable without slowing down the interaction.

**Independent Test**: Send a voice message and verify that the bot replies with the transcribed text (e.g., prefixed with a label like "Voice:") before the Claude response starts streaming.

**Acceptance Scenarios**:

1. **Given** the bridge transcribes a voice message,
   **When** the transcription is ready,
   **Then** the bot sends a message showing the transcribed text before forwarding to the CLI.
2. **Given** the transcription preview is displayed,
   **When** the CLI begins responding,
   **Then** the streamed response appears as a separate message, clearly distinguishable from the transcription preview.

---

### User Story 3 - Graceful Handling of Transcription Failures (Priority: P2)

If the speech-to-text engine is unavailable, the audio file is corrupted, or the transcription produces empty output, the user receives a clear error message explaining what went wrong. No silent failures occur, and the user is guided on how to retry.

**Why this priority**: Voice recognition is inherently unreliable. Users need clear feedback when it fails so they can retry or fall back to typing.

**Independent Test**: Send an audio file with pure silence or white noise and verify the bot responds with a meaningful error rather than forwarding an empty prompt.

**Acceptance Scenarios**:

1. **Given** the speech-to-text engine is not installed or not accessible,
   **When** the user sends a voice message,
   **Then** the bot replies with an error message indicating that voice transcription is unavailable.
2. **Given** the bridge receives a voice message,
   **When** the transcription produces empty or unintelligible output,
   **Then** the bot informs the user that the voice message could not be understood and suggests retrying or typing instead.
3. **Given** the audio file download fails,
   **When** the bot cannot retrieve the voice message from Telegram,
   **Then** the bot informs the user of the download failure.

---

### Edge Cases

- What happens when the user sends a very long voice message (over 5 minutes)? The system MUST enforce a maximum audio duration and inform the user if their message exceeds it.
- What happens when the user sends a non-voice audio file (e.g., a music file or document)? The system MUST either attempt transcription or reject it with a clear message explaining that only voice messages are supported.
- What happens when the user sends a voice message while a previous prompt is still executing? The existing queuing/rejection behavior from the bridge (FR-011 of feature 001) MUST apply — the transcribed text is treated as any other prompt.
- What happens when the speech-to-text engine is slow and takes longer than expected? The bot MUST show a processing indicator so the user knows the system is working.
- What happens when the audio language does not match the expected language? The system MUST transcribe whatever it detects and forward it — language detection and restriction are out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST detect when an incoming Telegram message is a voice message or audio file rather than text.
- **FR-002**: The system MUST download the audio file from Telegram to local storage for processing.
- **FR-003**: The system MUST transcribe the downloaded audio to text using a locally-installed speech-to-text engine.
- **FR-004**: The system MUST display the transcribed text to the user in the Telegram chat before forwarding it to the CLI.
- **FR-005**: The system MUST forward the transcribed text to the Claude CLI as a prompt, using the same execution path as typed text messages.
- **FR-006**: The system MUST delete the downloaded audio file from local storage after transcription completes (or fails).
- **FR-007**: The system MUST inform the user with a clear error message if the speech-to-text engine is unavailable.
- **FR-008**: The system MUST inform the user if the transcription produces empty or unintelligible output.
- **FR-009**: The system MUST enforce a maximum audio duration and reject voice messages that exceed it with a descriptive error.
- **FR-010**: The system MUST show a processing indicator while transcription is in progress.
- **FR-011**: The system MUST handle voice messages through the same authentication and session management as text messages (no separate auth flow).

### Key Entities

- **Voice Message**: An audio recording sent by the user through Telegram, containing spoken content intended as a prompt.
- **Transcription**: The text output produced by the speech-to-text engine from a voice message. Becomes the prompt forwarded to the CLI.
- **Audio File**: The temporary local file downloaded from Telegram for processing. Deleted after transcription.
- **Speech-to-Text Engine**: A locally-installed tool that converts audio to text. Must be present on the host machine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A voice message under 1 minute long is transcribed and the first CLI output appears within 30 seconds of sending the voice message.
- **SC-002**: Transcription accuracy for clear speech in a quiet environment is sufficient for Claude to understand and respond meaningfully to 90% of voice prompts.
- **SC-003**: 100% of transcription failures (engine unavailable, empty result, download error) produce a user-visible error message — no silent failures.
- **SC-004**: Audio files are cleaned up from local storage within 60 seconds of transcription completing.
- **SC-005**: Users who already know how to use the text bridge can successfully send their first voice prompt without any additional instructions.

## Assumptions

- The user has a speech-to-text engine (such as Whisper) already installed and accessible on the host machine where the bridge runs. The bridge does not install or manage the engine.
- Voice messages are in formats supported by Telegram's voice message feature (OGG/Opus). The speech-to-text engine is expected to handle this format, possibly with a conversion step.
- The maximum voice message duration is set to 5 minutes as a reasonable default. Longer messages can be split by the user.
- The transcription runs locally on the host machine — no cloud speech-to-text services are used. This keeps the feature privacy-friendly and free of external dependencies.
- Language detection and multi-language support depend on the capabilities of the locally-installed engine. The bridge does not impose language restrictions.
- This feature extends the existing Telegram adapter from feature 001 — it is not a standalone service.
