---
name: verabrain
description: Use VeraBrain as a durable-memory subsystem over MCP. Apply when the user explicitly wants to save something for future cross-session use or retrieve bounded durable context about a topic, project, preference, or decision. Do not use for ordinary session-local continuity or transient task state.
version: 0.1.0
author: VeraMind
license: MIT
metadata:
  hermes:
    tags: [memory, pkm, second-brain, mcp, verabrain]
    related_skills: []
---

# VeraBrain

Use VeraBrain as Hermes's durable-memory companion through the existing
MCP tool surface.

## Purpose

This skill helps you decide:

- when to stay within Hermes's own memory layers
- when to save something durably in VeraBrain
- when to retrieve bounded durable context from VeraBrain

This skill is procedural guidance only. It does not redefine:

- Hermes memory authority
- VeraBrain storage semantics
- VeraBrain MCP contracts

## Decision Classes

### `stay-local`

Use this as the default.

Stay local when the request can be handled through:

- prompt memory
- current session context
- episodic recall from Hermes
- procedural guidance already available in Hermes

Do not call VeraBrain for:

- normal conversational continuity
- transient task progress
- short-lived working context that belongs only to this session

### `save-to-verabrain`

Use this when the user clearly asks to preserve something durably for
future use.

Typical durable-save requests:

- "remember this"
- "register this idea"
- "save this in VeraBrain"
- "keep this for later"

Use this for:

- ideas worth keeping
- project facts worth recovering later
- preferences, rules, or decisions with future reuse value

### `retrieve-from-verabrain`

Use this when the user clearly asks for durable cross-session recall.

Typical durable-recall requests:

- "what do I already know about X?"
- "check VeraBrain for this topic"
- "bring back context about this project"
- "recover what we stored about this"

## Tool Mapping

Map decision classes to MCP tools like this:

- `save-to-verabrain` -> `save_memory`
- `retrieve-from-verabrain` for topic lookup -> `search_memory`
- `retrieve-from-verabrain` for bounded working context ->
  `get_context_bundle`
- `stay-local` -> do not call a VeraBrain MCP tool

## Minimum Tool Usage

### `save_memory`

Use when the user is explicitly asking to preserve something durably.

Minimum arguments:

- `text`
- `type`
- `scope`
- `source`

Use `source="manual"` unless a stronger source convention is
explicitly available.

### `search_memory`

Use when the user wants a bounded lookup about a stored topic or fact.

Minimum arguments:

- `text`
- `limit`

Keep the request narrow and topic-focused.

### `get_context_bundle`

Use when the user wants bounded durable context for active work.

Minimum arguments:

- `query`
- `memory_limit`

Prefer this when the user wants context for a project, topic, or active
thread of work rather than a simple lookup.

## Interaction Rules

1. Default to `stay-local` unless durable memory is clearly relevant.
2. Prefer explicit user intent over subtle inference.
3. Never claim something was durably saved unless `save_memory`
   actually succeeded.
4. Never fabricate durable recall if VeraBrain retrieval is unavailable.
5. Keep retrieval bounded; do not treat VeraBrain as an unbounded dump
   of context.
6. Do not silently broaden capture policy beyond the user's intent.

## Practical Patterns

### Explicit Durable Save

If the user says:

> Save this idea in VeraBrain: I want a personal assistant workflow for
> vascular surgery study notes.

Then:

1. choose `save-to-verabrain`
2. call `save_memory`
3. confirm the save result explicitly

### Topic Recall

If the user says:

> What do we already have in VeraBrain about my PKM roadmap?

Then:

1. choose `retrieve-from-verabrain`
2. call `search_memory`
3. summarize the bounded result

### Bounded Working Context

If the user says:

> Bring back the context we saved about the local MVP for VeraBrain.

Then:

1. choose `retrieve-from-verabrain`
2. call `get_context_bundle`
3. use the bounded context in the reply

## Non-Use Cases

Do not use VeraBrain when the user is only asking about:

- the current chat turn
- the last few messages
- a transient TODO for this session
- ordinary follow-up context that Hermes already has
