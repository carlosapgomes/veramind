# Spec: Postgres JSONB Parameter Adaptation

## ADDED Requirements

### Requirement: Infrastructure must adapt JSONB metadata explicitly

The Postgres infrastructure adapters MUST adapt metadata objects through
the driver-specific `JSONB` wrapper before executing write statements.

#### Scenario: Memory writes use explicit JSONB adaptation

- **WHEN** a memory record is inserted or updated through the Postgres
  repository
- **THEN** the `metadata` parameter is wrapped for `JSONB` adaptation
- **AND** the adapter does not pass a raw Python `dict` directly to the
  driver placeholder

#### Scenario: Other repository writes use the same JSONB adaptation

- **WHEN** knowledge, knowledge-link, or execution records are inserted
  or updated through the Postgres repositories
- **THEN** each `metadata` parameter is wrapped for `JSONB` adaptation
- **AND** the adaptation logic remains confined to infrastructure
