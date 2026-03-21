# Postgres Memory Search Null Filter

## Why

The Postgres memory repository currently builds optional salience
filters using a nullable parameter shape:

- `(%(min_salience)s IS NULL OR salience >= %(min_salience)s)`

With the real `psycopg` runtime path, that can produce an untyped `NULL`
parameter and trigger a Postgres error during memory retrieval:

- `could not determine data type of parameter`

This breaks the local MVP retrieval path even though the memory query is
otherwise valid.

## What Changes

- Define a bugfix slice for optional memory-search salience filters on
  the Postgres path
- Keep the existing memory search contract unchanged
- Build lexical and semantic candidate queries without nullable typed
  placeholders when `min_salience` is absent
- Add regression coverage for the affected query construction

## Non-Goals

- Redefining memory retrieval ranking policy
- Changing the public memory-search request contract
- Redesigning the Postgres unit-of-work model
- Introducing a broader transaction-recovery policy in this change

## Impact

- Fixes the current Postgres runtime retrieval failure on optional
  salience filtering
- Keeps the bugfix local to the infrastructure adapter
- Preserves the local MVP path without changing application semantics
