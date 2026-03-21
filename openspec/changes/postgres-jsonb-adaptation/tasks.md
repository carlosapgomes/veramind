# Tasks

- [x] Wrap Postgres `JSONB` metadata parameters with the proper `psycopg`
      adapter in all repository write paths
- [x] Add tests that assert metadata is no longer passed as raw `dict`
      values to the Postgres driver
