# Local MVP Runbook

[Portuguese (Brazil)](./local-mvp.pt-BR.md)

This runbook describes the first practical local MVP path for
VeraBrain:

- Postgres + `pgvector` provisioned through project-local Docker Compose
- VeraBrain MCP launched from the host over `stdio`
- Hermes configured as the MCP client

## Prerequisites

- Docker and Docker Compose
- `uv`
- Hermes Agent with MCP support
- project Python dependencies installed through `uv sync`

## Files Used by This Runbook

- [`docker-compose.yml`](../../docker-compose.yml)
- [`.env.example`](../../.env.example)
- [`pyproject.toml`](../../pyproject.toml)

## 1. Prepare Local Configuration

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

The default values already match the local MVP path:

- host: `127.0.0.1`
- port: `54329`
- database: `verabrain`
- user: `verabrain`
- password: `verabrain`
- migration mode: `apply`

## 2. Start the Project-Local Postgres Service

Start the dedicated VeraBrain database:

```bash
docker compose up -d verabrain-postgres
```

Check that the container is healthy:

```bash
docker compose ps
```

Stop the local database when needed:

```bash
docker compose down
```

To remove the persisted database volume too:

```bash
docker compose down -v
```

## 3. Sync the Python Environment

```bash
uv sync
```

The local MVP launcher depends on:

- `mcp[cli]` for the MCP server runtime
- `psycopg[binary]` for the Postgres driver

## 4. Launch the VeraBrain MCP Server from the Host

Run the local MVP launcher with the `.env` file:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

This path:

- reads the explicit runtime settings
- connects to the Compose-backed Postgres instance
- applies or verifies the VeraBrain schema
- starts the MCP server over `stdio`

## 5. Configure Hermes as the MCP Client

Add a local MCP server entry to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  verabrain:
    command: "uv"
    args:
      - "--directory"
      - "/home/carlos/projects/veramind"
      - "run"
      - "verabrain-mcp-local-mvp"
    env:
      VERABRAIN_POSTGRES_HOST: "127.0.0.1"
      VERABRAIN_POSTGRES_PORT: "54329"
      VERABRAIN_POSTGRES_DB: "verabrain"
      VERABRAIN_POSTGRES_USER: "verabrain"
      VERABRAIN_POSTGRES_PASSWORD: "verabrain"
      VERABRAIN_POSTGRES_MIGRATION_MODE: "apply"
      VERABRAIN_POSTGRES_FAIL_FAST: "true"
      VERABRAIN_MCP_SERVER_NAME: "VeraBrain"
```

This keeps the intended authority split:

- Hermes owns session-local and prompt memory
- VeraBrain owns durable memory in its own Postgres store

## 6. Manual Smoke Path

After Hermes is running with the `verabrain` MCP server enabled:

1. Save one explicit durable memory through `save_memory`.
2. Retrieve it through `search_memory`.
3. Retrieve bounded context through `get_context_bundle`.

Expected outcomes:

- the save call succeeds and returns a durable memory record
- bounded retrieval returns the saved record
- Hermes consumes VeraBrain recall through MCP without replacing its own
  session-local memory behavior

## 7. Optional Skill Layer

If you want Hermes to load explicit procedural guidance for VeraBrain
usage, install the MVP skill too:

- [Hermes VeraBrain Skill Runbook](./hermes-verabrain-skill.md)

## Troubleshooting

### Postgres is not reachable

Check:

- `docker compose ps`
- whether the `.env` host/port values match the Compose mapping

### Schema bootstrap fails

Check:

- the Postgres container is healthy
- the selected image supports `pgvector`
- the runtime settings still point at the VeraBrain Compose database

### MCP startup fails because the SDK is missing

Resync the project environment:

```bash
uv sync
```

Then retry:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

### Postgres startup fails because the driver is missing

Resync the project environment:

```bash
uv sync
```

Then retry:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```
