# ADR-0005: Adopt a Postgres and pgvector persistence architecture

[Portuguese (Brazil)](./ADR-0005-adopt-postgres-pgvector-persistence-architecture.pt-BR.md)

## Status

Accepted

## Context

ADR-0002 positioned VeraBrain as a Hermes-centered subsystem with a
core kept separate from MCP and any future native Hermes adapter.

Since then, the repository has gained:

- explicit repository and unit-of-work ports
- an initial in-memory infrastructure adapter
- callable application services over the port layer

That means the architectural seam for persistence is now stable enough
to lock the intended production persistence direction before building
the concrete database adapter.

The project already carries Postgres and `pgvector` as the intended
target, but that choice still needs an accepted ADR that explains how
those technologies fit the current core-plus-adapters architecture.

## Decision

Adopt Postgres plus `pgvector` as the target production persistence
architecture for VeraBrain.

This means:

- Postgres is the system of record for memory, knowledge, execution,
  and explicit knowledge links
- `pgvector` is the planned vector-search extension for embedding-backed
  retrieval
- the Postgres implementation will live in infrastructure adapters and
  fulfill the existing application-layer repository and unit-of-work
  ports
- the application layer will remain adapter-neutral and will not expose
  SQL, table names, migration details, or `pgvector` concerns in its
  public contracts

The in-memory adapter remains useful for tests and local composition,
but it is not the target production persistence path.

## Alternatives Considered

1. Keep only the in-memory adapter for the near term
2. Adopt SQLite as the first durable persistence backend
3. Adopt Postgres plus `pgvector` as the durable persistence baseline

## Consequences

- Positives:
  - matches the already stated long-term persistence target
  - supports structured relational storage and vector-backed retrieval
    in the same persistence platform
  - fits the current repository-port architecture without changing
    application contracts
  - keeps local and test adapters separate from production storage
- Negatives/Trade-offs:
  - increases operational complexity compared with an in-memory-only or
    SQLite path
  - requires migrations, schema design, and indexing discipline
  - creates a stronger dependency on infrastructure setup before
    end-to-end persistence flows can be exercised in production form

## Notes

This ADR chooses the target persistence architecture. It does not yet
define the final schema, retrieval scoring formula, or migration plan.
Those details should remain in specs and implementation slices.
