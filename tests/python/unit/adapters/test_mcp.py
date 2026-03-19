from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from verabrain.adapters.mcp import (
    INITIAL_MCP_TOOLS,
    context_bundle_to_mcp,
    list_review_queue_args_to_request,
    save_memory_args_to_request,
    search_execution_args_to_request,
)
from verabrain.application import ContextBundle, ExecutionRecord, KnowledgeRecord, MemoryRecord


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


def test_initial_mcp_tools_cover_the_expected_contract_surface() -> None:
    tool_names = {tool["name"] for tool in INITIAL_MCP_TOOLS}

    assert tool_names == {
        "save_memory",
        "search_memory",
        "capture_knowledge",
        "search_knowledge",
        "link_knowledge_items",
        "save_execution",
        "search_execution",
        "get_context_bundle",
        "list_review_queue",
    }
    assert all(
        tool["parameters"]["additionalProperties"] is False
        for tool in INITIAL_MCP_TOOLS
    )


def test_save_memory_mapping_builds_a_typed_request() -> None:
    request = save_memory_args_to_request(
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
            "salience": 0.8,
            "metadata": {"channel": "chat"},
        }
    )

    assert request.type == "preference"
    assert request.scope == "long"
    assert request.metadata["channel"] == "chat"


def test_search_execution_mapping_parses_filters_and_datetimes() -> None:
    request = search_execution_args_to_request(
        {
            "limit": 5,
            "states": ["next", "waiting"],
            "due_before": "2026-03-20T10:00:00Z",
        }
    )

    assert request.limit == 5
    assert request.states == ("next", "waiting")
    assert request.due_before == datetime(2026, 3, 20, 10, 0, tzinfo=UTC)


def test_review_queue_mapping_requires_a_reference_time() -> None:
    request = list_review_queue_args_to_request(
        {"reference_at": "2026-03-19T12:00:00Z", "limit": 10}
    )

    assert request.limit == 10
    assert request.reference_at == _now()


def test_context_bundle_serialization_groups_domain_records() -> None:
    bundle = ContextBundle(
        memories=[
            MemoryRecord(
                id="mem-1",
                text="User prefers concise answers.",
                type="preference",
                scope="long",
                salience=0.9,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            )
        ],
        knowledge=[
            KnowledgeRecord(
                id="note-1",
                title="Hermes note",
                text="Hermes supports MCP.",
                kind="reference",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            )
        ],
        execution=[
            ExecutionRecord(
                id="task-1",
                title="Define MCP schemas",
                kind="task",
                state="next",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            )
        ],
    )

    response = context_bundle_to_mcp(bundle)
    memories = cast(list[dict[str, object]], response["memories"])
    knowledge = cast(list[dict[str, object]], response["knowledge"])
    execution = cast(list[dict[str, object]], response["execution"])

    assert memories[0]["type"] == "preference"
    assert knowledge[0]["kind"] == "reference"
    assert execution[0]["state"] == "next"
