# Spec: MCP Server Entrypoint

## Status

Proposed

## Requirements

### Requirement: Expose the wired MCP adapter as a server definition

The MCP adapter MUST expose a server-facing definition that binds the
current VeraBrain tool surface to callable handlers without moving
business rules into the transport layer.

The server definition MUST preserve, for each tool:

- the stable MCP tool name
- the human-facing tool description
- the declared input schema
- the callable handler that delegates into the wired application adapter

#### Scenario: VeraBrain composes an MCP server

- **WHEN** VeraBrain prepares its MCP integration surface
- **THEN** it produces a transport-ready server definition from the
  existing MCP adapter
- **AND** each tool remains bound to the same application-backed
  behavior already exposed by the adapter

### Requirement: Keep the initial runtime entrypoint stdio-first

The first MCP server runtime entrypoint MUST run over stdio transport so
Hermes can consume it through its existing MCP client flow.

The stdio entrypoint MUST be a thin adapter concern over the already
wired MCP application adapter.

#### Scenario: Hermes launches VeraBrain as an MCP server

- **WHEN** Hermes starts the VeraBrain MCP process through stdio
- **THEN** the server exposes the initial VeraBrain tool surface
- **AND** tool invocations dispatch into the same callable application
  services used by the non-transport adapter tests

### Requirement: Keep the MCP SDK optional at the transport edge

The MCP SDK dependency MUST remain isolated to the MCP server entrypoint
layer.

If the SDK is unavailable, the adapter MUST fail with a clear error that
explains how to install or supply the dependency, rather than leaking an
unclear import failure into the core.

#### Scenario: Contributor runs the server without the MCP SDK

- **WHEN** the stdio MCP server entrypoint is created without the
  optional MCP package installed
- **THEN** VeraBrain raises an explicit adapter-level dependency error
- **AND** the core and application layers remain importable without the
  transport package
