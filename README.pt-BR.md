# veramind

[English](./README.md)

Fundação de um agente pessoal de IA com foco em memória durável,
ferramentas explícitas e uma base consultável de conhecimento.

## Fluxo de trabalho

Este repositório usa `AGENTS.md`, `PROJECT_CONTEXT.md`, ADRs e artefatos
do OpenSpec para orientar os slices de implementação.

## Artefatos principais

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `docs/`
- `openspec/`
- `tests/`

## Documentação bilíngue

- O inglês é o idioma padrão da documentação de nível de repositório.
- `README.md` e os documentos relevantes em `docs/` possuem espelhos
  sincronizados em `pt-BR`.
- Ao editar um documento bilíngue, atualize as duas versões no mesmo
  slice.

## Setup inicial

```bash
uv sync
bash scripts/markdown-lint.sh
uv run pytest
uv run ruff check .
uv run pyright
```
