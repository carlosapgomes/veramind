# Spec: OpenAI Embedding Runtime Integration

## Status

Proposed

## Requirements

### Requirement: Keep OpenAI embedding integration outside the core

The first runtime-backed embedding integration MUST remain confined to
runtime and infrastructure edges.

Core and application services MUST continue to depend on the existing
adapter-neutral embedding contracts rather than OpenAI SDK objects,
transport details, or provider-specific request payloads.

#### Scenario: Runtime adopts OpenAI for memory embeddings

- **WHEN** the local MVP path is configured to use OpenAI embeddings
- **THEN** the provider-specific wiring occurs outside core and
  application domain logic
- **AND** the existing embedding-facing contracts remain unchanged

### Requirement: The local MVP runtime must define explicit OpenAI settings

The local MVP runtime MUST define an explicit configuration surface for
OpenAI embeddings.

That settings surface MUST support, at minimum:

- API key configuration
- model selection
- the ability to keep embeddings disabled when configuration is absent

#### Scenario: Runtime starts without OpenAI credentials

- **WHEN** the local MVP launcher starts without the configured OpenAI
  embedding credentials
- **THEN** the launcher follows the defined fallback behavior
- **AND** the absence of embeddings remains observable rather than
  implicit

### Requirement: OpenAI embeddings must support both write and query paths

The first provider-backed runtime integration MUST support:

- write-time memory embeddings during durable memory capture
- query-time embeddings for hybrid memory retrieval

The two uses MAY share a provider implementation, but they MUST remain
explicitly wired through the existing write and retrieval boundaries.

#### Scenario: Local MVP runs with OpenAI embeddings configured

- **WHEN** a user saves durable memory through the local MVP path
- **THEN** the memory write flow can attach an embedding through the
  configured provider
- **AND WHEN** the user later searches durable memory
- **THEN** the retrieval path can generate a query embedding for hybrid
  retrieval

### Requirement: Runtime fallback must remain explicit and survivable

If OpenAI embeddings are unavailable because configuration is missing,
the provider returns no embedding, or the provider request fails, the
local MVP path MUST keep the current explicit fallback behavior.

The initial integration MUST therefore preserve:

- durable memory writes without embeddings when fallback applies
- explicit metadata or observable runtime state showing degraded
  embedding behavior
- lexical-only retrieval when query embeddings are unavailable

#### Scenario: OpenAI request fails during memory save

- **WHEN** the runtime cannot obtain an embedding from OpenAI during a
  memory write
- **THEN** the system preserves the defined explicit fallback behavior
- **AND** the durable write flow remains survivable if persistence is
  otherwise available

#### Scenario: OpenAI request fails during retrieval

- **WHEN** the runtime cannot obtain a query embedding from OpenAI for a
  memory search
- **THEN** the retrieval path falls back to the existing lexical-only
  bounded behavior

### Requirement: OpenAI runtime integration must be documented for local MVP use

The local MVP documentation MUST describe how to configure and use the
OpenAI-backed embedding path.

The documentation MUST cover:

- required environment variables
- the local MVP startup path with OpenAI configured
- the expected fallback behavior when embeddings are unavailable

#### Scenario: Contributor enables OpenAI embeddings locally

- **WHEN** a contributor follows the local MVP runbook
- **THEN** they can configure the OpenAI embedding path without reading
  implementation code
- **AND** they understand how degraded embedding behavior appears when
  configuration or provider calls fail
