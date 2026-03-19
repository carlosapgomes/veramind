# ADR-0001: Initial stack and engineering principles

[Portuguese (Brazil)](./ADR-0001-initial-stack-and-engineering-principles.pt-BR.md)

## Status

Superseded by ADR-0003

## Context

The project is in its foundation phase. The initial architecture notes
define four main building blocks: `agent runtime`, `memory layer`,
`tool layer`, and `knowledge system`.

Before detailing product functionality, the repository needs a
consistent technical and methodological base to:

- reduce friction for MVP implementation
- align the stack with the intended agent runtime (`pi-mono`)
- guarantee clear modular boundaries
- reinforce TDD and traceability from the start

## Decision

Standardize the MVP on:

- TypeScript as the primary language
- Node.js 22 LTS as the runtime
- npm as the package manager
- Vitest for testing
- ESLint and Prettier for code quality and formatting
- markdownlint-cli for documentation validation

The following engineering principles are also established:

- apply TDD to new features and critical bug fixes
- preserve explicit boundaries between `agent runtime`, `memory layer`,
  `tool layer`, and `knowledge system`
- keep dependencies unidirectional, without reverse coupling into the
  runtime
- expose agent capabilities through explicit tools and controlled
  wrappers
- prioritize simplicity, observability, and fast iteration in the MVP

As a target architectural decision, the planned initial persistence
layer for memory and knowledge is Postgres with `pgvector` support.

## Alternatives Considered

1. Python as the MVP primary language
2. A hybrid TypeScript + Python architecture from the first slice
3. Delaying the stack decision until the first functional prototype

## Consequences

- Positives:
  - reduces friction with the `pi-mono` runtime
  - unifies the MVP codebase under one language
  - accelerates the creation of tests, tools, and module contracts
  - makes the quality policies documented in `AGENTS.md` operational
- Negatives/Trade-offs:
  - future ML-oriented components may still require Python integration
  - the team becomes initially more coupled to the Node.js ecosystem
  - Postgres is chosen early, before local benchmarking exists
