# ADR-0006: Estabelecer os limites da política de retrieval do VeraBrain

[English](./ADR-0006-establish-retrieval-policy-boundaries.md)

## Status

Accepted

## Contexto

O VeraBrain deve complementar a memória do Hermes, e não substituí-la.
Isso só funciona se o retrieval do VeraBrain permanecer bounded,
explícito e arquiteturalmente separado tanto das preocupações de
transporte quanto dos detalhes de tecnologia de armazenamento.

O repositório agora tem:

- contratos de aplicação para retrieval bounded de contexto
- mappings MCP que serializam contexto agrupado de volta para o Hermes
- um adaptador em memória que já consegue exercitar comportamento de
  consulta determinístico

Antes de implementar o adaptador Postgres e uma lógica de retrieval mais
rica, o projeto precisa de uma decisão estável sobre qual política de
retrieval pertence ao core e o que continua sendo uma preocupação de
infraestrutura.

## Decisão

Adotar os seguintes limites de política de retrieval para o VeraBrain:

- retrieval é uma preocupação do core do VeraBrain, não do MCP
- os resultados de retrieval devem sempre ser bounded por limites
  explícitos carregados nas requests de aplicação ou nos objetos de
  query dos repositórios
- retrieval pode combinar sinais lexicais, estruturais, de salience,
  temporais e apoiados por embeddings
- o algoritmo exato de ranking é implementation-defined e pode evoluir
  sem mudar os contratos da aplicação
- adapters podem pedir contexto, mas não devem ser donos da política de
  ranking nem das heurísticas de retrieval

A direção prática inicial é:

- comportamento determinístico lexical e baseado em filtros no
  adaptador em memória
- retrieval híbrido no futuro adaptador Postgres, com `pgvector`
  disponível para recall semântico
- saída agrupada por memória, conhecimento e execução em vez de um
  único pool indiferenciado de resultados

## Alternativas Consideradas

1. Manter o retrieval principalmente dentro de adapters MCP ou voltados
   ao Hermes
2. Travar agora uma única fórmula fixa de scoring
3. Definir retrieval como uma política do core, com contratos
   adapter-neutral e detalhes de ranking específicos da implementação

## Consequências

- Positivas:
  - preserva a arquitetura core mais adapters também no retrieval
  - permite melhorar ranking e recall sem quebrar contratos públicos
  - mantém as integrações com Hermes focadas em pedir contexto bounded,
    em vez de reimplementar o comportamento de memória
  - evita colapsar memória, conhecimento e execução em um único formato
    genérico de resultado de busca
- Negativas/Trade-offs:
  - deixa detalhes de ranking para specs e implementações posteriores
  - exige disciplina para que adapters de infraestrutura não vazem
    premissas de scoring para cima
  - pode criar diferenças temporárias entre a qualidade do retrieval em
    memória e o retrieval apoiado por Postgres

## Notas

Esta ADR fixa deliberadamente os limites, não um algoritmo final. Uma
spec posterior pode definir detalhes do retrieval híbrido, como geração
de embeddings, seleção de candidatos, reranking e ponderação de
freshness.
