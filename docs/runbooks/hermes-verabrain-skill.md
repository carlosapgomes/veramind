# Hermes VeraBrain Skill Runbook

[Portuguese (Brazil)](./hermes-verabrain-skill.pt-BR.md)

This runbook explains how to install and use the initial Hermes
`VeraBrain` skill for the MVP.

The skill is procedural guidance over the existing VeraBrain MCP tools.
It does not replace:

- the VeraBrain MCP server configuration
- the existing Hermes vs VeraBrain memory boundary
- the VeraBrain durable-memory contracts

## Prerequisites

Before using this skill, the local MVP path should already be working:

- [Local MVP Runbook](./local-mvp.md)

That means:

- project-local Postgres is running through Docker Compose
- the VeraBrain MCP server is configured for Hermes through the
  `verabrain-mcp-local-mvp` launcher
- Hermes can already call the VeraBrain MCP tools

## Skill Source

The initial skill artifact lives in:

- [`hermes-skills/verabrain/SKILL.md`](../../hermes-skills/verabrain/SKILL.md)

## 1. Install the Skill into Hermes

Hermes loads installed skills from `~/.hermes/skills/`.

Create the target directory and copy the skill:

```bash
mkdir -p ~/.hermes/skills/verabrain
cp /home/carlos/projects/veramind/hermes-skills/verabrain/SKILL.md \
  ~/.hermes/skills/verabrain/SKILL.md
```

If you prefer to keep it synced directly from the repo during local MVP
work, you can symlink it instead:

```bash
mkdir -p ~/.hermes/skills/verabrain
ln -sf /home/carlos/projects/veramind/hermes-skills/verabrain/SKILL.md \
  ~/.hermes/skills/verabrain/SKILL.md
```

## 2. Confirm the Skill Is Available

Once installed, Hermes should expose the skill as the `/verabrain`
slash command.

The skill name comes from the skill frontmatter:

- `name: verabrain`

## 3. How to Use the Skill

Use `/verabrain` when you want Hermes to load the procedural guidance
for deciding between:

- `stay-local`
- `save-to-verabrain`
- `retrieve-from-verabrain`

Typical use:

```text
/verabrain Save this idea in VeraBrain: I want a personal assistant workflow for vascular surgery study notes.
```

Or:

```text
/verabrain What do we already have in VeraBrain about my PKM roadmap?
```

## 4. Expected Behavior

After the skill is invoked:

- Hermes should stay local by default when durable memory is not needed
- Hermes should use `save_memory` for explicit durable-save intent
- Hermes should use `search_memory` for bounded topic recall
- Hermes should use `get_context_bundle` for bounded working context

The skill should not cause Hermes to:

- save durably without strong explicit intent
- treat VeraBrain as a replacement for Hermes session memory
- invent new storage or retrieval paths outside the MCP tools

## 5. Practical Prompt Patterns

Examples that should push Hermes toward durable save:

- `/verabrain Remember this project decision for later: use MCP-first before considering a native Hermes plugin.`
- `/verabrain Register this idea in VeraBrain: create a study workflow for vascular surgery notes.`

Examples that should push Hermes toward durable recall:

- `/verabrain What do we already have stored about the local MVP?`
- `/verabrain Bring back the bounded context we saved for the Postgres MCP local MVP.`

Examples that should remain local even with the skill loaded:

- `/verabrain What were we doing in the last few messages?`
- `/verabrain Continue the current task.`

## 6. Notes

- The skill is guidance, not a guarantee. Hermes still needs the
  VeraBrain MCP server configured and reachable.
- If the MCP server is unavailable, Hermes should not pretend that
  durable save or durable recall succeeded.
- Keep the skill aligned with the active OpenSpec change and the actual
  MCP tool surface.
