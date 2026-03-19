# Python-First Hermes Realignment

## Why

The repository foundation artifacts still reflect the earlier
TypeScript-first standalone direction, while the current strategic
direction is a Hermes-centered VeraBrain with MCP-first integration.

Without a formal stack realignment, future slices will continue to
inherit conflicting assumptions about implementation language, runtime
context, and the meaning of the existing TypeScript scaffold.

## What Changes

- Record Python 3.11+ as the primary implementation direction for the
  Hermes-centered VeraBrain path
- Clarify that the existing TypeScript scaffold is a legacy foundation
  artifact, not the main product direction
- Update operational and context artifacts to reflect the new stack
  stance
- Adjust the roadmap so the next slice focuses on core-and-adapter
  design instead of continuing the old standalone path

## Impact

- Makes repository guidance internally consistent again
- Prevents the next architecture slice from being framed around the old
  standalone runtime assumption
- Preserves a clear transition path from existing repository scaffold to
  future Python implementation work
