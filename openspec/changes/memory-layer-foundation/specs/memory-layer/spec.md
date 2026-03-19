# Spec: Memory Layer Foundation

## Status

Proposed

## Requirements

### Requirement: Keep memory separate from the knowledge system

The memory layer MUST store durable facts about the user and the
ongoing relationship with the agent. It MUST NOT be treated as the
general document corpus for notes, files, transcripts, or captured web
content.

#### Scenario: Contributor decides where data belongs

- **WHEN** a contributor models a durable user preference, decision, or
  active project fact
- **THEN** the record belongs in the memory layer

#### Scenario: Contributor handles a reference document

- **WHEN** a contributor models documentation, transcripts, PDFs, or
  general note content
- **THEN** that content belongs to the knowledge system instead of the
  memory layer

### Requirement: Persist structured memory records

The memory layer MUST persist memory records in a durable `memories`
store with the following fields:

- `id`
- `text`
- `type`
- `scope`
- `salience`
- `created_at`
- `updated_at`
- `last_used_at`
- `source`
- `embedding`
- `metadata`

The initial allowed `type` values MUST be:

- `preference`
- `decision`
- `project`
- `habit`
- `followup`
- `profile`

The initial allowed `scope` values MUST be:

- `short`
- `medium`
- `long`

#### Scenario: A memory record is created

- **WHEN** the system persists a new memory
- **THEN** the record includes the required fields and uses an allowed
  `type` and `scope`

### Requirement: Classify memory candidates on write

The initial memory write pipeline MUST classify an incoming message for
memory persistence purposes before storing anything.

For the first memory slice, the pipeline MUST distinguish between:

- `memory_candidate`
- `ignore`

Other outcomes such as notes and tasks are out of scope for the initial
memory implementation.

#### Scenario: Message should not become durable memory

- **WHEN** an incoming message does not express durable user context
- **THEN** the pipeline classifies it as `ignore`
- **AND** no memory record is written

#### Scenario: Message should become durable memory

- **WHEN** an incoming message expresses durable user context
- **THEN** the pipeline classifies it as `memory_candidate`

### Requirement: Deduplicate and upsert memory records

When a message is classified as a `memory_candidate`, the pipeline MUST:

1. check for similar existing memories
2. update an existing memory when the candidate is materially the same
3. create a new memory when no matching memory exists
4. generate or attach an embedding for retrieval
5. store source and metadata needed for later inspection

The exact similarity threshold is implementation-defined for the first
implementation slice, but deduplication behavior MUST exist.

#### Scenario: Similar memory already exists

- **WHEN** a candidate memory materially matches an existing memory
- **THEN** the existing record is updated instead of creating a
  duplicate durable memory

#### Scenario: No similar memory exists

- **WHEN** no existing memory materially matches the candidate
- **THEN** the system creates a new memory record

### Requirement: Retrieve memories through hybrid relevance

The memory layer MUST support retrieval for response generation through
hybrid search that combines lexical and vector relevance.

The first retrieval implementation MUST:

- retrieve the top candidate memories for a query
- rerank them using semantic relevance, recency, salience, and memory
  type
- return only a bounded subset for prompt injection

#### Scenario: Runtime prepares prompt context

- **WHEN** the runtime requests relevant memories for a response
- **THEN** the memory layer returns a bounded set of the highest-ranked
  memories instead of the full memory store

### Requirement: Expose explicit memory contracts

The memory layer MUST be consumed through explicit contracts or tools
rather than through unrestricted direct access from unrelated modules.

The first implementation slice MUST at least support contract boundaries
for:

- saving memory
- searching memory

#### Scenario: Runtime needs memory capabilities

- **WHEN** the runtime needs to persist or retrieve memory
- **THEN** it uses explicit memory-layer contracts instead of bypassing
  the module boundary
