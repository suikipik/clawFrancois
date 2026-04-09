# Data Model: Claude Mobile Bridge

**Date**: 2026-04-09
**Feature**: 001-mobile-cli-bridge

## Entities

### BridgeConfig

Represents the bridge server configuration loaded at startup.

| Field              | Type     | Description                                    |
|--------------------|----------|------------------------------------------------|
| bot_token          | string   | Telegram Bot API token (from BotFather)        |
| pairing_secret     | string   | One-time secret for user pairing               |
| allowed_user_ids   | int[]    | Telegram user IDs allowed to interact           |
| max_prompt_length  | int      | Maximum characters per prompt (default: 10000) |
| edit_interval_ms   | int      | Minimum ms between message edits (default: 1000)|
| bind_address       | string   | Network interface to bind (default: 127.0.0.1) |

**Storage**: Local JSON or YAML config file (`~/.claude-bridge/config.json`).
Pairing secret is regenerated each startup unless user provides a fixed one.

### Session

Represents an active user session (in-memory only, no persistence).

| Field           | Type     | Description                                   |
|-----------------|----------|-----------------------------------------------|
| user_id         | int      | Telegram user ID                              |
| chat_id         | int      | Telegram chat ID                              |
| state           | enum     | idle, executing, error                        |
| current_process | Process  | Reference to active Claude CLI subprocess     |
| message_id      | int?     | ID of the current response message being edited|
| buffer          | string   | Accumulated output not yet sent to Telegram   |
| last_edit_time  | datetime | Timestamp of last message edit                |

**Lifecycle**: Created on first authenticated message, destroyed on
`/stop` command or bridge shutdown. One session per user.

### PromptExecution

Represents a single prompt-response cycle (transient, not persisted).

| Field        | Type     | Description                              |
|--------------|----------|------------------------------------------|
| prompt_text  | string   | The user's prompt                        |
| started_at   | datetime | When CLI subprocess was spawned          |
| completed_at | datetime?| When CLI subprocess exited               |
| exit_code    | int?     | CLI process exit code                    |
| output_chars | int      | Total characters streamed back           |

## State Transitions

```
Session.state:

  [new connection] → idle
  idle → executing  (user sends prompt)
  executing → idle  (CLI completes successfully)
  executing → error (CLI crashes or times out)
  error → idle      (user sends new prompt)
```

## Relationships

```
BridgeConfig (1) ──── manages ──── (*) Session
Session (1) ──── owns ──── (0..1) PromptExecution (active)
```
