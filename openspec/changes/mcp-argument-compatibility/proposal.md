# MCP Argument Compatibility

## Why

The current VeraBrain MCP adapter expects tool arguments in the
canonical MCP shape: the tool argument object is passed directly at the
root of the tool call payload.

In practical Hermes integration, there are cases where tool arguments
arrive wrapped as:

- `{"kwargs": {...}}`

instead of:

- `{...}`

This creates an avoidable interoperability failure at the MCP adapter
boundary even though the underlying VeraBrain application contracts are
already correct.

Without an explicit compatibility slice, local MVP testing can fail for
transport-shape reasons rather than for domain or persistence reasons.

## What Changes

- Define a compatibility rule for MCP tool arguments at the VeraBrain
  adapter boundary
- Keep the canonical direct-arguments MCP shape as the normative form
- Allow the adapter to unwrap a top-level `kwargs` object when present
- Keep this tolerance isolated to the MCP adapter boundary
- Record the implementation-oriented tasks for the compatibility fix

## Non-Goals

- Replacing MCP with a CLI-first integration path
- Changing application contracts or domain request objects
- Making `kwargs` wrapping the new canonical tool-call format
- Adding Hermes-specific logic to the VeraBrain core or application
  layers
- Redefining the archived MCP server or MVP usability baselines

## Impact

- Makes the VeraBrain MCP adapter more tolerant to Hermes-side
  invocation shape drift
- Preserves MCP-first architecture while avoiding unnecessary runtime
  friction
- Keeps compatibility logic local to the integration boundary where it
  belongs
