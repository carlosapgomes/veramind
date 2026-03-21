# Documentation

[Portuguese (Brazil)](./README.pt-BR.md)

This directory contains architecture decisions, release evidence, and
other durable project documents.

## Structure

- `docs/domain/`: Conceptual and domain-model documents
- `docs/adr/`: Architecture Decision Records
- `docs/runbooks/`: Practical runbooks for local and operational paths
- `docs/releases/`: Release evidence and release-oriented notes

Current runbooks:

- `local-mvp.md`
- `hermes-verabrain-skill.md`

## Bilingual Rule

- English documents are the default source.
- Every relevant English document in `docs/` must have a synchronized
  `pt-BR` mirror next to it.
- Any change to a bilingual document must update both language versions
  in the same slice.
