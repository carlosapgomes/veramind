# VeraBrain Core and Adapter Architecture

## Why

The repository now has accepted ADRs for the Hermes-centered and
Python-first direction, but it still lacks a normative architecture
slice that explains how VeraBrain should be divided internally.

Without this boundary definition, future implementation work could:

- leak MCP or Hermes-specific concerns into VeraBrain core logic
- mix memory, knowledge, and execution into one model
- hard-code GTD into the base domain instead of keeping it optional
- make future migration from MCP-first to a native Hermes plugin
  expensive

## What Changes

- Define VeraBrain as a core domain plus adapter architecture
- Specify the boundary between the VeraBrain core and Hermes-facing
  adapters
- Separate the domain between memory, knowledge items, execution, and
  the optional GTD-inspired workflow layer
- Define the initial application contracts that Hermes integrations
  should call
- Clarify which responsibilities belong to the core versus the
  integration layer

## Impact

- Gives the next Python implementation slices a stable architectural
  target
- Protects the VeraBrain core from MCP- and Hermes-specific coupling
- Preserves a future path from MCP-first delivery to native Hermes
  plugin integration without rewriting the core
