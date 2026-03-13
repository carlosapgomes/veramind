# PROJECT_CONTEXT.md

## Proposito

Resumo executivo para retomada rapida apos pausas e para onboarding de novos contribuidores.

## Fontes Autoritativas

- `AGENTS.md`
- `openspec/specs/`
- `openspec/changes/`
- `docs/adr/`
- `docs/releases/`
- `texts/personal_agent_architecture_notes.md`
- Em caso de conflito: specs/artefatos mais recentes no Git prevalecem.

## Objetivo do Sistema

Construir um agente pessoal de IA ("Second Brain / Personal OS") com
memoria duravel, ferramentas explicitas e base consultavel de
conhecimento.

O sistema deve ajudar o usuario a:

- preservar contexto de longo prazo
- recuperar informacoes relevantes no momento certo
- executar fluxos orientados por ferramentas com seguranca
- evoluir de forma incremental, com arquitetura simples e observavel

## Arquitetura de Alto Nivel

- **agent runtime**: Orquestracao do agente, prompts, contexto e
  chamada de ferramentas.
- **memory layer**: Memoria duravel sobre usuario, preferencias,
  decisoes e projetos ativos.
- **tool layer**: Ferramentas explicitas e wrappers controlados para
  capacidades do agente.
- **knowledge system**: Base consultavel de documentos, notas e referencias.
- **docs** (docs): Documentacao e rastreabilidade.
- **scripts** (scripts): Automacoes e utilitarios.
- **tests** (tests): Suite de testes automatizados.

Direcao de dependencias desejada:

- `agent runtime -> memory/tool/knowledge contracts`
- `tool layer -> adapters externos`
- sem dependencia reversa para o runtime

Stack inicial acordado:

- TypeScript
- Node.js 22 LTS
- npm
- Vitest
- ESLint + Prettier
- Postgres + pgvector como alvo de persistencia
- pi-mono como runtime de agente pretendido

Estado atual do projeto:

- Fase de fundacao e definicao de especificacoes
- Scaffold inicial de aplicacao TypeScript criado
- Boundaries arquiteturais iniciais codificadas em modulo testado

## Regras Nao Negociaveis

- Nao quebrar contratos publicos de API sem mudanca versionada.
- Toda mudanca relevante deve deixar evidencia no Git (spec/task/commit).
- Manter boundaries explicitos entre runtime, memoria, ferramentas e
  conhecimento.
- Preferir wrappers controlados a acesso irrestrito ao shell.
- Priorizar simplicidade e capacidade de iteracao sobre arquitetura prematura.

## Quality Bar

- Testes relevantes executam localmente antes de merge.
- Lint e checks estaticos sem erros criticos.
- Mudancas com risco medio/alto devem ter plano de rollback.
- Novas funcionalidades e bugfixes criticos seguem TDD.
- Documentacao operacional deve refletir o estado real do repositorio.

## Proximos Slices Provaveis

- Especificacao da camada de memoria
- ADRs complementares para boundaries, persistencia e modelo de
  ferramentas

<!-- generated-by: project-context-maintainer -->
