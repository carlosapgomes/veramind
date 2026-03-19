#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv not found. Install uv to format markdown." >&2
  exit 1
fi

mapfile -d '' files < <(find . -type f -name '*.md' \
  -not -path './.venv/*' \
  -not -path './node_modules/*' \
  -not -path './.pi/*' \
  -not -path './.codex/*' \
  -not -path './.git/*' \
  -not -path './texts/*' \
  -print0)

if [ ${#files[@]} -eq 0 ]; then
  echo "No .md files found."
  exit 0
fi

uv run mdformat "${files[@]}"
bash scripts/markdown-lint.sh

echo "Markdown formatted and validated successfully."
