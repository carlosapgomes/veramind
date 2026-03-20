# Memory Loop MVP

## Why

VeraBrain now has a solid architectural baseline: core/application
boundaries, MCP adapter surfaces, Postgres persistence adapters, hybrid
retrieval, and a completed memory write pipeline with embedding support.

What is still missing is a single explicit change that defines the
minimum observable behavior VeraBrain must deliver end to end before the
project expands into broader operational hardening, richer knowledge
modeling, or execution workflows.

Without this MVP change, the roadmap risks expanding laterally across:

- Postgres operational hardening before the main user-visible loop is
  proven
- knowledge and semantic-link ambition before the memory loop shows
  clear value
- execution and GTD-inspired workflows before durable memory improves
  the Hermes-centered agent experience

## What Changes

- Define the observable MVP behavior for the first VeraBrain memory loop
- Treat the MVP as a vertical slice that crosses the relevant layers of
  the system
- Make the initial happy-path and fallback-path scenarios explicit
- Define the minimum bounded retrieval behavior VeraBrain must expose to
  Hermes through MCP
- Record the next implementation-oriented slices required to prove that
  end-to-end loop

## Non-Goals

- Production-grade Postgres operational hardening
- A full policy for Hermes memory versus VeraBrain memory authority
- Broad knowledge graph modeling or ambitious semantic ontology work
- Execution workflows, GTD-specific behavior, or planning UX
- A native Hermes plugin evaluation beyond MCP-first integration

## Impact

- Establishes the first product-level definition of done for VeraBrain,
  not only the architectural one
- Keeps the roadmap focused on proving observable user value before
  broadening scope
- Creates a clean prerequisite for the later
  `hermes-verabrain-memory-boundary` and `memory-loop-e2e-integration`
  changes
