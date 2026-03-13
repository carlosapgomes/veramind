# AGENTS.md

## 1. Stack e Versoes

- Linguagem principal do MVP: TypeScript
- Runtime: Node.js 22 LTS
- Gerenciador de pacotes: npm
- Testes: Vitest
- Qualidade: ESLint, Prettier e markdownlint-cli
- Persistencia alvo da arquitetura: Postgres + pgvector
- Runtime de agente pretendido: pi-mono

## 2. Comandos de Validacao (Quality Gate)

- Verificacao basica obrigatoria: `git status --short`
- Documentacao/markdown: `bash scripts/markdown-lint.sh`
- Testes unitarios: `npm run test`
- Lint de codigo: `npm run lint`
- Type-check: `npm run typecheck`

## 3. Comandos Essenciais (Operacao Local)

### Operacao basica

```bash
git status --short
git branch --show-current
bash scripts/markdown-lint.sh
```

### Operacao TypeScript

```bash
npm install
npm run test
npm run lint
npm run typecheck
```

## 4. Arquitetura e Constraints

- Definir boundaries explicitos por modulo e manter dependencias
  unidirecionais.
- Separar o sistema em `agent runtime`, `memory layer`, `tool layer`
  e `knowledge system`.
- Permitir dependencia do runtime para contratos de memoria,
  ferramentas e conhecimento; nao permitir dependencia inversa.
- Expor ferramentas por wrappers controlados; evitar shell cru como
  interface publica.
- Manter regras de negocio fora da camada de apresentacao/CLI.

## 5. Politica de Testes

- TDD para novas funcionalidades e bugfixes criticos.
- Aplicar ciclo red-green-refactor nas mudancas de dominio e contratos.
- Priorizar testes unitarios; usar integracao para contratos e fluxos.
- Ao tocar legado sem testes, adicionar ao menos um teste de caracterizacao.
- Nao introduzir modulo novo sem cobertura de testes correspondente ao
  comportamento principal.

## 6. Stop Rule (CRUCIAL)

- Implementar uma task slice por vez.
- Rodar comandos de validacao da secao 2.
- Atualizar tasks/specs e parar para confirmacao do proximo slice.

## 7. Definition of Done (DoD)

- [ ] Build/check sem erros
- [ ] Testes relevantes passando
- [ ] Lint/type-check sem erros relevantes
- [ ] Specs/docs atualizadas quando necessario
- [ ] Commit com mensagem clara e rastreavel
- [ ] Boundaries modulares preservados

## 8. Anti-patterns Proibidos

- Nao criar classes/funcoes God object com responsabilidades demais.
- Nao deixar TODO/FIXME sem issue ou plano.
- Nao acoplar regras de negocio em camada de apresentacao.
- Nao criar dependencia ciclica entre runtime, memoria, ferramentas e
  conhecimento.
- Nao expor acesso irrestrito ao shell como ferramenta default do
  agente.

## 9. Prompt de Reentrada

```text
Read AGENTS.md and PROJECT_CONTEXT.md first.
Implement ONLY the next incomplete slice from tasks/spec.
Run section 2 validation commands, update artifacts, then STOP and ask confirmation.
```

<!-- generated-by: agents-md-generator -->
