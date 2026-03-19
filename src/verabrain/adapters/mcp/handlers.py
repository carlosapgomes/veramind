"""MCP-facing adapter that dispatches tool calls to application services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from verabrain.application import VeraBrainApplication

from .mappings import (
    capture_knowledge_args_to_request,
    context_bundle_to_mcp,
    execution_record_to_mcp,
    get_context_bundle_args_to_request,
    knowledge_link_record_to_mcp,
    knowledge_record_to_mcp,
    link_knowledge_args_to_request,
    list_review_queue_args_to_request,
    memory_record_to_mcp,
    save_execution_args_to_request,
    save_memory_args_to_request,
    search_execution_args_to_request,
    search_knowledge_args_to_request,
    search_memory_args_to_request,
)
from .schemas import INITIAL_MCP_TOOLS

ToolHandler = Callable[[Mapping[str, object]], dict[str, object]]


@dataclass(slots=True)
class MCPApplicationAdapter:
    """Thin MCP adapter over the callable VeraBrain application services."""

    application: VeraBrainApplication

    def list_tools(self) -> tuple[dict[str, object], ...]:
        """Return the declared initial MCP tool definitions."""

        return INITIAL_MCP_TOOLS

    def dispatch(self, tool_name: str, args: Mapping[str, object]) -> dict[str, object]:
        """Dispatch a tool call and return a JSON-serializable MCP response."""

        try:
            handler = self._handlers()[tool_name]
        except KeyError:
            return self._error(
                tool_name=tool_name,
                code="unknown_tool",
                message=f"Unknown MCP tool '{tool_name}'",
            )

        try:
            result = handler(args)
        except ValueError as exc:
            return self._error(
                tool_name=tool_name,
                code="invalid_arguments",
                message=str(exc),
            )
        except Exception as exc:  # pragma: no cover - exercised through adapter users
            return self._error(
                tool_name=tool_name,
                code="application_error",
                message=str(exc),
            )
        return {"ok": True, "tool": tool_name, "result": result}

    def _handlers(self) -> dict[str, ToolHandler]:
        return {
            "save_memory": self._save_memory,
            "search_memory": self._search_memory,
            "capture_knowledge": self._capture_knowledge,
            "search_knowledge": self._search_knowledge,
            "link_knowledge_items": self._link_knowledge_items,
            "save_execution": self._save_execution,
            "search_execution": self._search_execution,
            "get_context_bundle": self._get_context_bundle,
            "list_review_queue": self._list_review_queue,
        }

    @staticmethod
    def _error(*, tool_name: str, code: str, message: str) -> dict[str, object]:
        return {
            "ok": False,
            "tool": tool_name,
            "error": {"code": code, "message": message},
        }

    def _save_memory(self, args: Mapping[str, object]) -> dict[str, object]:
        request = save_memory_args_to_request(args)
        record = self.application.memory.save(request)
        return memory_record_to_mcp(record)

    def _search_memory(self, args: Mapping[str, object]) -> dict[str, object]:
        request = search_memory_args_to_request(args)
        records = self.application.memory.search(request)
        return {"items": [memory_record_to_mcp(record) for record in records]}

    def _capture_knowledge(self, args: Mapping[str, object]) -> dict[str, object]:
        request = capture_knowledge_args_to_request(args)
        record = self.application.knowledge.capture(request)
        return knowledge_record_to_mcp(record)

    def _search_knowledge(self, args: Mapping[str, object]) -> dict[str, object]:
        request = search_knowledge_args_to_request(args)
        records = self.application.knowledge.search(request)
        return {"items": [knowledge_record_to_mcp(record) for record in records]}

    def _link_knowledge_items(self, args: Mapping[str, object]) -> dict[str, object]:
        request = link_knowledge_args_to_request(args)
        link = self.application.knowledge.link(request)
        return knowledge_link_record_to_mcp(link)

    def _save_execution(self, args: Mapping[str, object]) -> dict[str, object]:
        request = save_execution_args_to_request(args)
        record = self.application.execution.save(request)
        return execution_record_to_mcp(record)

    def _search_execution(self, args: Mapping[str, object]) -> dict[str, object]:
        request = search_execution_args_to_request(args)
        records = self.application.execution.search(request)
        return {"items": [execution_record_to_mcp(record) for record in records]}

    def _get_context_bundle(self, args: Mapping[str, object]) -> dict[str, object]:
        request = get_context_bundle_args_to_request(args)
        bundle = self.application.context.get_bundle(request)
        return context_bundle_to_mcp(bundle)

    def _list_review_queue(self, args: Mapping[str, object]) -> dict[str, object]:
        request = list_review_queue_args_to_request(args)
        records = self.application.execution.list_review_queue(request)
        return {"items": [execution_record_to_mcp(record) for record in records]}
