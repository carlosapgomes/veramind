# Pgvector Driver Registration

## Why

The OpenAI-backed local MVP now generates embeddings successfully, but
the Postgres runtime path still fails to use them reliably because the
`psycopg` driver is not registering `pgvector` types on connection
startup.

Without driver-level type registration:

- `embedding` values can fail to round-trip cleanly from Postgres back
  into Python
- semantic query parameters can be adapted inconsistently
- the local MVP appears to have a schema or retrieval bug even though
  the vector extension and stored values are present

## What Changes

- Add the `pgvector` Python dependency required for Psycopg 3 type
  registration
- Register `pgvector` types on the default Postgres runtime connection
  path
- Add tests that cover driver registration and embedding round-tripping
  expectations

## Impact

- Makes the Postgres runtime path treat `vector` columns and parameters
  as first-class values
- Unblocks real semantic retrieval in the local MVP
- Keeps the fix at the infrastructure driver boundary
