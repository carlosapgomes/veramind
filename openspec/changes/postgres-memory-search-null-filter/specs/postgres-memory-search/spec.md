# Spec: Postgres Memory Search Null Filter

## Status

Proposed

## Requirements

### Requirement: Omit optional salience placeholders when no salience filter is requested

The Postgres memory repository MUST NOT build lexical or semantic search
queries that rely on a nullable typed placeholder for `min_salience`
when the caller does not request a salience threshold.

When no salience threshold is present, the repository MUST omit that SQL
predicate instead of sending an untyped `NULL` parameter into the query.

#### Scenario: Lexical memory search omits absent salience threshold

- **WHEN** the repository builds a lexical candidate query
- **AND** `min_salience` is absent
- **THEN** the SQL omits the salience predicate
- **AND** the query parameters do not include a nullable salience value

#### Scenario: Semantic memory search omits absent salience threshold

- **WHEN** the repository builds a semantic candidate query
- **AND** `min_salience` is absent
- **THEN** the SQL omits the salience predicate
- **AND** the query parameters do not include a nullable salience value

### Requirement: Preserve explicit salience filtering when requested

The Postgres memory repository MUST keep explicit salience filtering
when `min_salience` is provided.

#### Scenario: Memory search applies explicit salience threshold

- **WHEN** the repository builds a memory candidate query
- **AND** `min_salience` is provided
- **THEN** the SQL includes a salience predicate
- **AND** the query parameters include the explicit salience value
