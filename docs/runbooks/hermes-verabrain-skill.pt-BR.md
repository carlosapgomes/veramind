# Runbook do Skill Hermes VeraBrain

[English](./hermes-verabrain-skill.md)

Este runbook explica como instalar e usar o skill inicial `VeraBrain`
do Hermes para o MVP.

O skill é uma camada procedural sobre os MCP tools existentes do
VeraBrain. Ele não substitui:

- a configuração do servidor MCP do VeraBrain
- a fronteira já definida entre memória do Hermes e do VeraBrain
- os contratos de memória durável do VeraBrain

## Pré-requisitos

Antes de usar este skill, o caminho do MVP local já deve estar
funcionando:

- [Runbook do MVP Local](./local-mvp.pt-BR.md)

Ou seja:

- o Postgres do projeto está rodando via Docker Compose
- o servidor MCP do VeraBrain está configurado no Hermes por meio do
  launcher `verabrain-mcp-local-mvp`
- o Hermes já consegue chamar os MCP tools do VeraBrain

## Origem do skill

O artefato inicial do skill está em:

- [`hermes-skills/verabrain/SKILL.md`](../../hermes-skills/verabrain/SKILL.md)

## 1. Instalar o skill no Hermes

O Hermes carrega skills instalados a partir de `~/.hermes/skills/`.

Crie o diretório-alvo e copie o skill:

```bash
mkdir -p ~/.hermes/skills/verabrain
cp /home/carlos/projects/veramind/hermes-skills/verabrain/SKILL.md \
  ~/.hermes/skills/verabrain/SKILL.md
```

Se você preferir mantê-lo sincronizado diretamente do repositório
durante o trabalho local, pode usar um symlink:

```bash
mkdir -p ~/.hermes/skills/verabrain
ln -sf /home/carlos/projects/veramind/hermes-skills/verabrain/SKILL.md \
  ~/.hermes/skills/verabrain/SKILL.md
```

## 2. Confirmar que o skill está disponível

Depois de instalado, o Hermes deve expor esse skill como o comando
`/verabrain`.

O nome vem do frontmatter do skill:

- `name: verabrain`

## 3. Como usar o skill

Use `/verabrain` quando quiser que o Hermes carregue a orientação
procedural para decidir entre:

- `stay-local`
- `save-to-verabrain`
- `retrieve-from-verabrain`

Uso típico:

```text
/verabrain Save this idea in VeraBrain: I want a personal assistant
workflow for vascular surgery study notes.
```

Ou:

```text
/verabrain What do we already have in VeraBrain about my PKM roadmap?
```

## 4. Comportamento esperado

Depois que o skill for invocado:

- o Hermes deve permanecer local por padrão quando memória durável não
  for necessária
- o Hermes deve usar `save_memory` para intentos explícitos de save
  durável
- o Hermes deve usar `search_memory` para recall bounded por tópico
- o Hermes deve usar `get_context_bundle` para contexto bounded de
  trabalho

O skill não deve levar o Hermes a:

- salvar duravelmente sem intento explícito forte
- tratar o VeraBrain como substituto da memória de sessão do Hermes
- inventar caminhos de storage ou retrieval fora dos MCP tools

## 5. Padrões práticos de prompt

Exemplos que devem empurrar o Hermes para durable save:

- `/verabrain Remember this project decision for later: use MCP-first
  before considering a native Hermes plugin.`
- `/verabrain Register this idea in VeraBrain: create a study workflow
  for vascular surgery notes.`

Exemplos que devem empurrar o Hermes para durable recall:

- `/verabrain What do we already have stored about the local MVP?`
- `/verabrain Bring back the bounded context we saved for the Postgres
  MCP local MVP.`

Exemplos que devem permanecer locais mesmo com o skill carregado:

- `/verabrain What were we doing in the last few messages?`
- `/verabrain Continue the current task.`

## 6. Observações

- O skill é orientação, não garantia. O Hermes ainda precisa do servidor
  MCP do VeraBrain configurado e acessível.
- Se o servidor MCP estiver indisponível, o Hermes não deve fingir que
  o save durável ou o durable recall funcionaram.
- Mantenha o skill alinhado com o change ativo do OpenSpec e com a
  surface real dos MCP tools.
