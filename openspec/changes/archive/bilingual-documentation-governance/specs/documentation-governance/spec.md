# Spec: Documentation Governance

## Status

Proposed

## Requirements

### Requirement: Use English as the default language

The project MUST use American English as the default language for
normative repository artifacts.

#### Scenario: Contributor edits a normative artifact

- **WHEN** a contributor updates `AGENTS.md`, `PROJECT_CONTEXT.md`,
  active ADRs, or active OpenSpec artifacts
- **THEN** the updated artifact is written in American English

### Requirement: Maintain bilingual mirrors for primary documentation

The project MUST maintain synchronized Brazilian Portuguese mirrors for
`README.md` and relevant documents under `docs/`.

#### Scenario: Contributor edits a bilingual document

- **WHEN** a contributor changes a bilingual English document
- **THEN** the paired `pt-BR` mirror is updated in the same slice

### Requirement: Cross-link bilingual document pairs

Each bilingual English document MUST link to its `pt-BR` mirror at the
top of the file.

#### Scenario: Reader opens an English document

- **WHEN** a reader opens `README.md` or a relevant English document in
  `docs/`
- **THEN** the document provides a top-of-file link to its
  `pt-BR` mirror

### Requirement: Record bilingual synchronization in the workflow

The project MUST include bilingual synchronization in its documented
workflow and definition of done.

#### Scenario: Contributor checks the workflow before starting work

- **WHEN** a contributor reads the project operational artifacts
- **THEN** they can identify that bilingual document pairs must stay
  synchronized
