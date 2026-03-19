# ADR-0007: Define the VeraBrain tool model

[Portuguese (Brazil)](./ADR-0007-define-verabrain-tool-model.pt-BR.md)

## Status

Accepted

## Context

VeraBrain now has an initial MCP tool surface and an adapter that
dispatches those tool calls into application services.

Before expanding that surface or adding a future Hermes-native adapter,
the project needs a stable decision about what a VeraBrain capability
looks like at the tool boundary.

Without that decision, there is a risk of drifting into:

- storage-shaped tools
- transport-specific tool semantics
- GTD-specific workflows treated as the product identity
- broad catch-all tools with weak domain boundaries

## Decision

Adopt a domain-oriented VeraBrain tool model with explicit bounded
contracts.

The tool model rules are:

- tools expose domain capabilities, not raw storage primitives
- the primary tool groupings remain memory, knowledge, execution,
  bounded context, and review-oriented workflows
- GTD-inspired behavior may exist, but it must sit on top of execution
  and knowledge instead of redefining the core model
- tool names, JSON schemas, and transport bindings stay inside adapters
- application contracts remain the stable adapter-neutral boundary
- future Hermes-native integrations must reuse the same application
  contracts instead of inventing a separate business interface

Tools must not default to:

- unrestricted shell access
- direct SQL or persistence mutation surfaces
- generic "do anything with my second brain" endpoints
- transport-specific assumptions embedded in core services

## Alternatives Considered

1. Let MCP tool names and payloads become the de facto core interface
2. Expose lower-level storage and retrieval primitives directly as tools
3. Keep a domain-oriented tool model over stable application contracts

## Consequences

- Positives:
  - keeps the tool surface understandable and evolvable
  - preserves clear separation between core behavior and adapter
    transport details
  - reduces the chance of coupling future Hermes plugin work to MCP
    naming
  - reinforces that GTD is an optional workflow layer rather than the
    defining identity of VeraBrain
- Negatives/Trade-offs:
  - requires some translation code in adapters instead of exposing
    lower-level primitives directly
  - constrains experimentation with ad hoc tool shapes
  - means new capabilities should usually be added through contracts and
    services before being surfaced as tools

## Notes

This ADR does not freeze the exact first tool catalog forever. It fixes
the design rule that VeraBrain tools are domain-facing wrappers over
application contracts, not the architectural center of the system.
