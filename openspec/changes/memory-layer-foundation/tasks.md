# Tasks

## 1. Specification

- [x] Define the memory-layer foundation proposal
- [x] Define the initial memory-layer specification
- [x] Record the next implementation-oriented tasks

## 2. Next implementation slices

- [x] Create the initial storage schema and repository contract for
  `memories`
- [x] Implement the memory retrieval contract with hybrid search inputs
  and bounded prompt injection
- [x] Add unit tests for the implemented memory-layer contracts and
  retrieval behavior
- [x] Implement the explicit memory write pipeline classification
  boundary (`memory_candidate` vs `ignore`)
- [ ] Implement memory deduplication and update behavior through
  `find_similar` before write-side upsert
- [ ] Enforce the initial allowed `type` and `scope` values in the
  memory write path
- [ ] Add unit tests for memory write-pipeline classification,
  deduplication, and allowed-value enforcement
