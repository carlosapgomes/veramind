# PROJECT_CONTEXT.md

## Purpose

Executive summary for quick resumption after pauses and for onboarding
new contributors.

## Authoritative Sources

- `AGENTS.md`
- `openspec/specs/`
- `openspec/changes/`
- `docs/adr/`
- `docs/releases/`
- `texts/personal_agent_architecture_notes.md`
- If conflicts exist, the most recent specs and artifacts in Git win.

## System Goal

Build a personal AI agent ("Second Brain / Personal OS") with durable
memory, explicit tools, and a consultable knowledge base.

The system should help the user:

- preserve long-term context
- recover relevant information at the right time
- execute tool-oriented flows safely
- evolve incrementally with a simple and observable architecture

## High-Level Architecture

- **agent runtime**: Orchestrates the agent, prompts, context, and tool
  calls.
- **memory layer**: Stores durable information about the user,
  preferences, decisions, and active projects.
- **tool layer**: Exposes explicit tools and controlled wrappers for
  agent capabilities.
- **knowledge system**: Provides a consultable base of documents, notes,
  and references.
- **docs** (`docs`): Documentation and traceability.
- **scripts** (`scripts`): Automation and utility scripts.
- **tests** (`tests`): Automated test suite.

Desired dependency direction:

- `agent runtime -> memory/tool/knowledge contracts`
- `tool layer -> external adapters`
- no reverse dependency into the runtime

Agreed initial stack:

- Python 3.11+ as the primary implementation direction for
  VeraBrain-on-Hermes
- `uv` as the intended Python package and environment manager
- TypeScript/Node.js as the existing repository scaffold, not the
  primary product direction
- Current repository checks: Vitest, ESLint, Prettier, and
  markdownlint-cli
- Postgres + pgvector as the target persistence architecture
- Hermes Agent as the intended runtime shell
- MCP-first integration with an optional thin Hermes plugin later

Current project state:

- Foundation and specification phase
- Initial TypeScript application scaffold is in place
- Initial architectural boundaries are encoded in a tested module
- Memory layer foundation is now specified in OpenSpec
- VeraBrain concept modeling is documented in `docs/domain/`
- Stack direction has been realigned from the original TypeScript-first
  standalone path to a Python-first Hermes-centered path

## Documentation Policy

- English is the default language for normative project artifacts.
- `README.md` and relevant documents under `docs/` must maintain a
  synchronized `pt-BR` mirror.
- Bilingual document pairs must be updated together in the same change.

## Non-Negotiable Rules

- Do not break public API contracts without a versioned change.
- Every relevant change must leave evidence in Git
  (spec, task, and commit).
- Keep explicit boundaries between runtime, memory, tools, and
  knowledge.
- Prefer controlled wrappers over unrestricted shell access.
- Prioritize simplicity and iteration capability over premature
  architecture.

## Quality Bar

- Relevant tests run locally before merge.
- Lint and static checks pass without critical errors.
- Medium/high-risk changes require a rollback plan.
- New features and critical bug fixes follow TDD.
- Operational documentation must reflect the actual repository state.
- Bilingual document mirrors stay synchronized.

## Likely Next Slices

- Design the VeraBrain core and adapter boundaries
- Define the initial Python project skeleton for the Hermes-centered
  implementation path
- Add ADRs for boundaries, persistence, and the tool model

<!-- generated-by: project-context-maintainer -->
