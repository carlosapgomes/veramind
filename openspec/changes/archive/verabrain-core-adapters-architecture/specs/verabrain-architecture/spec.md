# Spec: VeraBrain Core and Adapter Architecture

## Status

Proposed

## Requirements

### Requirement: Structure VeraBrain as a core-plus-adapters system

VeraBrain MUST be structured as a core domain and application layer
with adapter layers around it.

The VeraBrain core MUST remain independent from:

- MCP transport details
- Hermes plugin manifests, hooks, and runtime APIs
- CLI or presentation concerns

#### Scenario: Contributor places a new capability

- **WHEN** a contributor designs a new VeraBrain capability
- **THEN** business rules are placed in the VeraBrain core
- **AND** transport-specific code is placed in an adapter layer

### Requirement: Keep dependencies unidirectional

The dependency direction for the Hermes-centered architecture MUST be:

- `Hermes runtime -> MCP adapter or Hermes plugin adapter`
- `adapter -> VeraBrain application contracts`
- `application contracts -> domain model and infrastructure ports`
- `infrastructure adapters -> external services and storage`

The VeraBrain core MUST NOT depend directly on Hermes runtime internals,
MCP tool definitions, or plugin-specific hooks.

#### Scenario: Contributor adds a new adapter

- **WHEN** a contributor adds or replaces an integration adapter
- **THEN** the adapter depends on VeraBrain contracts
- **AND** the VeraBrain core does not gain a reverse dependency on that
  adapter

### Requirement: Keep memory, knowledge, execution, and GTD distinct

The VeraBrain domain model MUST preserve explicit boundaries between the
following concerns:

- `memory`
  - durable user facts, preferences, decisions, and continuity context
- `knowledge items`
  - notes, captures, references, documents, research, and linked
    artifacts
- `execution`
  - tasks, open loops, reviews, and action state
- `GTD-inspired workflow layer`
  - inbox clarification, next-action conventions, waiting-for,
    someday/maybe, and review flows

The GTD-inspired workflow layer MUST remain optional and MUST be built
on top of the execution and knowledge model rather than defining the
base identity of VeraBrain.

#### Scenario: Contributor models a GTD workflow

- **WHEN** a contributor adds GTD-inspired behavior
- **THEN** that behavior uses the existing execution and knowledge
  structures
- **AND** the base domain does not require GTD as its only workflow

### Requirement: Expose explicit application contracts to Hermes

Hermes-facing integrations MUST call VeraBrain through explicit
application contracts instead of accessing domain objects or storage
directly.

The initial contract surface MUST at least cover:

- saving and searching memories
- capturing and retrieving knowledge items
- linking related items
- creating and updating execution items
- retrieving a bounded context bundle for agent use
- running review-oriented workflows

The exact function or tool names are implementation-defined, but the
contract boundaries MUST be explicit and adapter-neutral.

#### Scenario: Hermes requests long-term context

- **WHEN** Hermes needs durable context beyond its built-in memory,
  `session_search`, or optional Honcho layer
- **THEN** the adapter calls the relevant VeraBrain application
  contract
- **AND** it receives a typed, bounded result instead of raw storage
  access

### Requirement: Use MCP as the initial adapter, not the center

The first Hermes-facing VeraBrain integration MUST treat MCP as the
initial adapter boundary rather than the architectural center of the
system.

The MCP adapter MUST translate MCP tool requests into VeraBrain
application contract calls and MUST NOT own VeraBrain business rules.

#### Scenario: MCP tool is implemented

- **WHEN** a contributor implements an MCP-facing tool
- **THEN** the tool schema and transport mapping stay in the MCP adapter
- **AND** the core behavior remains reusable outside MCP

### Requirement: Allow an optional Hermes plugin adapter

The architecture MUST allow an optional Hermes plugin adapter that can
reuse the same VeraBrain application contracts as the MCP adapter.

The Hermes plugin adapter MAY add user experience improvements, setup
helpers, or hook-driven orchestration, but it MUST remain a thin layer.

#### Scenario: Project later adds a Hermes plugin

- **WHEN** a native Hermes plugin becomes desirable
- **THEN** the plugin delegates to the same application contracts used
  by the MCP adapter
- **AND** the VeraBrain core does not require redesign to support the
  new adapter

### Requirement: Keep adapter responsibilities thin

Adapters MAY handle request parsing, schema validation, identity or
session metadata translation, response serialization, and transport-
specific error mapping.

Adapters MUST NOT own:

- domain classification rules
- storage policy
- retrieval ranking logic
- task or review business rules
- GTD workflow semantics

#### Scenario: Contributor implements adapter behavior

- **WHEN** an adapter needs logic beyond request and response
  translation
- **THEN** that logic is placed into a VeraBrain application or domain
  component instead of staying inside the adapter
