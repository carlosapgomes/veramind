# Spec: Hermes VeraBrain MVP Usability

## Status

Proposed

## Requirements

### Requirement: Define the initial Hermes-facing usability policy

The project MUST define the initial policy for how Hermes should use
VeraBrain during the MVP phase.

The initial policy MUST preserve the archived memory-boundary baseline:

- Hermes keeps session-local, prompt, episodic, and procedural memory
  responsibilities
- VeraBrain remains the durable-memory and bounded-retrieval subsystem

The usability layer MUST clarify when Hermes should:

- stay within its own memory layers
- call VeraBrain retrieval tools
- call VeraBrain save tools

#### Scenario: Hermes evaluates whether to involve VeraBrain

- **WHEN** Hermes is handling a user request during the MVP phase
- **THEN** Hermes has explicit procedural guidance for whether to stay
  local or call VeraBrain
- **AND** that guidance preserves the existing authority boundary

### Requirement: Define explicit user-intent-driven VeraBrain usage

The initial MVP usability path MUST prefer explicit user intent for
durable capture and deliberate recall.

The project MUST define the initial user-facing phrases, requests, or
interaction patterns that should strongly signal:

- durable save into VeraBrain
- bounded retrieval from VeraBrain

The initial design MUST NOT rely on silent or overly aggressive durable
capture.

#### Scenario: User explicitly asks Hermes to save durable memory

- **WHEN** the user asks Hermes to remember, register, or save something
  durably for future use
- **THEN** the usability layer treats that as a strong signal to use the
  VeraBrain save path
- **AND** the resulting behavior remains explicit and observable

### Requirement: Define the role of a Hermes VeraBrain skill

The project MUST define the role of a Hermes `VeraBrain` skill in the
MVP usage path.

The skill MUST be treated as a procedural guide for when and how Hermes
should call the existing VeraBrain MCP tools.

The skill MUST NOT become the architectural source of truth for:

- memory authority
- durable storage semantics
- MCP tool contracts

#### Scenario: Hermes uses the VeraBrain skill during MVP usage

- **WHEN** Hermes has the VeraBrain skill available
- **THEN** the skill guides Hermes toward the correct VeraBrain MCP
  tools and usage patterns
- **AND** the underlying MCP contracts remain the operational boundary

### Requirement: Define practical MVP interaction patterns

The project MUST define the first practical interaction patterns for
using VeraBrain through Hermes.

The initial patterns MUST at least cover:

- explicit durable save
- bounded recall for a question or topic
- bounded context retrieval for active work

#### Scenario: Contributor uses VeraBrain through Hermes in practice

- **WHEN** a contributor follows the MVP usability guidance
- **THEN** the contributor can reliably trigger the intended VeraBrain
  behavior through Hermes
- **AND** the behavior is aligned with the existing local MVP baseline

### Requirement: Keep usability work scoped to the MVP

This change MUST stay focused on the MVP usability layer over the
existing local VeraBrain baseline.

It MUST NOT expand into:

- native Hermes plugin architecture
- automatic always-on durable capture
- broader product repositioning
- advanced knowledge modeling or execution workflows

#### Scenario: Contributor evaluates the usability change scope

- **WHEN** a contributor uses the artifacts from this change
- **THEN** the result improves practical MVP usage through Hermes
- **AND** the change stays within the current MVP scope
