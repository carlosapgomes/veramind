# VeraBrain Concept Model

[Portuguese (Brazil)](./verabrain-concept-model.pt-BR.md)

## Purpose

This document captures the initial conceptual model for VeraBrain as a
second-brain and personal knowledge system.

Its goal is to clarify what belongs in the VeraBrain core, what belongs
in optional workflow layers, and where GTD-inspired behavior fits.

## Positioning

VeraBrain should not be framed as:

- only a task manager
- only a note-taking system
- only a memory store for an agent
- only a GTD implementation

VeraBrain should be framed as:

- a personal memory and knowledge system
- a second-brain layer that helps capture, organize, relate, and
  retrieve durable context
- an optional execution layer for turning open loops into action

## Architectural View

VeraBrain should be modeled as three layers:

1. `Second-brain core`
2. `Personal knowledge system`
3. `Execution workflows`

The core idea is that execution is important, but it should sit on top
of the knowledge model rather than define it.

## 1. Second-Brain Core

This is the minimal VeraBrain center of gravity.

It should own:

- durable personal memory
- contextual retrieval
- semantic relationships between items
- identity and preference facts
- project and topic continuity across sessions

This layer answers questions such as:

- What should the system remember about the user over time?
- What context should be easy to recover later?
- What relationships exist between projects, people, topics, and
  decisions?

### Core objects

- `Memory`
  - durable facts about the user, preferences, decisions, habits, and
    active context
- `KnowledgeItem`
  - notes, documents, excerpts, captures, summaries, references, and
    research artifacts
- `Link`
  - semantic relation between two items, such as `supports`,
    `relates_to`, `contradicts`, `belongs_to`, or `derived_from`
- `Source`
  - origin metadata for a captured item, such as URL, local file,
    conversation, message, or manual entry

### Core responsibilities

- capture
- classify
- enrich
- store
- link
- retrieve
- summarize

## 2. Personal Knowledge System

This layer sits above the core memory engine and focuses on managing a
broader corpus of personal knowledge.

It should include:

- notes
- research captures
- ADRs and decisions
- snippets
- bookmarks and web captures
- transcripts
- supporting documents

### PKS organizing concepts

- `Project`
  - a multi-step outcome with active or historical relevance
- `Area`
  - a persistent responsibility domain such as health, finances, career,
    family, or product work
- `Topic`
  - a theme or concept that may span multiple projects and notes
- `Decision`
  - a durable conclusion with rationale and consequences
- `Reference`
  - useful information that is not actionable by itself but should be
    retrievable later

### PKS design principle

The PKS should optimize for:

- easy capture
- low-friction retrieval
- meaningful linking
- gradual structuring

It should not require the user to fully classify everything up front.

## 3. Execution Workflows

Execution should be modeled as a separate layer that uses the same
underlying memory and knowledge structures.

This layer should include:

- tasks
- next actions
- reminders
- waiting-for items
- inbox processing
- reviews
- checklists

### Execution objects

- `InboxItem`
  - unprocessed input that still needs clarification
- `Task`
  - a concrete actionable item
- `OpenLoop`
  - something unresolved that may or may not already be an explicit task
- `Review`
  - a recurring or ad hoc process for re-evaluating state

## Where GTD Fits

GTD should be treated as an optional execution methodology rather than
the core VeraBrain identity.

That means VeraBrain should support GTD-inspired capabilities such as:

- inbox capture
- clarification
- next actions
- project tracking
- waiting-for
- someday/maybe
- weekly review

But the data model should not be hard-coded around GTD as the only valid
workflow.

### Recommended stance

- `Second-brain core`: mandatory
- `Personal knowledge system`: mandatory
- `Task and review layer`: recommended
- `GTD workflow conventions`: optional but first-class

## Boundary Between Knowledge and Execution

The following distinction should remain explicit:

- Knowledge answers: what do I know, what happened, what matters, and
  how things connect?
- Execution answers: what should I do next, what am I waiting on, and
  what needs review?

This avoids collapsing VeraBrain into either:

- a pure notes system with no action model
- a pure task system with weak context and poor memory

## Suggested Initial Domain Entities

The first conceptual entity set should be:

- `Memory`
- `KnowledgeItem`
- `Project`
- `Area`
- `Task`
- `OpenLoop`
- `Decision`
- `Source`
- `Link`
- `Review`

This is intentionally broad enough to support both PKM and execution
without forcing a full GTD implementation from day one.

## Initial Non-Goals

At this stage, VeraBrain should not assume:

- a full GTD implementation before the core memory model exists
- a rigid PARA-only or GTD-only taxonomy
- a heavy productivity UI as the first milestone
- that every captured item must become a task
- that every unresolved thought must be formalized immediately

## Product Direction Implication

The likely product framing is:

> VeraBrain is a personal memory and knowledge system with optional
> execution workflows, including GTD-inspired task and review layers.

That framing keeps the system broad enough to support:

- second-brain use cases
- personal knowledge management
- project continuity
- action management
- future methodology-specific views without locking the architecture too
  early
