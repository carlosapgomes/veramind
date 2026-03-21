# Proposal: Postgres JSONB Adaptation

## Why

The local MVP exposed a real-runtime gap in the Postgres adapter: write
paths send Python `dict` values directly to `JSONB` placeholders. The
fake connection tests tolerated this, but real `psycopg` rejects raw
`dict` values with `cannot adapt type 'dict' using placeholder '%s'`.

This bug affects memory writes today and leaves the same failure mode
available in other Postgres-backed repositories that persist metadata to
`JSONB` columns.

## What Changes

- Adapt Postgres metadata parameters through the `psycopg` `JSONB`
  wrapper at the infrastructure boundary.
- Apply the same adaptation consistently across memory, knowledge,
  knowledge-link, and execution repository write paths.
- Add tests that assert `JSONB` parameters are no longer passed as raw
  Python `dict` values.

## Impact

- Fixes real `save_memory` writes in the host-launched MCP MVP path.
- Prevents the same adaptation failure from surfacing later in other
  repository adapters.
- Preserves the current application and core contracts, keeping the fix
  local to infrastructure.
