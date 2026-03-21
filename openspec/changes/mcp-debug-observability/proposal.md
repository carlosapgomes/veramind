# MCP Debug Observability

## Why

The local MVP now depends on real Hermes-to-MCP interactions, but the
current VeraBrain process emits too little diagnostic information to
debug failures reliably from its own side.

Today, most integration investigation depends on Hermes CLI summaries
instead of first-party VeraBrain logs. That makes it difficult to tell:

- whether the MCP tool was called with the expected arguments
- whether the write or retrieval path used lexical-only or semantic
  behavior
- whether a failure happened in startup, application wiring, or tool
  execution

## What Changes

- Add an explicit CLI debug mode to the local MVP launcher
- Emit MCP-server-side debug logs for startup and tool dispatch
- Keep debug logging optional so the normal local MVP path stays quiet

## Non-Goals

- Introducing full tracing or metrics infrastructure
- Logging secrets, raw embeddings, or entire long memory payloads
- Replacing Hermes-side logs

## Impact

- Makes VeraBrain integration issues diagnosable without depending only
  on Hermes summaries
- Preserves the quiet default path while enabling targeted debugging
  when needed
