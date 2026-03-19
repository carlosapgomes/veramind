# Spec: Implementation Direction Realignment

## Status

Proposed

## Requirements

### Requirement: Use Python as the primary implementation direction

The project MUST treat Python 3.11+ as the primary implementation
direction for the first Hermes-centered VeraBrain version.

#### Scenario: Contributor reads the current stack guidance

- **WHEN** a contributor reads the repository's operational and context
  artifacts
- **THEN** those artifacts identify Python as the preferred
  implementation direction for the Hermes-centered path

### Requirement: Preserve the meaning of the existing TypeScript scaffold

The project MUST distinguish between the existing repository scaffold and
the current product implementation direction.

#### Scenario: Contributor inspects the repository toolchain

- **WHEN** a contributor sees TypeScript, npm, and Vitest artifacts in
  the repository
- **THEN** the documentation clarifies that those artifacts are existing
  repository scaffolding rather than the primary product direction

### Requirement: Align the roadmap with the new direction

The project MUST update roadmap and planning artifacts to reflect the
Hermes-centered Python-first path.

#### Scenario: Contributor looks for the next recommended slice

- **WHEN** a contributor reviews project planning artifacts
- **THEN** the next recommended slice is architecture design for the
  VeraBrain core and adapters, not a continuation of the old standalone
  runtime path
