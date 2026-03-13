# Project Foundation

## Why

O repositorio possui notas de arquitetura e artefatos basicos, mas
ainda nao registra de forma normativa:

- o stack inicial do MVP
- a metodologia de engenharia adotada
- as fronteiras arquiteturais que devem guiar os proximos slices

Sem esse alinhamento, os proximos specs e implementacoes tendem a
divergir em linguagem, tooling e estrutura modular.

## What Changes

- Definir TypeScript/Node.js/npm como stack base do MVP
- Formalizar TDD como politica obrigatoria para novas funcionalidades e
  bugfixes criticos
- Registrar boundaries entre `agent runtime`, `memory layer`,
  `tool layer` e `knowledge system`
- Atualizar `AGENTS.md` e `PROJECT_CONTEXT.md` para refletir o estado
  real do projeto
- Registrar a decisao em ADR
- Criar o scaffold inicial em TypeScript com testes, lint e type-check

## Impact

- Melhora consistencia dos proximos slices
- Reduz ambiguidade operacional
- Prepara o repositorio para o scaffold inicial sem impor implementacao
  prematura
