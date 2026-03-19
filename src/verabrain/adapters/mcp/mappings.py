"""Request and response mappings between MCP payloads and application contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Mapping

from verabrain.application.contracts import (
    CaptureKnowledgeRequest,
    ContextBundle,
    ContextBundleRequest,
    LinkKnowledgeItemsRequest,
    ReviewQueueRequest,
    SaveExecutionRequest,
    SaveMemoryRequest,
    SearchExecutionRequest,
    SearchKnowledgeRequest,
    SearchMemoryRequest,
)
from verabrain.application.ports import (
    ExecutionRecord,
    KnowledgeLinkRecord,
    KnowledgeRecord,
    MemoryRecord,
)


def _require_str(args: Mapping[str, object], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' must be a non-empty string")
    return value


def _optional_str(args: Mapping[str, object], key: str) -> str | None:
    value = args.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' must be a non-empty string when provided")
    return value


def _optional_int(args: Mapping[str, object], key: str, *, default: int) -> int:
    value = args.get(key, default)
    if not isinstance(value, int):
        raise ValueError(f"'{key}' must be an integer")
    return value


def _optional_float(args: Mapping[str, object], key: str) -> float | None:
    value = args.get(key)
    if value is None:
        return None
    if not isinstance(value, int | float):
        raise ValueError(f"'{key}' must be numeric when provided")
    return float(value)


def _optional_metadata(args: Mapping[str, object]) -> Mapping[str, object]:
    value = args.get("metadata")
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("'metadata' must be an object when provided")
    return {str(key): nested for key, nested in value.items()}


def _optional_states(args: Mapping[str, object]) -> tuple[str, ...]:
    value = args.get("states")
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("'states' must be an array of strings when provided")
    return tuple(value)


def _parse_datetime(value: str, *, key: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"'{key}' must be a valid ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _optional_datetime(args: Mapping[str, object], key: str) -> datetime | None:
    value = args.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"'{key}' must be an ISO-8601 string when provided")
    return _parse_datetime(value, key=key)


def save_memory_args_to_request(args: Mapping[str, object]) -> SaveMemoryRequest:
    return SaveMemoryRequest(
        text=_require_str(args, "text"),
        type=_require_str(args, "type"),
        scope=_require_str(args, "scope"),
        source=_require_str(args, "source"),
        salience=_optional_float(args, "salience"),
        metadata=_optional_metadata(args),
    )


def search_memory_args_to_request(args: Mapping[str, object]) -> SearchMemoryRequest:
    return SearchMemoryRequest(
        text=_require_str(args, "text"),
        limit=_optional_int(args, "limit", default=10),
        min_salience=_optional_float(args, "min_salience"),
    )


def capture_knowledge_args_to_request(
    args: Mapping[str, object],
) -> CaptureKnowledgeRequest:
    return CaptureKnowledgeRequest(
        title=_require_str(args, "title"),
        text=_require_str(args, "text"),
        kind=_require_str(args, "kind"),
        source=_require_str(args, "source"),
        metadata=_optional_metadata(args),
    )


def search_knowledge_args_to_request(
    args: Mapping[str, object],
) -> SearchKnowledgeRequest:
    return SearchKnowledgeRequest(
        text=_require_str(args, "text"),
        limit=_optional_int(args, "limit", default=10),
        related_to=_optional_str(args, "related_to"),
    )


def link_knowledge_args_to_request(
    args: Mapping[str, object],
) -> LinkKnowledgeItemsRequest:
    return LinkKnowledgeItemsRequest(
        left_id=_require_str(args, "left_id"),
        right_id=_require_str(args, "right_id"),
        relation=_require_str(args, "relation"),
        metadata=_optional_metadata(args),
    )


def save_execution_args_to_request(args: Mapping[str, object]) -> SaveExecutionRequest:
    return SaveExecutionRequest(
        title=_require_str(args, "title"),
        kind=_require_str(args, "kind"),
        state=_require_str(args, "state"),
        source=_require_str(args, "source"),
        project_id=_optional_str(args, "project_id"),
        due_at=_optional_datetime(args, "due_at"),
        review_at=_optional_datetime(args, "review_at"),
        metadata=_optional_metadata(args),
    )


def search_execution_args_to_request(
    args: Mapping[str, object],
) -> SearchExecutionRequest:
    return SearchExecutionRequest(
        limit=_optional_int(args, "limit", default=50),
        states=_optional_states(args),
        project_id=_optional_str(args, "project_id"),
        due_before=_optional_datetime(args, "due_before"),
        review_before=_optional_datetime(args, "review_before"),
    )


def get_context_bundle_args_to_request(
    args: Mapping[str, object],
) -> ContextBundleRequest:
    return ContextBundleRequest(
        query=_require_str(args, "query"),
        memory_limit=_optional_int(args, "memory_limit", default=5),
        knowledge_limit=_optional_int(args, "knowledge_limit", default=5),
        execution_limit=_optional_int(args, "execution_limit", default=5),
    )


def list_review_queue_args_to_request(
    args: Mapping[str, object],
) -> ReviewQueueRequest:
    reference_at = _optional_datetime(args, "reference_at")
    if reference_at is None:
        raise ValueError("'reference_at' must be provided")
    return ReviewQueueRequest(
        reference_at=reference_at,
        limit=_optional_int(args, "limit", default=20),
    )


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def memory_record_to_mcp(record: MemoryRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "text": record.text,
        "type": record.type,
        "scope": record.scope,
        "salience": record.salience,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "last_used_at": _serialize_datetime(record.last_used_at),
        "source": record.source,
        "embedding": list(record.embedding) if record.embedding else None,
        "metadata": dict(record.metadata),
    }


def knowledge_record_to_mcp(record: KnowledgeRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "title": record.title,
        "text": record.text,
        "kind": record.kind,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "source": record.source,
        "metadata": dict(record.metadata),
    }


def knowledge_link_record_to_mcp(link: KnowledgeLinkRecord) -> dict[str, object]:
    return {
        "id": link.id,
        "left_id": link.left_id,
        "right_id": link.right_id,
        "relation": link.relation,
        "created_at": link.created_at.isoformat(),
        "metadata": dict(link.metadata),
    }


def execution_record_to_mcp(record: ExecutionRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "title": record.title,
        "kind": record.kind,
        "state": record.state,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "source": record.source,
        "project_id": record.project_id,
        "due_at": _serialize_datetime(record.due_at),
        "review_at": _serialize_datetime(record.review_at),
        "metadata": dict(record.metadata),
    }


def context_bundle_to_mcp(bundle: ContextBundle) -> dict[str, object]:
    return {
        "memories": [memory_record_to_mcp(record) for record in bundle.memories],
        "knowledge": [knowledge_record_to_mcp(record) for record in bundle.knowledge],
        "execution": [execution_record_to_mcp(record) for record in bundle.execution],
    }
