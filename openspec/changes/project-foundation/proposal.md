# Project Foundation

## Why

The repository contains architecture notes and basic artifacts, but it
does not yet record the following in a normative way:

- the initial MVP stack
- the adopted engineering methodology
- the architectural boundaries that should guide the next slices

Without that alignment, future specs and implementations tend to diverge
in language, tooling, and modular structure.

## What Changes

- Define TypeScript/Node.js/npm as the MVP base stack
- Formalize TDD as a required policy for new features and critical bug
  fixes
- Record boundaries between `agent runtime`, `memory layer`,
  `tool layer`, and `knowledge system`
- Update `AGENTS.md` and `PROJECT_CONTEXT.md` to reflect the actual
  project state
- Record the decision in an ADR
- Create the initial TypeScript scaffold with test, lint, and
  type-check support

## Impact

- Improves consistency for future slices
- Reduces operational ambiguity
- Prepares the repository for the initial scaffold without forcing
  premature implementation
