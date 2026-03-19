# Spec: MCP Tool Schemas and Mappings

## Status

Proposed

## Requirements

### Requirement: Expose the initial contract surface as MCP tools

The MCP adapter MUST define an initial tool surface that maps to the
VeraBrain application contracts for:

- saving and searching memories
- capturing and searching knowledge items
- linking knowledge items
- saving and searching execution items
- retrieving a bounded context bundle
- listing execution items due for review

#### Scenario: Hermes discovers the VeraBrain MCP server

- **WHEN** Hermes connects to the VeraBrain MCP adapter
- **THEN** it can discover explicit tools for the initial VeraBrain
  contract surface
- **AND** those tools map to application contracts instead of raw
  persistence operations

### Requirement: Define MCP tool schemas explicitly

Each initial MCP tool MUST define:

- a stable tool name
- a description that explains when the tool should be used
- a JSON-schema parameter object
- explicit required fields

The tool schemas MUST reject undeclared top-level properties.

#### Scenario: Contributor adds a new MCP tool

- **WHEN** a contributor defines an MCP-facing VeraBrain tool
- **THEN** the tool schema declares the input shape explicitly
- **AND** callers do not rely on implicit or undocumented parameters

### Requirement: Map MCP requests into typed application contracts

The MCP adapter MUST translate MCP arguments into typed application
request objects before calling the VeraBrain application layer.

This mapping layer MUST remain responsible for:

- adapter-level input coercion
- ISO-8601 datetime parsing
- default values for optional tool inputs

It MUST NOT own:

- business rules for memory, knowledge, or execution semantics
- storage-specific behavior
- ranking or deduplication policy

#### Scenario: MCP tool receives a valid payload

- **WHEN** the MCP adapter receives a valid tool payload
- **THEN** it maps that payload into the corresponding typed
  application request object
- **AND** the application layer receives adapter-neutral input

### Requirement: Return JSON-serializable MCP responses

The MCP adapter MUST convert VeraBrain records and bundles into
JSON-serializable response objects for MCP clients.

The initial response mapping MUST:

- serialize datetimes as ISO-8601 strings
- preserve typed record fields by domain
- keep context-bundle responses grouped by memory, knowledge, and
  execution

#### Scenario: Application contract returns a context bundle

- **WHEN** the MCP adapter receives a context bundle from the
  application layer
- **THEN** it returns an MCP response grouped by domain type
- **AND** each record is serialized without leaking Python-only objects

### Requirement: Keep MCP naming transport-specific and core contracts adapter-neutral

Tool naming and JSON-schema details MUST stay inside the MCP adapter.

The application contracts MUST NOT depend on MCP names or JSON-schema
objects.

#### Scenario: Future Hermes plugin reuses the same contract

- **WHEN** a future Hermes plugin adapter needs the same capability
- **THEN** it can reuse the VeraBrain application contracts
- **AND** it does not inherit MCP-specific tool-schema details
