# ADR-0001: Stack inicial e principios de engenharia

## Status

Accepted

## Contexto

O projeto esta na fase de fundacao. As notas iniciais de arquitetura
definem quatro blocos principais do sistema: `agent runtime`,
`memory layer`, `tool layer` e `knowledge system`.

Antes de detalhar funcionalidades, o repositorio precisa de uma base
tecnica e metodologica consistente para:

- reduzir atrito na implementacao do MVP
- alinhar o stack com o runtime de agente pretendido (`pi-mono`)
- garantir fronteiras modulares claras
- reforcar TDD e rastreabilidade desde o inicio

## Decisao

Padronizar o MVP em:

- TypeScript como linguagem principal
- Node.js 22 LTS como runtime
- npm como gerenciador de pacotes
- Vitest para testes
- ESLint e Prettier para qualidade de codigo e formatacao
- markdownlint-cli para validacao da documentacao

Tambem ficam estabelecidos os seguintes principios de engenharia:

- aplicar TDD em novas funcionalidades e bugfixes criticos
- preservar boundaries explicitos entre `agent runtime`, `memory layer`,
  `tool layer` e `knowledge system`
- manter dependencias unidirecionais, sem acoplamento reverso ao runtime
- expor capacidades do agente por ferramentas explicitas e wrappers
  controlados
- priorizar simplicidade, observabilidade e iteracao rapida no MVP

Como decisao arquitetural de alvo, a persistencia inicial planejada
para memoria e conhecimento e Postgres com suporte a `pgvector`.

## Alternativas Consideradas

1. Python como linguagem principal do MVP
2. Arquitetura hibrida inicial com TypeScript + Python desde o primeiro
   slice
3. Adiar a decisao de stack ate o primeiro prototipo funcional

## Consequencias

- Positivas:
  - reduz atrito com o runtime `pi-mono`
  - unifica a base de codigo do MVP em uma unica linguagem
  - acelera a criacao de testes, ferramentas e contratos de modulo
  - torna operacionais as politicas de qualidade documentadas em
    `AGENTS.md`
- Negativas/Trade-offs:
  - componentes futuros mais orientados a ML podem exigir integracao
    com Python
  - a equipe fica inicialmente mais acoplada ao ecossistema Node.js
  - a persistencia em Postgres fica decidida cedo, ainda sem benchmark
    local
