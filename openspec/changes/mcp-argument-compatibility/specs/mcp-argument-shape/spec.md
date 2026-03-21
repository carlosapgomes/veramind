# Spec: MCP Argument Compatibility

## Status

Proposed

## Requirements

### Requirement: Keep the direct MCP argument object canonical

The VeraBrain MCP adapter MUST continue to treat the direct argument
object as the canonical tool-call shape.

The normative input remains:

- `{...}`

and not:

- `{"kwargs": {...}}`

#### Scenario: Canonical MCP argument object is provided

- **WHEN** the adapter receives direct tool arguments at the root level
- **THEN** it processes those arguments without compatibility rewriting

### Requirement: Tolerate top-level `kwargs` wrapping at the adapter boundary

The VeraBrain MCP adapter MUST tolerate a top-level `kwargs` wrapper
when it contains the actual tool argument object.

This tolerance MUST be implemented only at the MCP adapter boundary and
MUST produce the same effective request object as the canonical direct
argument shape.

#### Scenario: Wrapped arguments arrive from an MCP client integration

- **WHEN** the adapter receives `{"kwargs": {...}}`
- **AND** the `kwargs` value is an object
- **THEN** the adapter unwraps that object before request mapping
- **AND** the downstream application contracts receive the same logical
  arguments as they would from the canonical direct shape

### Requirement: Reject malformed compatibility payloads explicitly

Compatibility tolerance MUST NOT silently accept malformed payloads.

If a top-level `kwargs` field is present but does not contain an object,
the adapter MUST surface an invalid-arguments error rather than guessing
or silently discarding data.

#### Scenario: Wrapped arguments are malformed

- **WHEN** the adapter receives a payload where `kwargs` is present but
  is not an object
- **THEN** the adapter returns an invalid-arguments error

### Requirement: Keep compatibility logic out of the core and application layers

The compatibility rule for wrapped MCP arguments MUST remain confined to
the MCP adapter boundary.

The VeraBrain application contracts, services, and core logic MUST NOT
gain Hermes-specific request-shape knowledge for this fix.

#### Scenario: Contributor extends MCP compatibility handling

- **WHEN** a contributor changes argument-shape handling for MCP inputs
- **THEN** the change stays in the MCP adapter layer
- **AND** the core and application layers continue to operate on normal
  VeraBrain request objects
