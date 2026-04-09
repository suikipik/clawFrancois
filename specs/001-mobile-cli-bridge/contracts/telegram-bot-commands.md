# Contract: Telegram Bot Commands

**Date**: 2026-04-09
**Feature**: 001-mobile-cli-bridge

## Bot Commands

These are the Telegram bot commands registered with BotFather and
handled by the bridge.

### /start

**Trigger**: User opens the bot for the first time or sends `/start`.
**Behavior**: Displays a welcome message explaining how to pair with
the bridge. Prompts the user to send the pairing secret.
**Auth required**: No (this is the entry point).

### /pair `<secret>`

**Trigger**: User sends `/pair abc123` with the bridge pairing secret.
**Behavior**:
- If secret matches: adds the user's Telegram ID to the allowed list,
  confirms pairing, session enters `idle` state.
- If secret is invalid: rejects with "Invalid pairing secret" message.
**Auth required**: No (this is the pairing step).

### /stop

**Trigger**: Authenticated user sends `/stop`.
**Behavior**: If a CLI process is running, terminates it. Sends
confirmation that execution was stopped. Session returns to `idle`.
**Auth required**: Yes.

### /status

**Trigger**: Authenticated user sends `/status`.
**Behavior**: Replies with current session state (idle, executing),
bridge uptime, and whether CLI is available.
**Auth required**: Yes.

## Message Handling (non-command)

### Text Message (prompt)

**Trigger**: Authenticated user sends any non-command text message.
**Behavior**:
1. If session is `idle`: treat message as a prompt.
   - Send an initial "Thinking..." message.
   - Spawn Claude CLI subprocess with the prompt.
   - Stream output by editing the "Thinking..." message at ~1s intervals.
   - If output exceeds 4096 chars, send a new message and continue.
   - On completion, append a "Done" indicator.
2. If session is `executing`: reply with "A prompt is already running.
   Send /stop to cancel it."
**Auth required**: Yes.

### Unauthenticated Message

**Trigger**: Any message from a user not in the allowed list.
**Behavior**: Reply with "You are not authorized. Send /pair <secret>
to connect."

## Message Edit Protocol

When streaming CLI output to Telegram:

1. **Initial message**: Send "Thinking..." immediately after prompt receipt.
2. **Edit cadence**: Every 1 second, if buffer has new content.
3. **Chunk threshold**: Also edit if buffer has grown by 50+ characters,
   even if 1 second hasn't elapsed.
4. **Max length**: If accumulated text exceeds 4000 characters (with
   margin below 4096 limit), send a new message and continue there.
5. **Completion**: Final edit appends a completion marker (e.g., `---`).
6. **Error**: If CLI exits non-zero, append error indicator to message.
