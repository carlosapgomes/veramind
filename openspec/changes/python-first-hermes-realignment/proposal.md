# Python-First Hermes Realignment

## Why

The repository foundation artifacts and the temporary Node/TypeScript
scaffold still reflect the earlier standalone direction, while the
current strategic direction is a Hermes-centered VeraBrain with
MCP-first integration.

Without a formal stack realignment, future slices will continue to
inherit conflicting assumptions about implementation language, runtime
context, and whether the temporary Node/TypeScript scaffold is still a
live part of the product path.

## What Changes

- Record Python 3.11+ as the primary implementation direction for the
  Hermes-centered VeraBrain path
- Retire the temporary TypeScript/Node scaffold once the Python
  foundation becomes runnable
- Update operational and context artifacts to reflect the new stack
  stance
- Adjust the roadmap so the next slice focuses on core-and-adapter
  design instead of continuing the old standalone path

## Impact

- Makes repository guidance internally consistent again
- Prevents the next architecture slice from being framed around the old
  standalone runtime assumption
- Completes the transition from temporary Node scaffolding to the
  Python-first implementation path
