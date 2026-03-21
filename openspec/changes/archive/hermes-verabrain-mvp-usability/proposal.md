# Hermes VeraBrain MVP Usability

## Why

The repository now has an archived local MVP baseline for VeraBrain:

- Compose-backed Postgres with `pgvector`
- a host-launched MCP stdio launcher
- a manual runbook
- integration coverage for the local MVP path

What is still missing is the first usability layer that makes this MVP
natural to use from Hermes in day-to-day interaction.

Without a dedicated usability change:

- the VeraBrain MCP tools remain available but operationally thin
- contributors have to remember tool semantics manually
- Hermes has no explicit procedural guidance for when to save durable
  memory or when to retrieve it
- the local MVP may be technically runnable but still feel awkward in
  real use

## What Changes

- Define the initial Hermes-facing usability policy for the VeraBrain
  MVP
- Define how explicit user intent should trigger VeraBrain capture or
  retrieval
- Define the role of a Hermes skill as a procedural layer over the
  existing MCP tool surface
- Define the first practical prompt patterns and interaction paths for
  using VeraBrain through Hermes
- Define the first validation path for real MVP usage through Hermes

## Non-Goals

- Replacing the existing MCP-first integration strategy
- Introducing a native Hermes plugin or hook integration
- Expanding VeraBrain into broader knowledge-graph modeling
- Expanding execution workflows or GTD-oriented behavior
- Making VeraBrain automatic or silently always-on for durable capture

## Impact

- Turns the local MVP from “runnable” into “usable”
- Gives Hermes a clear procedural layer for working with VeraBrain
- Preserves the existing authority boundary between Hermes memory and
  VeraBrain durable memory
- Creates the right bridge from technical MVP to practical day-to-day
  usage
