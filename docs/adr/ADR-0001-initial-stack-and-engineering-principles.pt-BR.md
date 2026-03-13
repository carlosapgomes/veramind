# ADR-0001: Stack inicial e princípios de engenharia

[English](./ADR-0001-initial-stack-and-engineering-principles.md)

## Status

Accepted

## Contexto

O projeto está em sua fase de fundação. As notas iniciais de
arquitetura definem quatro blocos principais: `agent runtime`,
`memory layer`, `tool layer` e `knowledge system`.

Antes de detalhar funcionalidades do produto, o repositório precisa de
uma base técnica e metodológica consistente para:

- reduzir atrito na implementação do MVP
- alinhar o stack com o runtime de agente pretendido (`pi-mono`)
- garantir boundaries modulares claras
- reforçar TDD e rastreabilidade desde o início

## Decisão

Padronizar o MVP em:

- TypeScript como linguagem principal
- Node.js 22 LTS como runtime
- npm como gerenciador de pacotes
- Vitest para testes
- ESLint e Prettier para qualidade e formatação de código
- markdownlint-cli para validação da documentação

Também ficam estabelecidos os seguintes princípios de engenharia:

- aplicar TDD em novas funcionalidades e bug fixes críticos
- preservar boundaries explícitas entre `agent runtime`, `memory layer`,
  `tool layer` e `knowledge system`
- manter dependências unidirecionais, sem acoplamento reverso ao
  runtime
- expor capacidades do agente por ferramentas explícitas e wrappers
  controlados
- priorizar simplicidade, observabilidade e iteração rápida no MVP

Como decisão arquitetural de alvo, a persistência inicial planejada para
memória e conhecimento é Postgres com suporte a `pgvector`.

## Alternativas consideradas

1. Python como linguagem principal do MVP
2. Arquitetura híbrida com TypeScript + Python desde o primeiro slice
3. Adiar a decisão de stack até o primeiro protótipo funcional

## Consequências

- Positivas:
  - reduz atrito com o runtime `pi-mono`
  - unifica a base de código do MVP em uma única linguagem
  - acelera a criação de testes, ferramentas e contratos de módulo
  - torna operacionais as políticas de qualidade documentadas em
    `AGENTS.md`
- Negativas/Trade-offs:
  - componentes futuros orientados a ML ainda podem exigir integração
    com Python
  - a equipe fica inicialmente mais acoplada ao ecossistema Node.js
  - Postgres é escolhido cedo, antes de benchmarking local
