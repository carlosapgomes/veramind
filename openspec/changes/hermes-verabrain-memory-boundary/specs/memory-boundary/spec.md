# Spec: Hermes VeraBrain Memory Boundary

## Status

Proposed

## Requirements

### Requirement: Keep Hermes and VeraBrain memory roles distinct

The system MUST maintain an explicit distinction between:

- Hermes memory and session-local recall
- VeraBrain durable long-term memory

Hermes memory MUST remain the owner of session-local operational
context.

VeraBrain MUST remain the owner of durable memories that are intended to
survive across sessions and support later bounded retrieval.

#### Scenario: Contributor asks which system owns a memory kind

- **WHEN** a contributor evaluates a memory behavior
- **THEN** the project can classify it as Hermes-owned or
  VeraBrain-owned
- **AND** the same memory role is not treated as equally owned by both
  systems

### Requirement: Define the initial Hermes-owned memory scope

The initial policy MUST treat the following as Hermes-owned unless a
later policy explicitly promotes them:

- current session context
- immediate working memory for the active loop
- procedural or operational guidance already represented through Hermes
  mechanisms such as skills or bounded user modeling
- transient conversational details that do not merit durable recall

#### Scenario: Current conversational detail appears during an active session

- **WHEN** the information is only useful for the current session or
  immediate loop
- **THEN** it remains Hermes-owned
- **AND** the system does not automatically persist it as VeraBrain
  durable memory

### Requirement: Define the initial VeraBrain-owned memory scope

The initial policy MUST treat the following as VeraBrain durable-memory
candidates:

- stable user preferences
- durable personal or professional profile facts
- durable project context worth recovering later
- decisions, followups, and habits that merit cross-session recall

Those candidates MAY still be rejected by the VeraBrain write pipeline
when classification or validation says they should not be stored.

#### Scenario: Durable preference should survive across sessions

- **WHEN** a preference or durable fact is expected to help future
  sessions
- **THEN** it is treated as a VeraBrain durable-memory candidate
- **AND** VeraBrain remains the durable owner if it is persisted

### Requirement: Define an initial consultation order

The initial policy MUST define the order in which Hermes should rely on
its own context and on VeraBrain durable memory.

The initial consultation order is:

1. Hermes uses its current session-local context and built-in memory for
   the active interaction.
2. Hermes calls VeraBrain bounded retrieval when the task requires
   cross-session durable recall or a durable user/project memory lookup.
3. Hermes uses the returned VeraBrain memory context as a complement to,
   not a replacement for, its own active runtime context.

#### Scenario: Hermes can answer from active session context alone

- **WHEN** the required context is already available in Hermes-owned
  session memory
- **THEN** Hermes does not need to treat VeraBrain as the first source
  of truth for that interaction

#### Scenario: Hermes needs durable cross-session recall

- **WHEN** the task depends on stable memory beyond the current session
- **THEN** Hermes consults VeraBrain through the MCP-facing retrieval
  surface
- **AND** VeraBrain complements Hermes context rather than replacing it

### Requirement: Define the initial promotion boundary

The project MUST define when session-local information becomes a
candidate for VeraBrain durable storage.

The initial promotion rule is conservative:

- session-local information is not promoted automatically by default
- promotion to VeraBrain durable memory requires an explicit capture
  action through the VeraBrain MCP-facing memory surface

Later changes MAY introduce stronger automation or suggestion behavior,
but this change MUST not assume automatic background promotion.

#### Scenario: Session detail is not explicitly captured

- **WHEN** Hermes observes a transient or session-local detail
- **AND** no explicit VeraBrain capture action occurs
- **THEN** the detail remains Hermes-owned
- **AND** the system does not assume it became durable memory

#### Scenario: Durable fact is explicitly captured through VeraBrain

- **WHEN** Hermes or the user invokes the VeraBrain memory-capture
  surface explicitly
- **THEN** the information becomes a VeraBrain durable-memory candidate
- **AND** the existing VeraBrain write pipeline determines whether it is
  actually persisted

### Requirement: Keep MCP-first policy separate from later Hermes skills

The initial boundary policy MUST work with MCP-first integration and
MUST NOT depend on a native Hermes plugin or skill to be valid.

Hermes skills MAY later help operationalize this policy, but the policy
itself MUST be defined independently from prompt wording or skill text.

#### Scenario: Contributor evaluates whether a Hermes skill is required

- **WHEN** the contributor inspects the initial memory-boundary policy
- **THEN** the policy is already valid in an MCP-first integration
  model
- **AND** a future Hermes skill is treated as an operational layer over
  the policy rather than the policy source itself
