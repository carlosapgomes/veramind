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
- dependências Python do projeto instaladas com `uv sync`

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

O arquivo `.env.example` também inclui as runtime settings opcionais de
OpenAI embeddings usadas pelo caminho atual do MVP local:

- `VERABRAIN_OPENAI_API_KEY`
- `VERABRAIN_OPENAI_EMBEDDING_MODEL`
- `VERABRAIN_OPENAI_BASE_URL`

Se `VERABRAIN_OPENAI_API_KEY` ficar vazio, o MVP local continua
funcionando, mas cai para retrieval lexical-only e gravações sem
embeddings.

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

O launcher do MVP local depende de:

- `mcp[cli]` para o runtime do servidor MCP
- `psycopg[binary]` para o driver Postgres
- `openai` para o runtime opcional do provider de embeddings

## 4. Iniciar o servidor MCP do VeraBrain no host

Execute o launcher do MVP local usando o arquivo `.env`:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

Esse caminho:

- lê as runtime settings explícitas
- lê as runtime settings opcionais de OpenAI embeddings
- conecta ao Postgres provisionado pelo Compose
- aplica ou verifica o schema do VeraBrain
- inicia o servidor MCP via `stdio`

Se as settings de OpenAI estiverem presentes:

- `save_memory` tenta gerar embeddings no write path
- `search_memory` e `get_context_bundle` tentam gerar embeddings de
  query

Se as settings de OpenAI estiverem ausentes ou a chamada ao provider
falhar:

- gravações duráveis continuam funcionando se o Postgres estiver
  saudável
- os metadados da memória persistida registram o fallback explícito de
  embeddings
- o retrieval volta para o comportamento bounded lexical-only

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
      VERABRAIN_OPENAI_API_KEY: "sk-..."
      VERABRAIN_OPENAI_EMBEDDING_MODEL: "text-embedding-3-small"
      VERABRAIN_OPENAI_BASE_URL: ""
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

Se OpenAI embeddings estiver configurado e saudável:

- os registros de memória salvos não devem mais persistir
  `verabrain_embedding_status=unavailable` por padrão
- queries com redação relacionada devem conseguir recall semântico
  mesmo quando o match lexical não for perfeito

Nota de compatibilidade:

- o formato canônico das tool calls MCP continua sendo argumentos
  diretos no nível raiz
- o adapter MCP do VeraBrain também tolera wrapping no formato
  `{"kwargs": {...}}` para compatibilidade com o Hermes
- essa compatibilidade existe apenas na fronteira do adapter MCP e não
  altera os contratos de aplicação do VeraBrain

## 7. Camada opcional de skill

Se você quiser que o Hermes carregue orientação procedural explícita
para uso do VeraBrain, instale também o skill do MVP:

- [Runbook do Skill Hermes VeraBrain](./hermes-verabrain-skill.pt-BR.md)

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

Resincronize o ambiente do projeto:

```bash
uv sync
```

Depois tente novamente:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

### As tool calls MCP falham porque os argumentos chegam embrulhados

O adapter MCP do VeraBrain aceita:

- argumentos diretos canônicos: `{...}`
- argumentos embrulhados por compatibilidade: `{"kwargs": {...}}`

Se o Hermes continuar falhando em uma tool call:

- confirme que você está rodando um checkout recente do `verabrain` com
  essa correção de compatibilidade
- reinicie o processo MCP do VeraBrain
- recarregue os servidores MCP do Hermes com `/reload-mcp`

### O startup do Postgres falha porque o driver está ausente

Resincronize o ambiente do projeto:

```bash
uv sync
```

Depois tente novamente:

```bash
uv run --env-file .env verabrain-mcp-local-mvp
```

### O recall semântico continua se comportando como lexical

Verifique:

- se `VERABRAIN_OPENAI_API_KEY` está presente no `.env` ou nas env vars
  do MCP no Hermes
- se `VERABRAIN_OPENAI_EMBEDDING_MODEL` aponta para um modelo de
  embedding válido
- se o processo MCP do VeraBrain foi reiniciado após mudar as env vars

Se OpenAI estiver indisponível ou mal configurado, o VeraBrain faz
fallback intencional para retrieval lexical-only.

### Os saves de memória continuam com `verabrain_embedding_status=unavailable`

Verifique:

- se a chave de API da OpenAI está configurada
- se o nome do modelo de embedding é válido
- se o processo MCP do VeraBrain consegue alcançar a API da OpenAI

Se a chamada ao provider falhar, o write path continua sobrevivente e
registra metadados explícitos de fallback em vez de quebrar o save
inteiro.
