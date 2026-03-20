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

1. provision a local Postgres instance with `pgvector` through Docker
   Compose
2. provide explicit runtime settings to VeraBrain
3. bootstrap or verify the Postgres schema through infrastructure
   runtime wiring
4. assemble the `VeraBrainApplication` over the Postgres-backed
   unit-of-work
5. expose the application through the MCP server surface from the host
   over `stdio`
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

The canonical local startup sequence is:

1. start the project-local Docker Compose Postgres service
2. load explicit runtime settings for the local VeraBrain process
3. create a startup connection with `PostgresConnectionFactory`
4. run `bootstrap_postgres_runtime_schema(...)`
5. build the application through
   `PostgresRuntimeApplicationFactory.create_application(...)`
6. expose the application through the MCP server entrypoint on the host
7. let Hermes launch or connect to that host process over `stdio`

This ordering is intentional:

- infrastructure readiness is checked before the MCP surface is exposed
- schema handling stays out of MCP tool behavior
- the MCP server never becomes responsible for implicit Postgres setup

## Local Infrastructure Assumptions

The first local MVP should assume:

- a contributor provisions Postgres locally in a reproducible way
  through project-owned Docker Compose configuration
- the required `pgvector` extension is available
- the VeraBrain MCP server starts from the host process environment
- the MVP path should not depend on undocumented machine-local setup

This split is intentional:

- Compose isolates the durable Postgres dependency from the rest of the
  machine
- host-launched `stdio` keeps the initial Hermes MCP integration simple
  and aligned with the current server surface

The minimum Compose environment should provide:

- one dedicated Postgres service for VeraBrain
- explicit database credentials and database name for local MVP use
- a host-visible port so the host-launched VeraBrain process can connect
- a project-scoped persistent volume
- a readiness signal, such as a healthcheck, so the startup flow can
  wait for Postgres intentionally
- `pgvector` availability through the selected image or initialization
  path

The initial Compose scope should stay narrow. It is enough for the MVP
to own the durable database path without yet containerizing the
VeraBrain MCP process itself.

## Hermes MCP Interaction Path

The local MVP remains MCP-first.

Hermes should:

- keep local session and prompt memory as defined by the archived
  boundary change
- call VeraBrain through the existing host-launched MCP tool surface
- use `save_memory` for explicit durable promotion
- use `search_memory` or `get_context_bundle` for bounded durable recall

The first local MVP must not depend on a Hermes-native plugin or skill
to function.

The minimum Hermes-side integration shape should be:

- one explicit local MCP server entry for VeraBrain
- a host command that starts the VeraBrain MCP server over `stdio`
- explicit environment values for the VeraBrain runtime settings
- no sharing of Hermes SQLite/session persistence as VeraBrain durable
  storage

This keeps the authority boundary intact:

- Hermes remains the MCP client and owner of session-local memory
- VeraBrain remains the MCP server and owner of durable memory

## Manual Smoke Workflow

The minimum manual smoke workflow should prove:

1. project-local Docker Compose Postgres is available
2. VeraBrain can start from the host over the configured Postgres path
3. Hermes can launch or connect to the local VeraBrain MCP server over
   `stdio`
4. a durable memory can be saved through `save_memory`
5. the saved memory can be retrieved in bounded form through
   `search_memory` or `get_context_bundle`
6. the observed behavior matches the archived memory-loop MVP outcomes

The smoke workflow should be documented so a contributor can follow it
without reverse engineering the codebase.

The minimum smoke path should be documented as a short sequence:

1. start Compose Postgres
2. export or provide the runtime settings expected by the VeraBrain host
   process
3. configure Hermes with the local VeraBrain MCP server entry
4. start Hermes with that MCP server enabled
5. invoke one explicit durable save
6. invoke one bounded retrieval
7. confirm the returned behavior matches the local MVP expectation

## Failure and Fallback Paths

The local MVP should make these failure states observable:

- Postgres unavailable or misconfigured at startup
- schema state missing or invalid
- MCP dependency unavailable
- memory save succeeds without embedding
- memory save fails because durable persistence failed

The change should prefer explicit startup and smoke-path failures over
silent fallback into an unintended local mode.

For the startup flow specifically:

- Postgres startup failure should stop the local MVP before MCP startup
- schema verification failure should stop the local MVP before MCP
  startup
- MCP dependency failure should stop the local MVP after application
  assembly is attempted, not silently downgrade to a non-MCP mode

## Out of Scope

This change does not cover:

- production deployment hardening
- non-local runtime environments
- native Hermes plugin integration
- advanced knowledge modeling
- execution workflows or GTD-oriented behavior
