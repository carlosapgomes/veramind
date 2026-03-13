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

- TypeScript
- Node.js 22 LTS
- npm
- Vitest
- ESLint + Prettier + markdownlint-cli
- Postgres + pgvector as the target persistence architecture
- pi-mono as the intended agent runtime

Current project state:

- Foundation and specification phase
- Initial TypeScript application scaffold is in place
- Initial architectural boundaries are encoded in a tested module

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

- Specify the memory layer foundation
- Add ADRs for boundaries, persistence, and the tool model

<!-- generated-by: project-context-maintainer -->
