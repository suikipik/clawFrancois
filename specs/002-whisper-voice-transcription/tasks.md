# Tasks: Voice Message Transcription

**Input**: Design documents from `/specs/002-whisper-voice-transcription/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Add new dependencies and configuration support

- [x] T001 Add whisper_model and max_audio_duration fields to BridgeConfig in src/config.py
- [x] T002 Update config.example.json with new whisper_model and max_audio_duration fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core transcription module that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create TranscriptionResult dataclass in src/transcriber.py with fields: text, language, duration_secs, success, error_message
- [x] T004 Implement check_whisper_available() function in src/transcriber.py that checks if whisper CLI is in PATH
- [x] T005 Implement transcribe_audio() function in src/transcriber.py that runs whisper CLI as subprocess, reads output .txt file, and returns TranscriptionResult
- [x] T006 Add temp file cleanup logic in transcribe_audio() — delete downloaded audio and whisper output files (.txt, .vtt, .srt, .json) in a finally block

**Checkpoint**: Foundation ready — transcriber module works standalone, user story implementation can begin

---

## Phase 3: User Story 1 — Send a Voice Message as a Prompt (Priority: P1) 🎯 MVP

**Goal**: User sends a voice message in Telegram, it gets transcribed and forwarded to Claude CLI as a prompt, response streams back normally.

**Independent Test**: Send a voice message saying "What is the capital of France?" and verify Claude responds about Paris.

### Implementation for User Story 1

- [ ] T007 [US1] Add voice/audio message handler method handle_voice() in src/telegram_adapter.py that downloads audio, calls transcriber, and forwards text to run_prompt()
- [ ] T008 [US1] Implement audio file download using Voice.get_file() and File.download_to_drive() to a temp directory in handle_voice() in src/telegram_adapter.py
- [ ] T009 [US1] Add audio duration validation in handle_voice() — reject messages exceeding max_audio_duration with a descriptive error in src/telegram_adapter.py
- [ ] T010 [US1] Wire transcribed text into the existing prompt execution flow (session.start_execution + run_prompt + streaming) in handle_voice() in src/telegram_adapter.py
- [ ] T011 [US1] Register voice handler with filters.VOICE and filters.AUDIO in register_handlers() in src/telegram_adapter.py
- [ ] T012 [US1] Add temp file cleanup in handle_voice() finally block — delete downloaded audio regardless of success/failure in src/telegram_adapter.py

**Checkpoint**: At this point, voice messages are transcribed and produce Claude responses. MVP complete.

---

## Phase 4: User Story 2 — Transcription Feedback and Confirmation (Priority: P2)

**Goal**: Bot shows transcribed text to the user before forwarding to Claude, so the user can see what was understood.

**Independent Test**: Send a voice message and verify the bot replies with the transcribed text (prefixed with "Voice:") before the Claude response starts streaming.

### Implementation for User Story 2

- [ ] T013 [US2] Send transcription preview message (prefixed "Voice: ") to the user before forwarding to run_prompt() in handle_voice() in src/telegram_adapter.py
- [ ] T014 [US2] Send "Transcribing..." processing indicator immediately when voice message is received in handle_voice() in src/telegram_adapter.py
- [ ] T015 [US2] Update "Transcribing..." message to show transcribed text once ready, then start streaming Claude response as a new message in src/telegram_adapter.py

**Checkpoint**: User sees what was transcribed before Claude responds. Stories 1 and 2 both work.

---

## Phase 5: User Story 3 — Graceful Handling of Transcription Failures (Priority: P2)

**Goal**: Clear error messages for all failure modes — whisper not installed, empty transcription, download failure.

**Independent Test**: Send silence/noise as a voice message and verify a meaningful error is shown. Stop whisper and send a voice message to verify "unavailable" error.

### Implementation for User Story 3

- [ ] T016 [US3] Add whisper availability check to /status command output using check_whisper_available() in handle_status() in src/telegram_adapter.py
- [ ] T017 [US3] Handle transcription failure (success=False) in handle_voice() — display error_message to user and reset session in src/telegram_adapter.py
- [ ] T018 [US3] Handle empty transcription (success=True but text is empty/whitespace) — inform user audio could not be understood in src/telegram_adapter.py
- [ ] T019 [US3] Handle audio download failure — catch exceptions from get_file()/download_to_drive() and inform user in src/telegram_adapter.py
- [ ] T020 [US3] Handle whisper CLI timeout (configurable, default 120s) in transcribe_audio() — return TranscriptionResult with timeout error in src/transcriber.py

**Checkpoint**: All failure modes produce user-visible errors. No silent failures.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation across all stories

- [ ] T021 [P] Update quickstart.md with final installation and usage instructions in specs/002-whisper-voice-transcription/quickstart.md
- [ ] T022 [P] Add whisper dependency note to project README or docs
- [ ] T023 Run quickstart.md validation — follow the quickstart from scratch and verify all steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (config fields) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 3 (T010 specifically — needs working voice→prompt flow)
- **User Story 3 (Phase 5)**: Depends on Phase 2 completion — can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational only — core MVP
- **User Story 2 (P2)**: Depends on US1 — adds feedback to existing voice flow
- **User Story 3 (P2)**: Depends on Foundational only — can be implemented in parallel with US1

### Within Each User Story

- Models/dataclasses before service logic
- Service logic before handler wiring
- Handler wiring before registration

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T003, T004 can run in parallel within Phase 2 (independent functions)
- US1 and US3 can be worked on in parallel after Phase 2
- T021 and T022 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# After Phase 2 completes, within US1:
# T007-T010 are sequential (building up handle_voice incrementally)
# T011 depends on T007 (handler must exist to register)
# T012 depends on T007 (cleanup wraps the handler logic)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T006)
3. Complete Phase 3: User Story 1 (T007–T012)
4. **STOP and VALIDATE**: Send a voice message, verify transcription + Claude response
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Transcriber module works standalone
2. Add User Story 1 → Voice messages produce Claude responses (MVP!)
3. Add User Story 2 → User sees transcription before response
4. Add User Story 3 → All error cases handled gracefully
5. Polish → Documentation updated and validated

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The transcriber module (Phase 2) is the only new file — all US tasks extend existing files
