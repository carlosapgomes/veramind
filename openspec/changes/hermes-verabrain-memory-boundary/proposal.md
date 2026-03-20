# Hermes VeraBrain Memory Boundary

## Why

The repository now has a proven MVP memory loop for VeraBrain:

- durable memory capture
- write-path classification and deduplication
- embedding-backed persistence with explicit fallback
- bounded retrieval through the MCP-facing surface

What remains unresolved is the authority boundary between:

- Hermes built-in memory and session-local recall
- VeraBrain durable long-term memory

Without an explicit policy change, future work risks:

- storing the same kind of memory in both systems without a clear owner
- creating ambiguous retrieval behavior for Hermes
- promoting session-local context into durable memory implicitly
- pushing policy into ad hoc prompts or skills instead of a project
  artifact

## What Changes

- Define the initial authority boundary between Hermes memory and
  VeraBrain memory
- Define what kinds of information stay session-local in Hermes
- Define what kinds of information are durable-memory candidates for
  VeraBrain
- Define the initial consultation order and promotion boundary between
  Hermes context and VeraBrain durable memory
- Record the next implementation-oriented slices for applying this
  policy through MCP-first integration

## Non-Goals

- Replacing Hermes built-in memory with VeraBrain
- Defining a final native Hermes plugin strategy
- Designing the full prompt or skill wording Hermes will eventually use
- Expanding knowledge-system scope or execution workflows
- Changing the existing VeraBrain memory write pipeline itself

## Impact

- Prevents authority confusion between Hermes and VeraBrain
- Creates a policy baseline for future MCP usage and possible Hermes
  skills
- Ensures later integration work follows an explicit memory contract
  rather than implicit habits
