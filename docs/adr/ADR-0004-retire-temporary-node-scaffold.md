# ADR-0004: Retire the temporary TypeScript and Node repository scaffold

[Portuguese (Brazil)](./ADR-0004-retire-temporary-node-scaffold.pt-BR.md)

## Status

Accepted

## Context

ADR-0003 kept the existing TypeScript and Node scaffold in the
repository as a temporary transition artifact while the Python-first
Hermes-centered direction was still being established.

That transition condition no longer holds:

- the Python package skeleton now exists under `src/verabrain`
- the repository quality gate can run through `uv`
- the architectural boundary checks now exist in Python

Keeping the temporary Node scaffold after that point would leave the
repository with two competing foundations and would continue to signal
that the old standalone path is still active.

## Decision

Retire the temporary TypeScript and Node repository scaffold.

This includes:

- removing the TypeScript boundary module and its tests
- removing `package.json`, `package-lock.json`, `tsconfig.json`,
  `vitest.config.ts`, and Node-specific lint configuration
- replacing Node-based repository quality commands with Python and `uv`
  commands
- moving markdown validation and formatting to `uv`-managed Python tools

The Hermes-centered, Python-first direction from ADR-0003 remains in
force. This ADR only closes the temporary coexistence period.

## Alternatives Considered

1. Keep the temporary Node scaffold indefinitely
2. Keep Node only for repository tooling such as markdown validation
3. Retire the scaffold and update the repository to a Python-only
   foundation

## Consequences

- Positives:
  - removes mixed-stack ambiguity from the repository
  - simplifies the quality gate and contributor onboarding
  - makes the repository state match the accepted product direction
  - reduces maintenance of duplicate boundary tests and tooling
- Negatives/Trade-offs:
  - removes the old Node-based fallback path
  - requires Python equivalents for repository tooling such as markdown
    validation
  - makes future TypeScript use a deliberate reintroduction instead of a
    leftover default

## Notes

This decision does not change the architecture principle from ADR-0002
or the Python-first Hermes direction from ADR-0003. It only retires the
temporary repository scaffolding that existed during the transition.
