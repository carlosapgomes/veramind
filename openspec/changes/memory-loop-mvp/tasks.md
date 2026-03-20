# Tasks

## 1. Specification

- [x] Define the memory loop MVP proposal
- [x] Define the initial memory loop MVP specification
- [x] Record the next implementation-oriented tasks

## 2. Next implementation slices

- [ ] Define the canonical observable happy path for
  `capture -> classify -> deduplicate -> embed -> persist -> retrieve`
- [ ] Define the minimum MCP-facing bounded retrieval behavior the MVP
  must expose to Hermes
- [ ] Define the observable fallback behavior for embedding or
  persistence degradation in the MVP loop
- [ ] Add an initial vertical integration slice that proves the MVP
  memory loop through the relevant application, adapter, and
  infrastructure boundaries
- [ ] Add end-to-end validation coverage for the MVP memory loop
