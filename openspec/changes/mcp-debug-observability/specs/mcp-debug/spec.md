# Spec: MCP Debug Observability

## Status

Proposed

## Requirements

### Requirement: Local MVP debug mode must be opt-in

The local MVP launcher MUST support an explicit debug mode that a
contributor can enable from the command line.

The default launcher behavior MUST remain quiet enough for normal local
use.

#### Scenario: Contributor enables debug mode

- **WHEN** the contributor starts the local MVP launcher with the debug
  option
- **THEN** VeraBrain emits startup and MCP diagnostic logs to stderr

### Requirement: MCP debug logs must come from VeraBrain itself

When debug mode is enabled, VeraBrain MUST log enough information to
diagnose MCP-side issues without depending only on Hermes summaries.

The initial debug logs MUST cover:

- startup context
- tool dispatch entry
- tool dispatch success or failure

#### Scenario: Tool call fails during MCP execution

- **WHEN** an MCP tool call fails inside VeraBrain
- **THEN** VeraBrain emits first-party diagnostic information about that
  failure
- **AND** the normal MCP response contract remains intact

### Requirement: Debug logs must avoid sensitive payload leakage

The initial debug logging path MUST avoid leaking secrets or oversized
internal payloads.

The initial implementation MUST therefore avoid logging:

- API keys
- raw embeddings
- full long memory payloads by default

#### Scenario: Contributor debugs a memory tool call

- **WHEN** VeraBrain logs an MCP tool invocation in debug mode
- **THEN** the log contains enough argument summary information for
  diagnosis
- **AND** it does not print secrets or raw embedding vectors
