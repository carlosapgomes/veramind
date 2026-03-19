# ADR-0005: Adotar uma arquitetura de persistência com Postgres e pgvector

[English](./ADR-0005-adopt-postgres-pgvector-persistence-architecture.md)

## Status

Accepted

## Contexto

A ADR-0002 posicionou o VeraBrain como um subsistema centrado no Hermes
com o core mantido separado do MCP e de qualquer adaptador Hermes
nativo futuro.

Desde então, o repositório ganhou:

- ports explícitos de repositório e unit of work
- um adaptador inicial de infraestrutura em memória
- serviços de aplicação chamáveis sobre a camada de ports

Isso significa que a fronteira arquitetural de persistência agora está
estável o suficiente para travar a direção de persistência de produção
antes de construir o adaptador concreto de banco de dados.

O projeto já carrega Postgres e `pgvector` como alvo pretendido, mas
essa escolha ainda precisava de uma ADR aceita explicando como essas
tecnologias se encaixam na arquitetura atual de core mais adapters.

## Decisão

Adotar Postgres com `pgvector` como a arquitetura-alvo de persistência
de produção do VeraBrain.

Isso significa:

- Postgres é o system of record para memória, conhecimento, execução e
  links explícitos de conhecimento
- `pgvector` é a extensão planejada para busca vetorial apoiada por
  embeddings
- a implementação em Postgres ficará em adapters de infraestrutura e
  cumprirá os ports existentes de repositório e unit of work da camada
  de aplicação
- a camada de aplicação continuará adapter-neutral e não exporá SQL,
  nomes de tabela, detalhes de migração nem preocupações de
  `pgvector` em seus contratos públicos

O adaptador em memória continua útil para testes e composição local, mas
não é o caminho alvo de persistência de produção.

## Alternativas Consideradas

1. Manter apenas o adaptador em memória no curto prazo
2. Adotar SQLite como o primeiro backend durável de persistência
3. Adotar Postgres com `pgvector` como baseline de persistência durável

## Consequências

- Positivas:
  - alinha com o alvo de persistência de longo prazo já declarado
  - suporta armazenamento relacional estruturado e retrieval com vetores
    na mesma plataforma de persistência
  - encaixa na arquitetura atual baseada em repository ports sem mudar
    os contratos da aplicação
  - mantém separados os adapters locais/de teste e o armazenamento de
    produção
- Negativas/Trade-offs:
  - aumenta a complexidade operacional em comparação com um caminho só
    em memória ou com SQLite
  - exige migrações, desenho de schema e disciplina de indexação
  - cria uma dependência mais forte de setup de infraestrutura antes que
    os fluxos end-to-end de persistência possam ser exercitados em forma
    de produção

## Notas

Esta ADR escolhe a arquitetura-alvo de persistência. Ela ainda não
define o schema final, a fórmula de scoring de retrieval nem o plano de
migração. Esses detalhes devem continuar em specs e slices de
implementação.
