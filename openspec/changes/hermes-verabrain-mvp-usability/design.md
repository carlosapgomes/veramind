# Design: Hermes VeraBrain MVP Usability

## Objective

Define the first practical usability layer for using VeraBrain through
Hermes during the MVP phase.

This change does not introduce a new architectural boundary. It adds a
procedural and interaction layer over the existing local MVP baseline so
that Hermes can use VeraBrain in a deliberate, repeatable, and
user-friendly way.

## Usability Decision Flow

The MVP usability flow should be:

1. Hermes first evaluates whether the user request can be satisfied
   through its own local/session memory layers
2. Hermes consults VeraBrain only when the request suggests durable
   cross-session memory or bounded durable recall
3. Hermes saves to VeraBrain when user intent to preserve something
   durably is explicit enough
4. Hermes retrieves from VeraBrain when the request clearly benefits
   from durable recall or bounded context retrieval

This preserves the previously accepted memory-boundary model while
making it easier to use in real interaction.

The initial decision policy should be expressed through three practical
classes:

- `stay-local`
- `retrieve-from-verabrain`
- `save-to-verabrain`

These classes are intentionally conservative.

### `stay-local`

Use this when Hermes can already handle the request through:

- prompt memory
- session-local context
- episodic recall
- procedural guidance from skills or local runtime behavior

This should remain the default class.

### `retrieve-from-verabrain`

Use this when the request benefits from durable cross-session memory,
such as:

- recalling prior stored facts about a topic
- recovering bounded context for an ongoing project
- checking what was explicitly saved for later use

This class should trigger bounded retrieval, not broad or automatic
knowledge expansion.

### `save-to-verabrain`

Use this when the user is clearly asking to preserve something durably,
such as:

- an idea worth keeping
- a project fact or project context worth recovering later
- a preference, rule, or decision worth reusing in future sessions

This class should remain explicit and should not be inferred too
aggressively from ordinary conversation.

## Hermes vs VeraBrain Usage Patterns

The initial usage split should remain:

- Hermes for prompt memory, session-local memory, episodic recall, and
  procedural guidance
- VeraBrain for durable memory capture and bounded durable retrieval

Practical MVP patterns should include:

- explicit durable save through `save_memory`
- bounded topic recall through `search_memory`
- bounded working context recall through `get_context_bundle`

The usability layer should not encourage Hermes to call VeraBrain for
every question. The default remains: stay local unless durable memory is
actually relevant.

## Role of the `VeraBrain` Skill

The Hermes `VeraBrain` skill should act as a procedural guide, not as
the memory authority model.

Its role should be:

- teach Hermes when to call the VeraBrain MCP tools
- teach Hermes how to interpret explicit user intent to save or recall
  durable memory
- reinforce the difference between session memory and durable memory
- provide practical examples of correct MVP usage

Its role should not be:

- redefining durable memory semantics
- changing the MCP contracts
- silently broadening capture policy

In practical MVP terms, the skill should map:

- `save-to-verabrain` -> `save_memory`
- `retrieve-from-verabrain` for topic lookup -> `search_memory`
- `retrieve-from-verabrain` for bounded working context ->
  `get_context_bundle`
- `stay-local` -> no VeraBrain tool call

The skill should also teach:

- the minimum arguments Hermes needs to provide
- what successful save or retrieval looks like
- when not to use VeraBrain at all

This keeps the skill procedural and lightweight. It tells Hermes how to
use VeraBrain; it does not redefine what VeraBrain is.

## Explicit User Intent Patterns

The usability design should focus first on strong, explicit patterns.

The initial intent model should be grouped into:

- `durable-save intents`
- `durable-recall intents`
- `stay-local by default`

### `durable-save intents`

These should map to `save-to-verabrain`.

Examples:

- “remember this”
- “register this idea/project/decision”
- “save this in VeraBrain”
- “keep this for later”

### `durable-recall intents`

These should map to `retrieve-from-verabrain`.

Examples:

- “what do I already know about X?”
- “check VeraBrain for this topic”
- “bring back context about this project”
- “recover what we stored about this”

### `stay-local by default`

These should remain in `stay-local` unless other strong signals are
present.

Examples:

- “what were we doing just now?”
- “continue this task”
- “summarize the last few messages”
- “what did you just tell me?”

The MVP should prefer strong explicit signals over subtle inference, and
the skill should preserve this mapping rather than improvising broader
capture behavior.

## Failure and Non-Use Cases

The usability layer should also define when Hermes should *not* use
VeraBrain.

Examples:

- transient task state that belongs only to the current session
- normal conversational context already present in Hermes
- requests that do not imply durable memory value
- cases where the user did not ask for durable save and durable recall
  is not clearly helpful

Operational failures should remain explicit:

- if the VeraBrain MCP server is unavailable, Hermes should not pretend
  that durable capture succeeded
- if retrieval is not available, Hermes should continue with its own
  memory layers rather than fabricate durable recall

## Out of Scope

This change does not cover:

- automatic always-on durable capture
- native Hermes plugin or hook integration
- advanced knowledge modeling
- execution workflow expansion
- changing the accepted Hermes vs VeraBrain memory authority model
