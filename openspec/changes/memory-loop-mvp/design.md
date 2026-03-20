# Design: Memory Loop MVP

## Objective

Define the first observable VeraBrain product loop before broadening
scope into production hardening, richer knowledge modeling, or
execution workflows.

The MVP is not "all memory features". It is the smallest vertical slice
that proves VeraBrain can capture, store, retrieve, and expose durable
memory usefully in the Hermes-centered direction.

## Canonical MVP Flow

The canonical flow is:

1. A caller submits a durable memory candidate through the MCP-facing
   VeraBrain surface.
2. VeraBrain routes that request into the memory application service.
3. The write path classifies the input for memory capture.
4. The write path checks for materially similar existing memories.
5. The write path attempts embedding generation when a provider is
   available.
6. VeraBrain persists the resulting memory record durably.
7. A later bounded query retrieves relevant memories.
8. VeraBrain returns bounded memory context to Hermes through MCP.

This flow is the primary happy path the MVP must prove.

## Canonical Happy Path

The canonical observable happy path for this change is:

1. Hermes calls the MCP-facing VeraBrain memory capture surface with a
   durable memory candidate.
2. The MCP adapter translates that payload into a VeraBrain memory
   request without embedding provider or storage details leaking into
   the tool contract.
3. `MemoryApplicationService` classifies the input as a durable memory
   candidate.
4. The write path checks for materially matching existing memories.
5. The write path resolves an embedding when a provider is available,
   while preserving explicit fallback metadata if no embedding is
   available.
6. The resulting memory record is persisted durably through the
   repository and unit-of-work boundary.
7. Hermes later requests relevant memory context through the
   MCP-facing retrieval surface.
8. VeraBrain executes bounded retrieval and returns a small,
   agent-consumable context payload.

This is the exact flow the MVP must prove before scope expands into
production hardening, broader knowledge work, or execution workflows.

## Layer Responsibilities

### MCP adapter

- Accepts tool input from Hermes.
- Maps MCP requests into VeraBrain application contracts.
- Returns bounded memory context in an agent-consumable shape.
- Does not own memory rules, retrieval ranking policy, or persistence
  semantics.

### Application layer

- Orchestrates the capture and retrieval loop.
- Applies memory classification, duplicate assessment, embedding
  attachment, and fallback handling through core/application contracts.
- Coordinates the unit-of-work boundary.

### Core and write-path rules

- Decide whether a capture belongs in the memory pipeline.
- Decide whether a materially matching memory should be updated.
- Resolve duplicate embedding actions and embedding fallback state.

### Infrastructure layer

- Persists durable memory records.
- Executes bounded search through the repository ports.
- Provides the concrete Postgres runtime and migration path when the MVP
  is proven beyond in-memory or adapter-only tests.

## Observable Success Conditions

The MVP should be considered behaviorally proven only when all of the
following are true:

- Hermes can initiate the capture through the MCP-facing surface.
- A durable capture can be persisted through the real write path.
- The persisted record can carry an embedding when available.
- The persisted record remains observable when embedding capture
  degrades.
- A later bounded query can retrieve that memory as relevant context.
- Hermes can consume that bounded context through the MCP-facing
  surface.

## Failure and Fallback Paths

The MVP must make two degradation cases explicit:

- embedding degradation:
  the write path may still persist the memory if policy allows it, and
  the fallback remains observable
- persistence degradation:
  the caller must receive explicit failure and the loop must not be
  reported as successful

The MVP should prove graceful degradation, not silent degradation.

## Out of Scope

The MVP intentionally does not define:

- the final Hermes-versus-VeraBrain memory authority policy
- execution workflows or GTD-inspired planning behavior
- large-scale knowledge graph semantics
- production-hardening concerns such as readiness, ops runbooks, or
  deployment maturity as the primary goal

Those belong to later changes after the memory loop is proven.

## Planned Vertical Slices

1. Define the canonical observable happy path of the loop.
2. Define the minimum MCP-facing bounded retrieval behavior.
3. Define explicit fallback behavior for degraded embedding or
   persistence.
4. Add a vertical integration slice across application, adapters, and
   infrastructure.
5. Add end-to-end validation coverage for that loop.
