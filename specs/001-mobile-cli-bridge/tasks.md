# Tasks: Claude Mobile Bridge

**Input**: Design documents from `/specs/001-mobile-cli-bridge/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/telegram-bot-commands.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [x] T001 Create project structure: `src/__init__.py`, `src/__main__.py`, `tests/conftest.py` and directory layout per plan.md
- [x] T002 Create `requirements.txt` with `python-telegram-bot>=22.0,<23.0` and `pytest`, `pytest-asyncio` dev dependencies
- [x] T003 [P] Create `config.example.json` with all BridgeConfig fields and sensible defaults at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `BridgeConfig` dataclass and JSON loading/validation in `src/config.py` (fields: bot_token, pairing_secret, allowed_user_ids, max_prompt_length, edit_interval_ms, bind_address)
- [x] T005 Implement `Session` state machine in `src/session.py` (states: idle, executing, error; transitions per data-model.md state diagram)
- [x] T006 [P] Implement `PromptExecution` dataclass in `src/session.py` (fields: prompt_text, started_at, completed_at, exit_code, output_chars)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 2 - Authenticate with Token (Priority: P1)

**Goal**: Users authenticate via a pairing secret so unauthenticated access is rejected. Two-layer auth: one-time pairing secret + Telegram user ID whitelist.

**Independent Test**: Attempt to submit a prompt without pairing and verify rejection. Then `/pair <secret>` and verify access is granted.

### Implementation for User Story 2

- [x] T007 [US2] Implement pairing secret generation (cryptographic, 8+ chars) and user ID whitelist management in `src/auth.py`
- [x] T008 [US2] Implement whitelist persistence — save/load `allowed_user_ids` to config file in `src/auth.py`
- [x] T009 [US2] Implement `/start` command handler in `src/telegram_adapter.py` — welcome message explaining pairing flow
- [x] T010 [US2] Implement `/pair <secret>` command handler in `src/telegram_adapter.py` — validate secret, add user ID to whitelist, confirm pairing
- [x] T011 [US2] Implement authentication gate in `src/telegram_adapter.py` — reject all messages from users not in whitelist with "not authorized" reply

**Checkpoint**: Authentication flow is functional — unauthenticated users are blocked, pairing works

---

## Phase 4: User Story 1 - Send a Prompt from Mobile (Priority: P1) MVP

**Goal**: User sends a text message to the bot, it is forwarded to Claude CLI, and streamed output appears progressively on Telegram via message editing.

**Independent Test**: Start the bridge, pair from Telegram, send "Hello", verify streamed text appears within seconds.

### Implementation for User Story 1

- [x] T012 [US1] Implement async CLI subprocess spawning in `src/bridge.py` — run `claude -p --output-format stream-json --include-partial-messages --bare "<prompt>"` via `asyncio.create_subprocess_exec`
- [x] T013 [US1] Implement stream-json line parser in `src/bridge.py` — parse JSON events from CLI stdout, extract text content, yield as async generator
- [x] T014 [US1] Implement token buffer with edit-cadence logic in `src/bridge.py` — buffer tokens, flush every ~1s or 50+ chars
- [x] T015 [US1] Implement prompt size validation in `src/bridge.py` — reject prompts exceeding `max_prompt_length` from config
- [x] T016 [US1] Implement text message handler (non-command) in `src/telegram_adapter.py` — send "Thinking..." message, consume bridge async generator, edit message with buffered output
- [x] T017 [US1] Implement message overflow handling in `src/telegram_adapter.py` — when text exceeds 4000 chars, send new message and continue editing there
- [x] T018 [US1] Implement completion marker in `src/telegram_adapter.py` — append `---` on CLI completion, show error indicator on non-zero exit
- [x] T019 [US1] Implement "already executing" guard in `src/telegram_adapter.py` — if session is `executing`, reply with "A prompt is already running. Send /stop to cancel it."
- [x] T020 [US1] Implement CLI crash handling in `src/bridge.py` — detect non-zero exit codes and unexpected termination, propagate error to caller

**Checkpoint**: Core value proposition works — send prompt from Telegram, see streamed Claude output

---

## Phase 5: User Story 3 - View Connection Status (Priority: P2)

**Goal**: User can check bridge status and sees execution state feedback.

**Independent Test**: Send `/status` and verify it shows session state. Submit a prompt and verify "executing" indicator appears. 

### Implementation for User Story 3

- [x] T021 [US3] Implement `/status` command handler in `src/telegram_adapter.py` — reply with session state (idle/executing), bridge uptime, CLI availability
- [x] T022 [US3] Track bridge uptime in `src/telegram_adapter.py` or `src/session.py` — record start time, compute elapsed
- [x] T023 [US3] Check CLI availability in `/status` handler — verify `claude` binary is in PATH

**Checkpoint**: User can query bridge status at any time

---

## Phase 6: User Story 4 - Multiple Prompts in a Session (Priority: P2)

**Goal**: After a response completes, user submits another prompt without re-authenticating. Session persists across multiple cycles.

**Independent Test**: Send a prompt, wait for response, send a second prompt — both handled in same session without re-pairing.

### Implementation for User Story 4

- [x] T024 [US4] Implement session state reset on completion in `src/session.py` — transition executing->idle and error->idle to allow next prompt
- [x] T025 [US4] Implement `/stop` command handler in `src/telegram_adapter.py` — kill active CLI subprocess, reset session to idle, confirm cancellation
- [x] T026 [US4] Wire up entry point in `src/__main__.py` — load config, initialize auth, create Telegram application, register all handlers, start polling

**Checkpoint**: Full session lifecycle works — multiple prompts, stop, status, all in one session

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, hardening, and final validation

- [x] T027 [P] Handle `BadRequest("message is not modified")` silently in `src/telegram_adapter.py` when message edit content hasn't changed
- [x] T028 [P] Add graceful shutdown handling in `src/__main__.py` — clean up running CLI subprocesses on SIGINT/SIGTERM
- [x] T029 Print pairing secret to terminal on startup in `src/__main__.py` with clear instructions
- [x] T030 Run quickstart.md validation — verify all checklist items pass end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US2 Auth (Phase 3)**: Depends on Foundational — auth is needed before prompt flow
- **US1 Prompt (Phase 4)**: Depends on Foundational + US2 (auth gate must exist)
- **US3 Status (Phase 5)**: Depends on Foundational — can run in parallel with US1/US4
- **US4 Multi-Prompt (Phase 6)**: Depends on US1 (needs prompt flow to test session continuity)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US2 (Auth)**: Foundational only — no dependency on other stories
- **US1 (Prompt)**: Foundational + US2 — needs auth gate before accepting prompts
- **US3 (Status)**: Foundational only — independent of other stories
- **US4 (Multi-Prompt)**: US1 — needs prompt execution to test session persistence

### Within Each User Story

- Models/dataclasses before services
- Core logic (bridge.py) before adapter (telegram_adapter.py)
- Implementation before edge-case handling

### Parallel Opportunities

- T003 (config.example.json) can run in parallel with T001/T002
- T005 and T006 (session.py entities) can run in parallel with T004 (config.py)
- T021-T023 (US3 Status) can run in parallel with US1 tasks after Foundational
- T027 and T028 (Polish) can run in parallel

---

## Parallel Example: User Story 1

```bash
# After auth (US2) is complete, launch US1 tasks:
# T012 and T013 can be developed together (both in bridge.py but sequential: spawn then parse)
# T016 and T017 are sequential (handler then overflow)

# In parallel with US1, US3 can proceed:
Task: "Implement /status command handler in src/telegram_adapter.py" (T021)
Task: "Track bridge uptime" (T022)
Task: "Check CLI availability" (T023)
```

---

## Implementation Strategy

### MVP First (User Story 2 + User Story 1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (config + session state)
3. Complete Phase 3: US2 Auth (pairing + whitelist)
4. Complete Phase 4: US1 Prompt (CLI bridge + streaming)
5. **STOP and VALIDATE**: Send a prompt from Telegram, see streamed output
6. This is a usable product at this point

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US2 Auth -> Pairing works, unauthorized rejected
3. Add US1 Prompt -> Core product works (MVP!)
4. Add US3 Status -> User can check bridge state
5. Add US4 Multi-Prompt -> Full session lifecycle
6. Polish -> Hardened for daily use

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No test tasks generated (not explicitly requested in spec)
- Single external dependency: python-telegram-bot
- All modules except telegram_adapter.py are client-agnostic per constitution principle IV
- Commit after each task or logical group
