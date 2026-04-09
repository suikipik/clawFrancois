<!--
## Sync Impact Report

- **Version change**: 0.0.0 → 1.0.0
- **Modified principles**: N/A (initial ratification)
- **Added sections**:
  - Core Principles (5 principles)
  - Technical Constraints
  - Development Workflow
  - Governance
- **Removed sections**: None
- **Templates requiring updates**:
  - `.specify/templates/plan-template.md` — ✅ No updates needed (Constitution Check section is generic and will be filled dynamically)
  - `.specify/templates/spec-template.md` — ✅ No updates needed (template is principle-agnostic)
  - `.specify/templates/tasks-template.md` — ✅ No updates needed (task phases are generic)
- **Follow-up TODOs**: None
-->

# Claude Mobile Bridge Constitution

## Core Principles

### I. Local-First Execution

All CLI execution MUST remain on the user's local machine. No prompt
content or CLI output may be routed through third-party compute
services. The bridge is a transport layer only — it forwards prompts
inward and streams results outward, never delegating execution.

**Rationale**: The project exists to extend the local CLI experience
to mobile, not to replace it with a hosted service. Local execution
preserves privacy, avoids API costs, and keeps the user in control
of their environment.

### II. Security by Default

Every access path MUST be authenticated. Anonymous prompt submission
is forbidden. Specific rules:

- A per-session or fixed secret token MUST gate all client requests.
- The bridge MUST NOT bind to public interfaces by default; local
  network or explicit tunnel only.
- Tokens MUST be generated with cryptographically secure randomness.
- Documentation MUST warn users to keep tokens private.

**Rationale**: The bridge exposes a local CLI that can execute
arbitrary prompts. Unauthenticated access would be a critical
security flaw.

### III. Streaming-First Output

CLI output MUST be streamed to the client as it is produced. Buffering
the full response before delivery is not acceptable. The mobile user
MUST see text appear progressively, replicating the experience of
watching a local terminal.

**Rationale**: The core value proposition is a live terminal feel on
mobile. Batch delivery would eliminate that experience.

### IV. Client-Agnostic Architecture

The bridge core (server, CLI bridge, authentication) MUST be
independent of any specific client channel. Adding a new client
(Telegram, Discord, web UI, native app) MUST NOT require changes to
the bridge core. Client adapters are separate modules.

**Rationale**: The project deliberately leaves the client channel open.
Architecture must support that flexibility without tight coupling.

### V. Simplicity and Reuse

Favor existing free services and APIs over custom infrastructure.
Minimize dependencies. Specific rules:

- For v0.1, choose the channel that ships fastest with the least
  custom code.
- Do not build what already exists (bot APIs, auth frameworks,
  WebSocket libraries).
- YAGNI applies: no feature is built until it is needed.
- Start simple; complexity MUST be justified in implementation plans.

**Rationale**: Speed of delivery for v0.1 matters more than custom
infrastructure. A working bridge with minimal code is better than
an overengineered one that ships late.

## Technical Constraints

- **Runtime**: Local machine only; no cloud functions or remote
  execution environments.
- **Dependencies**: Minimal — each dependency MUST justify its
  inclusion. Prefer standard library where feasible.
- **Transport**: WebSocket or SSE for streaming; HTTP polling is
  acceptable only as a fallback for constrained channels.
- **Token storage**: Tokens MUST NOT be logged, committed to version
  control, or transmitted in URL paths visible in server logs.
- **Platform**: The bridge server MUST run on macOS and Linux at
  minimum.

## Development Workflow

- **Branching**: One feature branch per spec. Branch names follow the
  pattern `###-feature-name`.
- **Testing**: Integration tests MUST cover the critical path — prompt
  submission, token validation, and streamed output delivery. Unit
  tests are encouraged for isolated logic but not mandated for every
  function.
- **Code review**: All changes to bridge core or security-related code
  MUST be reviewed before merge.
- **Commits**: Atomic commits with descriptive messages. Each commit
  SHOULD represent a single logical change.
- **Documentation**: User-facing changes MUST update relevant docs.
  Internal changes SHOULD update inline comments only when the logic
  is non-obvious.

## Governance

This constitution is the highest-authority document for project
decisions. When a practice conflicts with a principle above, the
principle wins.

**Amendment procedure**:
1. Propose the change with rationale.
2. Document the amendment in the Sync Impact Report.
3. Increment the version per semantic versioning:
   - MAJOR: Principle removed or fundamentally redefined.
   - MINOR: New principle or section added, or material expansion.
   - PATCH: Clarification, wording, or non-semantic refinement.
4. Update dependent templates if the change affects them.

**Compliance**: Implementation plans MUST include a Constitution Check
gate. Reviews SHOULD verify alignment with active principles.

**Version**: 1.0.0 | **Ratified**: 2026-04-09 | **Last Amended**: 2026-04-09
