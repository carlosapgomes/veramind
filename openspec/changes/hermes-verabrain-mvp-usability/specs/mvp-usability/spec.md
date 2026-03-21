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

The initial MVP usability policy MUST define three default decision
classes:

- `stay-local`
- `retrieve-from-verabrain`
- `save-to-verabrain`

The initial default MUST be conservative:

- Hermes stays local unless durable memory is clearly relevant
- Hermes retrieves from VeraBrain only when cross-session durable recall
  would materially help
- Hermes saves to VeraBrain only when explicit durable-save intent is
  strong enough

The initial policy MUST treat these as practical rules of use, not as a
replacement for the previously accepted memory-boundary model.

#### Scenario: Hermes evaluates whether to involve VeraBrain

- **WHEN** Hermes is handling a user request during the MVP phase
- **THEN** Hermes has explicit procedural guidance for whether to stay
  local or call VeraBrain
- **AND** that guidance preserves the existing authority boundary

#### Scenario: Hermes defaults to local memory layers

- **WHEN** the user request can be handled through prompt memory,
  session-local context, episodic recall, or procedural guidance already
  available in Hermes
- **THEN** Hermes stays in the `stay-local` decision class
- **AND** does not call VeraBrain by default

#### Scenario: Hermes uses VeraBrain for durable recall

- **WHEN** the user request suggests a need for durable cross-session
  recall or bounded stored context
- **THEN** Hermes moves into the `retrieve-from-verabrain` decision
  class
- **AND** uses the bounded VeraBrain retrieval path instead of treating
  VeraBrain as a full replacement for local context

#### Scenario: Hermes uses VeraBrain for explicit durable save

- **WHEN** the user request clearly asks for durable preservation of an
  idea, preference, project fact, or decision
- **THEN** Hermes moves into the `save-to-verabrain` decision class
- **AND** uses the explicit VeraBrain save path rather than silently
  assuming the information was persisted

### Requirement: Define explicit user-intent-driven VeraBrain usage

The initial MVP usability path MUST prefer explicit user intent for
durable capture and deliberate recall.

The project MUST define the initial user-facing phrases, requests, or
interaction patterns that should strongly signal:

- durable save into VeraBrain
- bounded retrieval from VeraBrain

The initial design MUST NOT rely on silent or overly aggressive durable
capture.

The initial MVP usability layer MUST define two explicit intent groups:

- `durable-save intents`
- `durable-recall intents`

The initial mapping from intent to behavior MUST be:

- `durable-save intents` -> `save-to-verabrain`
- `durable-recall intents` -> `retrieve-from-verabrain`

The project MUST also define examples of requests that remain
`stay-local`, so contributors do not over-apply VeraBrain.

#### Scenario: User explicitly asks Hermes to save durable memory

- **WHEN** the user asks Hermes to remember, register, or save something
  durably for future use
- **THEN** the usability layer treats that as a strong signal to use the
  VeraBrain save path
- **AND** the resulting behavior remains explicit and observable

#### Scenario: User explicitly asks Hermes to retrieve durable memory

- **WHEN** the user asks what is already stored, remembered, or known in
  VeraBrain about a topic, project, or prior saved context
- **THEN** the usability layer treats that as a strong signal to use the
  VeraBrain bounded retrieval path
- **AND** the resulting behavior remains bounded and observable

#### Scenario: User request remains local by default

- **WHEN** the user request only concerns the current session,
  immediate task progress, or normal conversational continuity
- **THEN** the usability layer keeps Hermes in the `stay-local`
  decision class
- **AND** the request does not escalate into VeraBrain usage by default

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
