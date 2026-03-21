from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_PATH = REPO_ROOT / "hermes-skills" / "verabrain" / "SKILL.md"
RUNBOOK_PATH = REPO_ROOT / "docs" / "runbooks" / "hermes-verabrain-skill.md"
LOCAL_MVP_RUNBOOK_PATH = REPO_ROOT / "docs" / "runbooks" / "local-mvp.md"


def test_verabrain_skill_and_runbook_stay_aligned_with_mcp_surface() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    for tool_name in ("save_memory", "search_memory", "get_context_bundle"):
        assert tool_name in skill
        assert tool_name in runbook

    for decision_class in (
        "stay-local",
        "save-to-verabrain",
        "retrieve-from-verabrain",
    ):
        assert decision_class in skill

    assert "/verabrain" in runbook
    assert "~/.hermes/skills/verabrain" in runbook


def test_skill_runbook_stays_aligned_with_local_mvp_launcher() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    local_mvp = LOCAL_MVP_RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "verabrain-mcp-local-mvp" in runbook
    assert "verabrain-mcp-local-mvp" in local_mvp
    assert "Local MVP Runbook" in runbook
