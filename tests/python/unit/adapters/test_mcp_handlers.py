from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence, cast

from verabrain.adapters.mcp import MCPApplicationAdapter
from verabrain.application import (
    ExecutionQuery,
    ExecutionRecord,
    ExecutionRepository,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    KnowledgeRepository,
    MemoryRecord,
    MemoryRepository,
    PersistenceUnitOfWork,
    VeraBrainApplication,
)


def _now() -> datetime:
    return datetime(2026, 3, 19, 12, 0, tzinfo=UTC)


class AdapterMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self.saved: MemoryRecord | None = None
        self.similar_result: Sequence[MemoryRecord] = ()
        self.result = [
            MemoryRecord(
                id="mem-existing",
                text="User prefers concise answers.",
                type="preference",
                scope="long",
                salience=0.9,
                created_at=_now(),
                updated_at=_now(),
                last_used_at=None,
                source="manual",
            )
        ]

    def get(self, record_id: str) -> MemoryRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        self.saved = record
        return record

    def find_similar(self, *, text: str, limit: int = 5) -> Sequence[MemoryRecord]:
        return self.similar_result[:limit]

    def search(self, query):  # type: ignore[no-untyped-def]
        return self.result[: query.limit]


class AdapterKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self.saved: KnowledgeRecord | None = None
        self.saved_link: KnowledgeLinkRecord | None = None
        self.result = [
            KnowledgeRecord(
                id="note-existing",
                title="Hermes note",
                text="Hermes supports MCP.",
                kind="reference",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
            )
        ]

    def get(self, record_id: str) -> KnowledgeRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def save(self, record: KnowledgeRecord) -> KnowledgeRecord:
        self.saved = record
        return record

    def search(self, query):  # type: ignore[no-untyped-def]
        return self.result[: query.limit]

    def save_link(self, link: KnowledgeLinkRecord) -> KnowledgeLinkRecord:
        self.saved_link = link
        return link

    def list_links(self, record_id: str) -> Sequence[KnowledgeLinkRecord]:
        if self.saved_link and self.saved_link.left_id == record_id:
            return [self.saved_link]
        return []


class AdapterExecutionRepository(ExecutionRepository):
    def __init__(self) -> None:
        self.saved: ExecutionRecord | None = None
        self.result = [
            ExecutionRecord(
                id="task-existing",
                title="Define handlers",
                kind="task",
                state="next",
                created_at=_now(),
                updated_at=_now(),
                source="manual",
                review_at=_now(),
            )
        ]
        self.last_review_reference: datetime | None = None

    def get(self, record_id: str) -> ExecutionRecord | None:
        return self.saved if self.saved and self.saved.id == record_id else None

    def save(self, record: ExecutionRecord) -> ExecutionRecord:
        self.saved = record
        return record

    def search(self, query: ExecutionQuery) -> Sequence[ExecutionRecord]:
        return self.result[: query.limit]

    def list_due_for_review(
        self, *, reference_at: datetime, limit: int = 50
    ) -> Sequence[ExecutionRecord]:
        self.last_review_reference = reference_at
        return self.result[:limit]


class AdapterUnitOfWork(PersistenceUnitOfWork):
    def __init__(self) -> None:
        self._memories = AdapterMemoryRepository()
        self._knowledge = AdapterKnowledgeRepository()
        self._execution = AdapterExecutionRepository()
        self.commits = 0
        self.rollbacks = 0

    @property
    def memories(self) -> MemoryRepository:
        return self._memories

    @property
    def knowledge(self) -> KnowledgeRepository:
        return self._knowledge

    @property
    def execution(self) -> ExecutionRepository:
        return self._execution

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _build_adapter() -> tuple[MCPApplicationAdapter, AdapterUnitOfWork]:
    unit_of_work = AdapterUnitOfWork()
    application = VeraBrainApplication(
        unit_of_work=unit_of_work,
        clock=_now,
        id_generator=lambda: "fixed-id",
    )
    return MCPApplicationAdapter(application=application), unit_of_work


def test_dispatch_routes_save_memory_to_the_application_service() -> None:
    adapter, unit_of_work = _build_adapter()

    response = adapter.dispatch(
        "save_memory",
        {
            "text": "User prefers concise answers.",
            "type": "preference",
            "scope": "long",
            "source": "manual",
        },
    )

    assert response["ok"] is True
    result = cast(dict[str, object], response["result"])
    assert result["id"] == "fixed-id"
    assert unit_of_work.commits == 1


def test_dispatch_returns_grouped_context_bundle_payloads() -> None:
    adapter, _ = _build_adapter()

    response = adapter.dispatch("get_context_bundle", {"query": "Hermes"})

    assert response["ok"] is True
    result = cast(dict[str, object], response["result"])
    memories = cast(list[dict[str, object]], result["memories"])
    knowledge = cast(list[dict[str, object]], result["knowledge"])
    execution = cast(list[dict[str, object]], result["execution"])
    assert memories[0]["type"] == "preference"
    assert knowledge[0]["kind"] == "reference"
    assert execution[0]["state"] == "next"


def test_dispatch_maps_review_queue_requests_to_execution_service() -> None:
    adapter, unit_of_work = _build_adapter()

    response = adapter.dispatch(
        "list_review_queue",
        {"reference_at": "2026-03-19T12:00:00Z", "limit": 1},
    )

    assert response["ok"] is True
    result = cast(dict[str, object], response["result"])
    items = cast(list[dict[str, object]], result["items"])
    execution_repository = cast(AdapterExecutionRepository, unit_of_work.execution)
    assert execution_repository.last_review_reference == _now()
    assert items[0]["state"] == "next"


def test_dispatch_reports_invalid_argument_errors_without_raising() -> None:
    adapter, _ = _build_adapter()

    response = adapter.dispatch("save_memory", {"type": "preference"})

    assert response["ok"] is False
    error = cast(dict[str, object], response["error"])
    assert error["code"] == "invalid_arguments"


def test_dispatch_reports_unknown_tools_without_raising() -> None:
    adapter, _ = _build_adapter()

    response = adapter.dispatch("unknown_tool", {})

    assert response == {
        "ok": False,
        "tool": "unknown_tool",
        "error": {
            "code": "unknown_tool",
            "message": "Unknown MCP tool 'unknown_tool'",
        },
    }
