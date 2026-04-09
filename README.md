# Claude Mobile Bridge — Project Specification

## Project Overview

`Claude Mobile Bridge` is a local utility that allows a user to interact with a Claude CLI workflow from a mobile device. The project provides a secure interface that sends prompts from the mobile client to the local machine, where they are executed by the Claude CLI. The CLI output is streamed back to the mobile client in near real time, preserving a live command-line experience on the go.

The mobile client could take several forms — a browser-based interface accessed over the local network, a Telegram bot relaying messages to the local machine, a dedicated mobile app, or any other channel that fits the user's workflow. The choice of client channel is deliberately left open at this stage.

## Core Idea

The core goal is to make the local Claude CLI feel accessible from a phone without compromising the local environment or requiring a remote hosted service.

Key principles:
- Keep the CLI execution local to the machine.
- Secure mobile access with a strong locally generated token.
- Stream output back to the mobile client so users can follow the command execution live.
- Maintain a simple mobile UX that feels like a chat interface.
- Reuse existing free and secure services whenever possible — avoid building what already exists. For v0.1, speed of delivery matters more than custom infrastructure.

## Primary Use Case

1. The user launches the local bridge service on their machine.
2. The service generates or requires a secret token for authentication.
3. The user connects from their mobile device through one of the supported channels (see examples below).
4. The mobile client accepts a prompt from the user.
5. The prompt is forwarded to the local Claude CLI process.
6. CLI output is streamed back to the mobile client, with updates arriving continuously.
7. The mobile user can watch the response build up as if they were on the local terminal.

### Possible Client Channels

The bridge is designed to be client-agnostic. The priority for v0.1 is to pick the channel that gets to a working demo fastest by leveraging existing free services — not to build custom infrastructure. Here are some examples:

- **Telegram bot** — Telegram's Bot API is free, handles authentication via user IDs, supports message editing for pseudo-streaming, and requires zero mobile-side development. The user simply opens an existing app they likely already have. This is a strong candidate for v0.1.
- **Local web interface** — The user opens a mobile browser and navigates to the machine's local IP address (e.g. `http://192.168.1.42:3000?token=xxx`). A lightweight chat-like UI handles prompt input and streamed output. Simple but requires building the frontend and handling network discovery.
- **Discord bot** — Similar to Telegram: free API, existing mobile app, built-in auth. Could be preferred if the user already lives in Discord.
- **Dedicated mobile app** — A native or cross-platform app connects to the bridge over WebSocket or HTTP, providing a richer UX with features like history, syntax highlighting, or notifications. Higher effort — better suited for a later version.
- **SMS / messaging gateway** — For minimal setups, prompts could be sent via SMS through a gateway service, with responses returned the same way. Services like Twilio offer free tiers.

The choice of channel does not affect the core bridge logic — it only changes how prompts arrive and how output is delivered back. For v0.1, the guiding question is: *which channel lets us ship a working bridge with the least custom code?*

## Requirements

### Functional Requirements

- A mobile-friendly web interface for sending prompts.
- A local endpoint that receives prompts securely.
- A bridge that forwards prompts to the Claude CLI.
- Streaming output from Claude CLI back to the mobile UI.
- A visible status indication for connection state and execution progress.
- The ability to send multiple prompts during a session.

### Non-functional Requirements

- Local-first: no remote execution of prompts.
- Minimal dependencies: simple and maintainable local tooling.
- Leverage existing free services and APIs (Telegram Bot API, Discord API, etc.) rather than building custom clients or infrastructure from scratch.
- Secure access via a token or secret.
- Clear user feedback for success, streaming progress, and errors.

## Security Model

The service should not expose the Claude CLI to the wider internet by default. Access is restricted by a local token and optionally limited to the local network. The following elements are important:

- A per-session or fixed secret token for client authentication.
- No anonymous prompt submission.
- Mobile access limited to the same network or tunnelled connection under user control.
- Clear guidance to keep the token private.

## User Experience (UX)

Regardless of the client channel, the mobile user should experience the following flow:

- Connect to the bridge (open a URL, start a Telegram conversation, launch an app, etc.).
- Authenticate (token, user ID whitelist, or another mechanism appropriate to the channel).
- Compose and submit a prompt.
- See CLI responses stream back progressively.
- Optionally clear output and send another prompt.

Live streaming should feel like watching a local terminal session, with text appended as it is emitted by Claude. The exact rendering will depend on the chosen channel — a browser can scroll a live text area, a Telegram bot might edit its last message or send chunked replies, and a native app could use a terminal-style view.

## Architecture Outline

This project is expected to include several logical components:

- **Server**: Accepts mobile requests, validates token, and launches Claude CLI processes.
- **Client**: Mobile-facing interface — could be a browser UI, a Telegram bot, a native app, or any other channel that can send prompts and display streamed output.
- **CLI Bridge**: Handles execution of the Claude CLI and streaming of stdout/stderr back to the client.
- **Authentication**: Token handling to restrict access.

## Integration Points

- **Claude CLI invocation**: The prompt from mobile is transformed into a command-line invocation of `claude code` or a similar Claude CLI entrypoint.
- **Streaming transport**: The output channel should push CLI stdout as it arrives, rather than waiting for the command to finish.

## Success Criteria

The project should be considered successful when:

- A mobile device can securely send a prompt to the local machine.
- The local Claude CLI runs the prompt.
- Output is streamed back and visible on the phone in real time.
- The solution preserves the local CLI experience while offering a mobile chat-like interface.

## Open Questions

- Which exact Claude CLI flags and input mode are required for best streaming behavior?
- Should the mobile interface support command history or past sessions?
- How should the bridge handle long-running CLI calls and partial outputs?
- What level of network access should be supported by default (local network only vs. optional tunneling)?
- Which client channel(s) should be implemented first? A local web UI is the simplest starting point, but a Telegram bot may better fit some users' daily workflow.
- Should the bridge support multiple client channels simultaneously (e.g. web + Telegram)?
- For bot-based channels, how should streaming be handled given platform-specific message limits and rate constraints?

## Next Step

Translate this specification into a minimal implementation with a local server, secure token authentication, a mobile web frontend, and streamed CLI output.
