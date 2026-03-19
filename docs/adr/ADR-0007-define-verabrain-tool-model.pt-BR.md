# ADR-0007: Definir o modelo de ferramentas do VeraBrain

[English](./ADR-0007-define-verabrain-tool-model.md)

## Status

Accepted

## Contexto

O VeraBrain agora tem uma superfície inicial de ferramentas MCP e um
adaptador que despacha essas chamadas de ferramenta para serviços de
aplicação.

Antes de expandir essa superfície ou adicionar um futuro adaptador
nativo do Hermes, o projeto precisa de uma decisão estável sobre como
uma capability do VeraBrain deve se apresentar na fronteira de
ferramentas.

Sem essa decisão, existe o risco de derivar para:

- ferramentas moldadas pelo armazenamento
- semântica de ferramenta específica de transporte
- workflows específicos de GTD tratados como identidade do produto
- ferramentas amplas e genéricas com fronteiras de domínio fracas

## Decisão

Adotar um modelo de ferramentas orientado a domínio para o VeraBrain,
com contratos explícitos e bounded.

As regras do modelo são:

- ferramentas expõem capabilities de domínio, não primitivas cruas de
  armazenamento
- os agrupamentos principais de ferramentas continuam sendo memória,
  conhecimento, execução, contexto bounded e workflows orientados à
  revisão
- comportamento inspirado em GTD pode existir, mas deve ficar em cima
  de execução e conhecimento em vez de redefinir o modelo do core
- nomes de ferramentas, schemas JSON e bindings de transporte ficam
  dentro dos adapters
- contratos de aplicação permanecem como a fronteira estável e
  adapter-neutral
- integrações nativas futuras com Hermes devem reutilizar os mesmos
  contratos de aplicação em vez de inventar uma interface de negócio
  separada

As ferramentas não devem, por padrão, expor:

- acesso irrestrito ao shell
- superfícies diretas de SQL ou mutação de persistência
- endpoints genéricos de "faça qualquer coisa com meu second brain"
- premissas específicas de transporte embutidas nos serviços do core

## Alternativas Consideradas

1. Deixar nomes e payloads de ferramentas MCP virarem a interface de
   facto do core
2. Expor diretamente como ferramentas primitivas mais baixas de
   armazenamento e retrieval
3. Manter um modelo de ferramentas orientado a domínio sobre contratos
   estáveis de aplicação

## Consequências

- Positivas:
  - mantém a superfície de ferramentas compreensível e evoluível
  - preserva a separação clara entre comportamento do core e detalhes de
    transporte do adapter
  - reduz a chance de acoplar futuro trabalho de plugin Hermes à
    nomenclatura do MCP
  - reforça que GTD é uma camada opcional de workflow, e não a
    identidade definidora do VeraBrain
- Negativas/Trade-offs:
  - exige algum código de tradução nos adapters em vez de expor
    diretamente primitivas de nível mais baixo
  - restringe experimentação com formatos ad hoc de ferramentas
  - significa que novas capabilities normalmente devem ser adicionadas
    via contratos e serviços antes de serem expostas como ferramentas

## Notas

Esta ADR não congela para sempre o catálogo exato das primeiras
ferramentas. Ela fixa a regra de desenho de que ferramentas do VeraBrain
são wrappers orientados a domínio sobre contratos de aplicação, e não o
centro arquitetural do sistema.
