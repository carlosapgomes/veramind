# Design: Postgres MCP Local MVP

## Objective

Define the first practical local run path for VeraBrain so a
contributor can start the system, connect it through MCP, and manually
exercise the archived memory-loop MVP behavior.

This change is not about expanding product scope. It is about turning
the current architecture and test baseline into a reproducible local
workflow.

## Canonical Local MVP Flow

The canonical local MVP flow is:

1. provision a local Postgres instance with `pgvector`
2. provide explicit runtime settings to VeraBrain
3. bootstrap or verify the Postgres schema through infrastructure
   runtime wiring
4. assemble the `VeraBrainApplication` over the Postgres-backed
   unit-of-work
5. expose the application through the MCP server surface
6. connect Hermes to that MCP server
7. manually exercise `save_memory`, `search_memory`, and
   `get_context_bundle`

The local MVP path must reuse the existing runtime, application, and
adapter boundaries rather than introducing a special-purpose launcher
stack.

## Runtime Assembly

The canonical runtime assembly path is:

- explicit runtime settings
- Postgres connection factory
- schema bootstrap or verification
- Postgres-backed application factory
- MCP application adapter
- MCP server startup

This preserves the existing boundary that operational wiring belongs to
infrastructure bootstrap and not to application services or MCP tool
semantics.

## Local Infrastructure Assumptions

The first local MVP should assume:

- a contributor can provision Postgres locally in a reproducible way
- the required `pgvector` extension is available
- the MVP path should not depend on undocumented machine-local setup

Containerized local infrastructure is the preferred initial direction
because it minimizes hidden environmental assumptions and improves
repeatability across contributors.

## Hermes MCP Interaction Path

The local MVP remains MCP-first.

Hermes should:

- keep local session and prompt memory as defined by the archived
  boundary change
- call VeraBrain through the existing MCP tool surface
- use `save_memory` for explicit durable promotion
- use `search_memory` or `get_context_bundle` for bounded durable recall

The first local MVP must not depend on a Hermes-native plugin or skill
to function.

## Manual Smoke Workflow

The minimum manual smoke workflow should prove:

1. local Postgres is available
2. VeraBrain can start over the configured Postgres path
3. the MCP server is reachable through its intended local runtime path
4. a durable memory can be saved
5. the saved memory can be retrieved in bounded form
6. the observed behavior matches the archived memory-loop MVP outcomes

The smoke workflow should be documented so a contributor can follow it
without reverse engineering the codebase.

## Failure and Fallback Paths

The local MVP should make these failure states observable:

- Postgres unavailable or misconfigured at startup
- schema state missing or invalid
- MCP dependency unavailable
- memory save succeeds without embedding
- memory save fails because durable persistence failed

The change should prefer explicit startup and smoke-path failures over
silent fallback into an unintended local mode.

## Out of Scope

This change does not cover:

- production deployment hardening
- non-local runtime environments
- native Hermes plugin integration
- advanced knowledge modeling
- execution workflows or GTD-oriented behavior
