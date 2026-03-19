# ADR-0002: Position VeraBrain as a Hermes extension

[Portuguese (Brazil)](./ADR-0002-verabrain-as-hermes-extension.pt-BR.md)

## Status

Proposed

## Context

VeraBrain was initially framed as a standalone personal agent system with
its own runtime, memory layer, tool layer, and knowledge system.

After reviewing Hermes Agent, it is clear that Hermes already provides a
large part of the infrastructure VeraBrain would otherwise need to build
from scratch:

- agent loop and tool-calling runtime
- terminal and messaging interfaces
- tool registry and plugin system
- MCP support for external tool ecosystems
- bounded persistent memory via `MEMORY.md` and `USER.md`
- session recall via SQLite + `session_search`
- procedural memory via skills
- optional Honcho-based cross-session user modeling

At the same time, Hermes does not fully cover the intended VeraBrain use
case. Its built-in memory is intentionally bounded and prompt-oriented,
while the desired VeraBrain capability is closer to a second-brain and
personal knowledge system with richer retrieval, durable knowledge
objects, and a broader corpus than curated prompt memory.

## Decision

Reposition VeraBrain from a standalone agent implementation to a
Hermes-centered extension architecture.

The default direction is:

- Hermes Agent as the runtime and user-facing agent shell
- VeraBrain as a complementary second-brain and personal knowledge
  subsystem
- an MCP server as the primary integration surface between Hermes and
  VeraBrain
- an optional thin Hermes plugin for UX improvements, setup helpers, or
  bundled skills when needed

The VeraBrain business logic must stay outside the integration layer.
MCP is the initial adapter, not the architectural center of the system.

VeraBrain should complement Hermes memory rather than replace it:

- Hermes built-in memory remains the hot, bounded, prompt-injected layer
- Hermes skills remain the procedural memory layer
- Hermes session search remains transcript recall
- Honcho remains optional user modeling
- VeraBrain becomes the long-term personal knowledge and second-brain
  layer

## Alternatives Considered

1. Continue building VeraBrain as a standalone agent from scratch
2. Build VeraBrain as a Hermes-native plugin only
3. Build VeraBrain as an MCP-first subsystem with an optional thin
   plugin layer

## Consequences

- Positives:
  - avoids rebuilding agent infrastructure that Hermes already provides
  - accelerates time to a usable personal system
  - preserves a clean conceptual split between hot memory and long-term
    knowledge
  - keeps VeraBrain reusable outside Hermes by centering integration on
    MCP
  - reduces coupling to undocumented Hermes internals compared with a
    deep plugin-only approach
  - preserves a low-friction migration path from MCP integration to a
    native Hermes plugin or hook-based integration later
- Negatives/Trade-offs:
  - shifts the implementation center from the original TypeScript-first
    direction toward a Hermes/Python ecosystem
  - introduces dependency on Hermes project evolution and extension
    points
  - may still require a thin compatibility layer if Hermes plugin hooks
    are needed beyond tool registration
  - requires careful UX design so Hermes memory, Honcho, skills, and
    VeraBrain do not overlap confusingly

## Notes

The Hermes plugin system is mature enough for adding tools, but its
documented lifecycle hooks appear broader than the hooks currently
invoked in the runtime. That makes MCP the safer primary integration
surface for the first VeraBrain-on-Hermes version.

To preserve future migration flexibility, VeraBrain should be split into
layers:

- a core memory and knowledge engine that owns data models, persistence,
  classification, retrieval, and ranking
- a thin MCP adapter that exposes those capabilities as tools
- an optional thin Hermes plugin adapter for future direct integration

With that structure, a later move from MCP-first integration to native
plugin or hook-based integration should only require replacing the
adapter layer rather than rewriting the VeraBrain core.
