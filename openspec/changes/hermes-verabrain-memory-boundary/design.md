# Design: Hermes VeraBrain Memory Boundary

## Objective

Define the first operational boundary between Hermes-owned memory and
VeraBrain-owned durable memory.

This change does not redesign either system. It defines who owns which
memory role, when Hermes should consult VeraBrain, and when information
may be promoted from session-local context into durable memory.

## Authority Model

The initial authority model is asymmetric by design:

- Hermes owns session-local context and runtime-working memory.
- VeraBrain owns durable cross-session memory once information is
  explicitly captured into its pipeline.

The purpose of this model is to avoid dual ownership of the same memory
role.

Operationally, the model has three states:

- `Hermes-owned`
- `promotion-candidate`
- `VeraBrain-owned`

`promotion-candidate` is intentionally not a third memory store. It is
only a policy state meaning:

- the information may deserve durable storage later
- but Hermes still owns it until explicit VeraBrain capture succeeds

This avoids accidental authority transfer just because something sounds
important.

## Hermes-Owned Scope

Hermes remains the owner of:

- active conversation context
- immediate working memory for the current loop
- transient interaction details
- runtime-operational guidance already represented by Hermes-native
  mechanisms

This information may influence the current interaction without becoming
durable VeraBrain memory.

Hermes also remains the owner of:

- session findings that have not yet been intentionally promoted
- episodic recall from prior sessions
- task-local state and temporary execution details

## VeraBrain-Owned Scope

VeraBrain remains the owner of durable memory candidates such as:

- stable preferences
- durable profile facts
- durable project context
- decisions, followups, and habits with cross-session value

These are still subject to VeraBrain classification, validation, and
deduplication. Being a candidate does not mean the write path must
persist it.

Authority transfers to VeraBrain only after:

1. explicit capture through the VeraBrain surface
2. successful persistence through the VeraBrain write path

Until then, the information remains Hermes-owned even if contributors
expect it may later become durable memory.

## Initial Authority Matrix

The initial matrix is:

- active conversation detail -> Hermes-owned
- current task progress -> Hermes-owned
- episodic "we discussed this before" recall -> Hermes-owned
- stable preference not yet captured -> promotion-candidate under Hermes
- durable project fact not yet captured -> promotion-candidate under
  Hermes
- persisted durable preference/fact/decision -> VeraBrain-owned

This matrix is intentionally conservative. It biases toward keeping
authority in Hermes until durable promotion is explicit.

## Consultation Order

The initial consultation order is:

1. Hermes first uses its active session context and built-in memory.
2. Hermes consults VeraBrain when the task needs durable recall beyond
   the current session.
3. Hermes treats VeraBrain retrieval as complementary durable context,
   not as a replacement for its active runtime context.

This prevents VeraBrain from becoming a default lookup for every local
interaction detail.

## Promotion Boundary

The initial promotion boundary is conservative:

- no automatic background promotion by default
- no assumption that session observations become durable memory
- promotion requires an explicit VeraBrain capture action through the
  MCP-facing memory surface

This keeps durable-memory writes intentional until a later change
defines stronger automation or suggestion behavior.

## MCP-First Interaction Pattern

The initial policy should work entirely through MCP-first integration.

The practical pattern is:

- Hermes handles the active interaction with its own context first
- Hermes calls VeraBrain MCP retrieval when durable memory is needed
- Hermes calls VeraBrain MCP capture only when durable promotion is
  intentional

This means the policy is enforceable before any native plugin or skill
exists.

## Future Skill Role

A future Hermes skill may help operationalize the policy by teaching the
agent:

- when to query VeraBrain
- when to capture durable memory
- when to keep information session-local

But the skill must not become the source of truth for the policy. The
policy must remain defined here and in the spec.

## Out of Scope

This change intentionally does not define:

- final prompt wording for Hermes
- autonomous memory promotion heuristics
- native Hermes plugin behavior
- durable knowledge or execution boundaries beyond the memory question

Those remain later concerns after the memory boundary is explicit.
