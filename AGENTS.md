# AGENTS.md

## 1. Stack and Versions

- Primary implementation direction: Python 3.11+
- Python environment and package management: `uv`
- Repository implementation scaffold: Python package under
  `src/verabrain`
- Current repository tests: pytest
- Current repository quality tooling: Ruff, Pyright, mdformat, and
  PyMarkdown
- Target persistence architecture: Postgres + pgvector
- Intended runtime context: Hermes Agent with MCP-first integration

## 2. Validation Commands (Quality Gate)

- Required basic check: `git status --short`
- Documentation and markdown: `bash scripts/markdown-lint.sh`
- Python unit tests: `uv run pytest`
- Python lint: `uv run ruff check .`
- Python type-check: `uv run pyright`

## 3. Essential Commands (Local Operation)

### Basic operation

```bash
git status --short
git branch --show-current
bash scripts/markdown-lint.sh
```

### Python operation

```bash
uv sync
bash scripts/markdown-lint.sh
uv run pytest
uv run ruff check .
uv run pyright
```

## 4. Architecture and Constraints

- Define explicit module boundaries and keep dependencies unidirectional.
- Prefer vertical slices that deliver observable end-to-end behavior
  across the relevant layers of the system.
- Avoid horizontal implementation slices limited to a single layer
  unless the slice is explicitly design-only or infrastructure-only by
  decision.
- Separate the system into `agent runtime`, `memory layer`,
  `tool layer`, and `knowledge system`.
- Treat Hermes Agent as the current runtime shell and VeraBrain as a
  core-plus-adapters subsystem.
- Allow the runtime to depend on memory, tool, and knowledge contracts;
  do not allow reverse dependencies.
- Keep VeraBrain core logic independent from MCP and Hermes plugin
  adapters.
- Expose capabilities through controlled wrappers; avoid raw shell as a
  public interface.
- Keep business rules out of presentation and CLI layers.

## 5. Testing Policy

- Use TDD for new features and critical bug fixes.
- Apply the red-green-refactor cycle to domain and contract changes.
- Prioritize unit tests; use integration tests for contracts and flows.
- When touching legacy code without tests, add at least one
  characterization test.
- Do not introduce a new module without tests that cover its primary
  behavior.

## 6. Documentation Language Policy

- `AGENTS.md`, `PROJECT_CONTEXT.md`, ADRs, and active OpenSpec artifacts
  must use American English as the default language.
- `README.md` and the relevant documents under `docs/` must have a
  synchronized `pt-BR` mirror placed next to the English file.
- Every change to a bilingual document must update both language
  versions in the same slice.
- English documents must link to the Portuguese mirror at the top.
- Portuguese mirrors should link back to the English source at the top.

## 7. Stop Rule (CRUCIAL)

- Implement one task slice at a time.
- Default to a small vertical slice that touches the necessary layers
  to prove behavior, not a broad layer-by-layer expansion.
- Run the validation commands from section 2.
- Update tasks, specs, and bilingual document mirrors.
- Commit the completed slice with a clear and traceable message.
- Push the current branch after the slice passes validation.
- Stop and ask for confirmation before starting the next slice.

## 8. Definition of Done (DoD)

- [ ] Build/check completes without errors
- [ ] Relevant tests are passing
- [ ] Lint and type-check pass without relevant errors
- [ ] Specs and docs are updated when needed
- [ ] Bilingual document pairs remain synchronized
- [ ] Commit message is clear and traceable
- [ ] Current branch is pushed after the successful slice
- [ ] Module boundaries remain preserved

## 9. Prohibited Anti-Patterns

- Do not create God objects with too many responsibilities.
- Do not leave TODO/FIXME items without an issue or a concrete plan.
- Do not couple business rules into the presentation layer.
- Do not create cyclical dependencies between runtime, memory, tools,
  and knowledge.
- Do not expose unrestricted shell access as the default agent tool.

## 10. Reentry Prompt

```text
Read AGENTS.md and PROJECT_CONTEXT.md first.
Implement ONLY the next incomplete slice from tasks/spec.
Prefer a vertical slice that proves observable behavior across the
necessary layers unless the task is explicitly design-only.
If a touched document is bilingual, update both language versions.
Respect the Python-first Hermes-centered direction unless an ADR changes
it again.
Run section 2 validation commands, update artifacts, commit and push
the successful slice, then STOP and ask for confirmation.
```

<!-- generated-by: agents-md-generator -->
