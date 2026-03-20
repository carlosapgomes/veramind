# Runbook do MVP Local

[English](./local-mvp.md)

Este runbook descreve o primeiro caminho prático de MVP local do
VeraBrain:

- Postgres + `pgvector` provisionados por Docker Compose do projeto
- MCP do VeraBrain iniciado no host via `stdio`
- Hermes configurado como cliente MCP

## Pré-requisitos

- Docker e Docker Compose
- `uv`
- Hermes Agent com suporte a MCP

## Arquivos usados por este runbook

- [`docker-compose.yml`](../../docker-compose.yml)
- [`.env.example`](../../.env.example)
- [`pyproject.toml`](../../pyproject.toml)

## 1. Preparar a configuração local

Crie um arquivo `.env` local a partir do exemplo:

```bash
cp .env.example .env
```

Os valores padrão já correspondem ao caminho do MVP local:

- host: `127.0.0.1`
- porta: `54329`
- banco: `verabrain`
- usuário: `verabrain`
- senha: `verabrain`
- modo de migration: `apply`

## 2. Subir o serviço Postgres do projeto

Suba o banco dedicado do VeraBrain:

```bash
docker compose up -d verabrain-postgres
```

Verifique se o container está saudável:

```bash
docker compose ps
```

Pare o banco local quando necessário:

```bash
docker compose down
```

Para remover também o volume persistido:

```bash
docker compose down -v
```

## 3. Sincronizar o ambiente Python

```bash
uv sync
```

## 4. Iniciar o servidor MCP do VeraBrain no host

Execute o launcher do MVP local usando o arquivo `.env`:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

Esse caminho:

- lê as runtime settings explícitas
- conecta ao Postgres provisionado pelo Compose
- aplica ou verifica o schema do VeraBrain
- inicia o servidor MCP via `stdio`

## 5. Configurar o Hermes como cliente MCP

Adicione uma entrada de servidor MCP local em `~/.hermes/config.yaml`:

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

Isso preserva a separação de autoridade pretendida:

- Hermes continua dono da memória de sessão e da memória de prompt
- VeraBrain continua dono da memória durável em seu próprio Postgres

## 6. Fluxo manual de smoke test

Depois que o Hermes estiver rodando com o servidor MCP `verabrain`
habilitado:

1. Salve uma memória durável explícita com `save_memory`.
2. Recupere essa memória com `search_memory`.
3. Recupere contexto bounded com `get_context_bundle`.

Resultados esperados:

- a chamada de save retorna um registro de memória durável
- o retrieval bounded retorna o registro salvo
- o Hermes consome o recall do VeraBrain via MCP sem substituir seu
  próprio comportamento de memória local de sessão

## Troubleshooting

### O Postgres não está acessível

Verifique:

- `docker compose ps`
- se os valores de host/porta do `.env` correspondem ao mapeamento do
  Compose

### O bootstrap do schema falha

Verifique:

- se o container Postgres está saudável
- se a imagem escolhida suporta `pgvector`
- se as runtime settings ainda apontam para o banco do Compose do
  VeraBrain

### O startup do MCP falha porque o SDK está ausente

Instale a dependência opcional de MCP no ambiente do projeto:

```bash
uv add "mcp[cli]"
```

Ou execute o launcher com dependência ad hoc:

```bash
uv run --with "mcp[cli]" --env-file .env verabrain-mcp-local-mvp
```
