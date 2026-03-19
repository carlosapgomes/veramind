# Spec: Project Foundation

## Status

Proposed

## Requirements

### Requirement: Standardize the MVP stack

The project MUST standardize the MVP application stack on Python 3.11+
using `uv` as the default package and environment manager.

#### Scenario: Contributor checks the official stack

- **WHEN** a contributor reads the project operational artifacts
- **THEN** the selected language, runtime and package manager are
  documented consistently

### Requirement: Document engineering quality practices

The project MUST document TDD, validation commands and quality
expectations in the repository operational artifacts.

#### Scenario: Contributor prepares a new slice

- **WHEN** a contributor starts a feature or critical bugfix
- **THEN** the artifacts instruct them to apply TDD and run the
  documented validation commands

### Requirement: Preserve architectural boundaries

The project MUST document the intended separation between `agent
runtime`, `memory layer`, `tool layer` and `knowledge system`,
including the desired unidirectional dependency flow.

#### Scenario: Contributor defines a new module

- **WHEN** a contributor plans or implements a new module
- **THEN** the project artifacts provide the expected architectural
  boundary and dependency direction

### Requirement: Keep foundational decisions traceable

The project MUST record foundational technical decisions in versioned
repository artifacts.

#### Scenario: Contributor needs the rationale for the selected stack

- **WHEN** a contributor reviews architectural decisions
- **THEN** an ADR and project context documents explain the selected
  stack and principles

### Requirement: Provide a runnable Python scaffold

The project MUST provide a minimal runnable scaffold in Python with
working test, lint, type-check, and markdown validation commands.

#### Scenario: Contributor validates the local scaffold

- **WHEN** a contributor runs the documented Python validation
  commands
- **THEN** the repository provides `bash scripts/markdown-lint.sh`,
  `uv run pytest`, `uv run ruff check .`, and `uv run pyright`
  successfully

### Requirement: Encode the initial module dependency rules

The project MUST codify the initial architectural dependency direction
between the core system modules in a tested Python module.

#### Scenario: Contributor checks dependency direction

- **WHEN** a contributor inspects the architecture boundary module
- **THEN** the allowed dependency direction from `agent runtime` to the
  other core modules is explicit and covered by unit tests
