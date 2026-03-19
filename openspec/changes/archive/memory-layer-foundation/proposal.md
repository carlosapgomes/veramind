# Memory Layer Foundation

## Why

The repository already states that durable memory is a core part of the
system, but it only exists as architecture notes and not as an
implementable specification.

Without a dedicated memory-layer spec, the next implementation slice
would risk mixing memory with knowledge, overreaching into task
management, or introducing storage behavior that is hard to change.

## What Changes

- Specify the initial memory-layer domain and its boundaries
- Define the first durable memory record shape
- Define the initial write pipeline for memory capture
- Define the initial retrieval behavior for prompt augmentation
- Explicitly record non-goals for the first memory slice
- Reconcile this change against the later archived foundation and
  retrieval changes that already implemented part of the memory baseline

## Non-Goals

- Implementing note storage
- Implementing task management
- Implementing background consolidation or scheduling
- Choosing the final embedding model
- Defining the final prompt orchestration strategy

## Impact

- Clarifies what the first memory implementation slice should build
- Protects the distinction between memory and the knowledge system
- Creates a concrete contract for tests, tooling, and future ADRs
- Makes the remaining gap explicit: the memory write pipeline still
  needs classification, deduplication, and allowed-value enforcement
