# ADR-0003: Revise the implementation stack for Hermes-centered VeraBrain

[Portuguese (Brazil)](./ADR-0003-python-first-hermes-stack.pt-BR.md)

## Status

Accepted

## Context

ADR-0001 established a TypeScript-first stack when VeraBrain was still
framed as a standalone agent implementation with its own runtime.

That assumption changed after the Hermes review and the decision in
ADR-0002 to reposition VeraBrain as a Hermes-centered extension
architecture.

Under that new direction, the first implementation no longer optimizes
for a custom TypeScript runtime. It optimizes for:

- integration with Hermes Agent
- MCP-first delivery
- possible future native Hermes plugin integration
- low-friction experimentation in the same ecosystem Hermes already uses

The repository already contains an initial TypeScript scaffold and those
artifacts remain useful for project bootstrapping and process
validation, but they no longer represent the preferred implementation
direction for the product itself.

## Decision

Adopt a Python-first implementation direction for the first
Hermes-centered VeraBrain version.

The revised stack direction is:

- Python 3.11+ as the primary implementation language
- `uv` as the preferred Python package and environment manager
- Hermes Agent as the runtime shell
- MCP as the primary initial integration surface
- an optional thin Hermes plugin adapter later if the native extension
  surface matures enough

The existing TypeScript/Node scaffold remains in the repository as a
legacy foundation artifact and may continue to support current local
quality checks until a Python scaffold replaces it.

## Alternatives Considered

1. Keep TypeScript as the primary implementation language despite the
   Hermes pivot
2. Use a hybrid architecture from the first implementation slice
3. Delay the stack revision until after the adapter architecture is
   designed

## Consequences

- Positives:
  - aligns the implementation language with the current Hermes-centered
    product direction
  - reduces friction for MCP integration and future thin plugin work
  - keeps architectural focus on VeraBrain core logic rather than on
    bridging two primary implementation stacks too early
  - makes the next design slices more honest about the intended delivery
    path
- Negatives/Trade-offs:
  - weakens the original TypeScript/pi-mono direction captured in
    ADR-0001
  - leaves the repository in a temporary mixed state while TypeScript
    scaffold and Python-first direction coexist
  - may require migrating or replacing local quality tooling in later
    slices

## Notes

This decision changes the preferred implementation direction, not the
core architecture principle from ADR-0002. VeraBrain should still be
structured as:

- a core domain layer
- an MCP adapter
- an optional future Hermes plugin adapter

That separation keeps future stack or integration changes cheaper.
