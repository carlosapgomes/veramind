# veramind

[Portuguese (Brazil)](./README.pt-BR.md)

Personal AI agent foundation focused on durable memory, explicit tools,
and a consultable knowledge base.

## Workflow

This repository uses `AGENTS.md`, `PROJECT_CONTEXT.md`, ADRs, and
OpenSpec artifacts to guide implementation slices.

## Main Artifacts

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `docs/`
- `openspec/`
- `tests/`

## Bilingual Documentation

- English is the default language for repository-level documentation.
- `README.md` and the relevant documents under `docs/` have synchronized
  `pt-BR` mirrors.
- When editing a bilingual document, update both language versions in
  the same slice.

## Initial Setup

```bash
uv sync
bash scripts/markdown-lint.sh
uv run pytest
uv run ruff check .
uv run pyright
```
