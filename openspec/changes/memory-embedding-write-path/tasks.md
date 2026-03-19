# Tasks

## 1. Specification

- [x] Define the memory embedding write-path proposal
- [x] Define the initial memory embedding write-path specification
- [x] Record the next implementation-oriented tasks

## 2. Next implementation slices

- [x] Define an explicit embedding provider boundary for memory capture
- [x] Attach generated embeddings during the memory write flow when a
  provider is available
- [ ] Define fallback behavior when embedding generation is unavailable
  or fails
- [ ] Preserve or replace embeddings explicitly when deduplicated memory
  updates occur
- [ ] Add unit tests for embedding-backed memory writes and fallback
  behavior
