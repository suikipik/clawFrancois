# Claude Mobile Bridge — Project Specification

## Project Overview

`Claude Mobile Bridge` is a local utility that allows a user to interact with a Claude CLI workflow from a mobile device. The project provides a secure, local mobile-friendly interface that sends prompts from the mobile browser to the local machine, where they are executed by the Claude CLI. The CLI output is streamed back to the mobile client in near real time, preserving a live command-line experience through the phone.

## Core Idea

The core goal is to make the local Claude CLI feel accessible from a phone without compromising the local environment or requiring a remote hosted service.

Key principles:
- Keep the CLI execution local to the machine.
- Secure mobile access with a strong locally generated token.
- Stream output back to the mobile client so users can follow the command execution live.
- Maintain a simple mobile UX that feels like a chat interface.
- Avoid major architectural decisions in this specification; instead, focus on the behavior and expected interactions.

## Primary Use Case

1. The user launches the local bridge service on their machine.
2. The service generates or requires a secret token for authentication.
3. The user opens the mobile interface in a phone browser using the machine's local IP address plus the token.
4. The mobile interface accepts a prompt from the user.
5. The prompt is forwarded to the local Claude CLI process.
6. CLI output is streamed back to the mobile client, with updates arriving continuously.
7. The mobile user can watch the response build up as if they were on the local terminal.

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
- Secure access via a token or secret.
- Clear user feedback for success, streaming progress, and errors.

## Security Model

The service should not expose the Claude CLI to the wider internet by default. Access is restricted by a local token and optionally limited to the local network. The following elements are important:

- A per-session or fixed secret token for client authentication.
- No anonymous prompt submission.
- Mobile access limited to the same network or tunnelled connection under user control.
- Clear guidance to keep the token private.

## User Experience (UX)

The mobile user should experience the following flow:

- Open the bridge URL in a mobile browser.
- Enter or use the authentication token.
- Type a prompt into a chat-like input field.
- Submit the prompt.
- See CLI responses stream back in the same window.
- Optionally clear output and send another prompt.

Live streaming should feel like watching a local terminal session, with text appended as it is emitted by Claude.

## Architecture Outline

This project is expected to include several logical components:

- **Server**: Accepts mobile requests, validates token, and launches Claude CLI processes.
- **Client**: Mobile UI rendered in a browser, connects over a WebSocket or equivalent streaming channel.
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

## Next Step

Translate this specification into a minimal implementation with a local server, secure token authentication, a mobile web frontend, and streamed CLI output.
