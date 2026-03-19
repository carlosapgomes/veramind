# Tasks

## 1. Specification

- [x] Define the core-and-adapters architecture proposal
- [x] Define the VeraBrain architecture specification
- [x] Record the next implementation-oriented tasks

## 2. Next implementation slices

- [x] Create the initial Python package skeleton for `core`,
  `application`, `adapters`, and `infrastructure`
- [x] Specify the repository and persistence ports for memory,
  knowledge, and execution records
- [x] Define the initial MCP tool schemas and request/response mappings
  for the application contracts
- [x] Add unit tests for the application contracts and boundary rules
  when implementation begins
- [x] Define the first callable application services behind the request
  contracts
- [x] Wire the MCP adapter mappings and schemas to the callable
  application services
- [x] Add the initial MCP server entrypoint over the wired application
  services
- [x] Implement the initial in-memory persistence adapters for the
  repository ports
- [x] Record ADRs for persistence architecture, retrieval boundaries,
  and the VeraBrain tool model
- [x] Specify the Postgres + pgvector persistence adapter boundaries
- [x] Implement the Postgres + pgvector repository and unit-of-work
  adapters
- [x] Add initial schema and migration support for the Postgres
  persistence path
