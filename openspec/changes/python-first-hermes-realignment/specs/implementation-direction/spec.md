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

### Requirement: Retire the temporary TypeScript scaffold

Once the Python scaffold is runnable, the project MUST retire the
temporary TypeScript/Node scaffold instead of keeping two primary
repository foundations in parallel.

#### Scenario: Contributor inspects the repository toolchain

- **WHEN** a contributor inspects the repository after the Python
  foundation exists
- **THEN** the repository tooling centers on Python and `uv`
- **AND** the temporary TypeScript/Node scaffold is no longer required

### Requirement: Align the roadmap with the new direction

The project MUST update roadmap and planning artifacts to reflect the
Hermes-centered Python-first path.

#### Scenario: Contributor looks for the next recommended slice

- **WHEN** a contributor reviews project planning artifacts
- **THEN** the next recommended slice is architecture design for the
  VeraBrain core and adapters, not a continuation of the old standalone
  runtime path
