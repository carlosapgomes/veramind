# PROJECT_CONTEXT.md

## Purpose

Executive summary for quick resumption after pauses and for onboarding
new contributors.

## Authoritative Sources

- `AGENTS.md`
- `openspec/specs/`
- `openspec/changes/`
- `openspec/changes/archive/`
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
- Current repository checks: pytest, Ruff, Pyright, mdformat, and
  PyMarkdown
- Postgres + pgvector as the target persistence architecture
- Hermes Agent as the intended runtime shell
- MCP-first integration with an optional thin Hermes plugin later

Delivery approach:

- Implementation should progress through small vertical slices that
  touch the necessary layers to prove observable behavior.
- Broad horizontal expansion by layer should be avoided unless a slice
  is intentionally design-only or infrastructure-only.

Current project state:

- Foundation and specification phase
- Initial Python package skeleton is now in place under `src/verabrain`
- Initial architectural boundaries are encoded in a tested Python
  module
- Memory layer foundation is now specified in OpenSpec
- The legacy foundation, stack-realignment, and bilingual-governance
  changes are now ready to be treated as archived baseline work
- The memory-layer foundation change has now been reconciled and is
  ready to be treated as archived baseline work
- The memory write path now has an explicit classification boundary for
  `memory_candidate` versus `ignore`
- The memory write path now deduplicates through `find_similar` and
  updates materially matching memory records before write-side upsert
- The memory write path now enforces the normative allowed values for
  memory `type` and `scope`
- Repository and persistence ports are now specified for memory,
  knowledge, and execution
- Initial in-memory persistence adapters now implement the repository
  ports and unit-of-work boundary
- Persistence, retrieval-policy, and tool-model ADRs are now accepted
- Postgres + pgvector persistence adapter boundaries are now specified
- Initial Postgres-backed repository and unit-of-work adapters now
  exist in the infrastructure layer
- Initial schema and migration support now exist for the Postgres
  persistence path
- A dedicated runtime settings surface and Postgres connection factory
  now exist for the operational wiring path
- Runtime bootstrap helpers now support explicit Postgres migration
  apply, verify, and skip modes with schema verification checks
- A dedicated Postgres application factory now wires runtime settings
  into the Postgres unit of work and VeraBrain application assembly
- The wired Postgres runtime path now has startup and operational tests
  covering bootstrap sequencing, explicit schema failure, and soft
  startup fallback behavior
- The completed Postgres runtime and operational wiring OpenSpec change
  is now ready to be treated as archived baseline work
- The completed foundation and hybrid retrieval OpenSpec changes are now
  ready to be treated as archived baseline work
- The first hybrid memory retrieval flow now exists in the Postgres
  adapter with optional semantic input and lexical fallback
- Retrieval scoring helpers now live in the VeraBrain core with unit
  tests for ranking behavior
- Context-bundle assembly now passes optional memory-query embeddings
  into bounded memory retrieval when a provider is available
- Hybrid retrieval now has explicit fallback behavior for environments
  without semantic recall
- Initial MCP tool schemas and request/response mappings are now
  specified for the application contracts
- The first callable application services now exist for memory,
  knowledge, execution, and bounded context retrieval
- The MCP adapter now dispatches tool calls into the callable
  application services
- An initial stdio-first MCP server definition and runtime entrypoint
  now exist over the wired adapter surface
- VeraBrain concept modeling is documented in `docs/domain/`
- The temporary TypeScript/Node scaffold has been retired from the
  repository
- Core-and-adapters architecture is now specified for the
  Hermes-centered path
- The completed memory-embedding write-path OpenSpec change is now
  ready to be treated as archived baseline work
- The memory write path now has an explicit adapter-neutral embedding
  provider boundary for memory capture
- The memory write path now attaches generated embeddings during
  capture when a provider is available
- The memory write path now persists explicit embedding fallback status
  when capture is unavailable or fails
- Deduplicated memory updates now record whether embeddings were
  preserved or replaced during write-side reconciliation
- The memory embedding write path now has dedicated unit coverage for
  embedding resolution, fallback status, and deduplicated action
  metadata
- The completed `memory-loop-mvp` OpenSpec change is now ready to be
  treated as archived baseline work
- The archived `memory-loop-mvp` change includes an explicit design
  artifact for the canonical vertical memory loop
- The archived `memory-loop-mvp` change defines the canonical happy
  path for `capture -> classify -> deduplicate -> embed -> persist ->
  retrieve -> expose via MCP`
- The archived `memory-loop-mvp` change defines the minimum bounded
  retrieval behavior that Hermes must consume through the MCP-facing
  surface
- The archived `memory-loop-mvp` change defines explicit fallback
  outcomes for `saved_with_embedding`, `saved_without_embedding`, and
  `save_failed`
- The archived `memory-loop-mvp` change has an initial vertical
  integration slice over MCP adapter, application services, and
  in-memory infrastructure
- The archived `memory-loop-mvp` change has end-to-end validation
  coverage for `saved_with_embedding`, `saved_without_embedding`, and
  `save_failed` through the MCP-facing loop
- The completed `hermes-verabrain-memory-boundary` OpenSpec change is
  now ready to be treated as archived baseline work
- The archived `hermes-verabrain-memory-boundary` change defines the
  initial authority model across `Hermes-owned`,
  `promotion-candidate`, and `VeraBrain-owned` memory roles
- The archived `hermes-verabrain-memory-boundary` change defines the
  consultation order of `Hermes local context first`,
  `VeraBrain durable retrieval second`
- The archived `hermes-verabrain-memory-boundary` change defines
  conservative promotion rules with `not-promotable-by-default` versus
  `promotion-candidate` session material
- The archived `hermes-verabrain-memory-boundary` change defines the
  MCP-first interaction pattern through `search_memory`,
  `get_context_bundle`, and `save_memory`
- The archived `hermes-verabrain-memory-boundary` change has
  integration checks showing that retrieval does not promote memory,
  explicit `save_memory` does, and failed persistence does not transfer
  durable authority

## Documentation Policy

- English is the default language for normative project artifacts.
- `README.md` and relevant documents under `docs/` must maintain a
  synchronized `pt-BR` mirror.
- Bilingual document pairs must be updated together in the same change.

## Non-Negotiable Rules

- Do not break public API contracts without a versioned change.
- Every relevant change must leave evidence in Git
  (spec, task, and commit).
- A successful slice is only complete after its commit is pushed from
  the current branch.
- Prefer slices that prove observable end-to-end behavior across the
  relevant layers instead of widening one layer in isolation.
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

- The `postgres-mcp-local-mvp` change is now archived as completed
  baseline work
- The archived local MVP baseline now includes the canonical
  `Compose Postgres -> host stdio MCP -> manual smoke` path
- The archived local MVP baseline now includes the
  `verabrain-mcp-local-mvp` launcher, smoke-oriented integration
  coverage, project-local Compose database assets, and bilingual
  runbook documentation
- The active change is now `hermes-verabrain-mvp-usability`
- The next focus is the Hermes-facing usability layer over the existing
  local MVP baseline, including the future `VeraBrain` skill as a
  procedural layer over MCP
- The active usability change now has a design artifact for the Hermes
  decision flow, explicit intent patterns, and the role of the future
  `VeraBrain` skill

<!-- generated-by: project-context-maintainer -->
