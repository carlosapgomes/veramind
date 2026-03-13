# AGENTS.md

## 1. Stack and Versions

- MVP primary language: TypeScript
- Runtime: Node.js 22 LTS
- Package manager: npm
- Testing: Vitest
- Quality tooling: ESLint, Prettier, and markdownlint-cli
- Target persistence architecture: Postgres + pgvector
- Intended agent runtime: pi-mono

## 2. Validation Commands (Quality Gate)

- Required basic check: `git status --short`
- Documentation and markdown: `bash scripts/markdown-lint.sh`
- Unit tests: `npm run test`
- Code lint: `npm run lint`
- Type-check: `npm run typecheck`

## 3. Essential Commands (Local Operation)

### Basic operation

```bash
git status --short
git branch --show-current
bash scripts/markdown-lint.sh
```

### TypeScript operation

```bash
npm install
npm run test
npm run lint
npm run typecheck
```

## 4. Architecture and Constraints

- Define explicit module boundaries and keep dependencies unidirectional.
- Separate the system into `agent runtime`, `memory layer`,
  `tool layer`, and `knowledge system`.
- Allow the runtime to depend on memory, tool, and knowledge contracts;
  do not allow reverse dependencies.
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
- Run the validation commands from section 2.
- Update tasks, specs, and bilingual document mirrors.
- Stop and ask for confirmation before starting the next slice.

## 8. Definition of Done (DoD)

- [ ] Build/check completes without errors
- [ ] Relevant tests are passing
- [ ] Lint and type-check pass without relevant errors
- [ ] Specs and docs are updated when needed
- [ ] Bilingual document pairs remain synchronized
- [ ] Commit message is clear and traceable
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
If a touched document is bilingual, update both language versions.
Run section 2 validation commands, update artifacts, then STOP and ask
for confirmation.
```

<!-- generated-by: agents-md-generator -->
