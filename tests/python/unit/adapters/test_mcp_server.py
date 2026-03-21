from __future__ import annotations

import logging
from typing import Callable, Mapping, cast

import pytest

from verabrain.adapters.mcp import (
    MissingMCPDependencyError,
    build_mcp_server,
    build_server_definition,
    run_stdio_server,
)
from verabrain.adapters.mcp.server import MCPResponse, MCPServerDefinition
from verabrain.application import VeraBrainApplication


class FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Mapping[str, object]]] = []
        self.tools = (
            {
                "name": "save_memory",
                "description": "Persist a durable memory.",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "search_memory",
                "description": "Search durable memories.",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
            },
        )

    def list_tools(self) -> tuple[dict[str, object], ...]:
        return self.tools

    def dispatch(self, tool_name: str, args: Mapping[str, object]) -> MCPResponse:
        self.calls.append((tool_name, args))
        return {"ok": True, "tool": tool_name, "result": dict(args)}


class FakeMCPServer:
    def __init__(self, server_name: str, *, json_response: bool = True) -> None:
        self.server_name = server_name
        self.json_response = json_response
        self.registered: list[tuple[str | None, str | None, object]] = []
        self.transport_runs: list[str] = []

    def tool(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ):
        def decorator(handler):
            self.registered.append((name, description, handler))
            return handler

        return decorator

    def run(self, *, transport: str = "stdio") -> None:
        self.transport_runs.append(transport)


def test_build_server_definition_preserves_tool_surface_and_dispatches() -> None:
    adapter = FakeAdapter()

    definition = build_server_definition(adapter, server_name="VeraBrain Test")

    assert definition.name == "VeraBrain Test"
    assert [tool.name for tool in definition.tools] == ["save_memory", "search_memory"]
    assert definition.tools[0].input_schema["required"] == ["text"]

    response = definition.tools[0].handler({"text": "Remember this"})

    assert response["ok"] is True
    assert adapter.calls == [("save_memory", {"text": "Remember this"})]


def test_build_mcp_server_registers_tool_handlers_with_json_responses() -> None:
    adapter = FakeAdapter()
    definition = build_server_definition(adapter)

    server = cast(
        FakeMCPServer,
        build_mcp_server(definition, server_factory=FakeMCPServer),
    )

    assert server.server_name == "VeraBrain"
    assert server.json_response is True
    assert [name for name, _, _ in server.registered] == ["save_memory", "search_memory"]

    _, _, handler = server.registered[0]
    response = cast(Callable[..., MCPResponse], handler)
    result = response(text="Keep this fact")
    assert result["tool"] == "save_memory"
    assert adapter.calls[-1] == ("save_memory", {"text": "Keep this fact"})


def test_build_mcp_server_reports_missing_optional_sdk_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = MCPServerDefinition(name="VeraBrain", tools=())
    missing = MissingMCPDependencyError("missing mcp")

    def fake_load_server_factory() -> object:
        raise missing

    monkeypatch.setattr(
        "verabrain.adapters.mcp.server._load_server_factory",
        fake_load_server_factory,
    )

    with pytest.raises(MissingMCPDependencyError) as excinfo:
        build_mcp_server(definition)

    assert excinfo.value is missing


def test_run_stdio_server_uses_stdio_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    server = FakeMCPServer("VeraBrain")

    def fake_create_mcp_server(
        application: VeraBrainApplication,
        *,
        server_name: str = "VeraBrain",
        server_factory=None,
    ) -> FakeMCPServer:
        return server

    monkeypatch.setattr(
        "verabrain.adapters.mcp.server.create_mcp_server",
        fake_create_mcp_server,
    )

    result = run_stdio_server(cast(VeraBrainApplication, object()))

    assert result is server
    assert server.transport_runs == ["stdio"]


def test_run_stdio_server_emits_debug_startup_logs(
    monkeypatch: pytest.MonkeyPatch,
    caplog,
) -> None:
    server = FakeMCPServer("VeraBrain")

    def fake_create_mcp_server(
        application: VeraBrainApplication,
        *,
        server_name: str = "VeraBrain",
        server_factory=None,
    ) -> FakeMCPServer:
        return server

    monkeypatch.setattr(
        "verabrain.adapters.mcp.server.create_mcp_server",
        fake_create_mcp_server,
    )

    with caplog.at_level(logging.DEBUG, logger="verabrain.adapters.mcp.server"):
        run_stdio_server(cast(VeraBrainApplication, object()))

    assert "Starting VeraBrain MCP server over stdio" in caplog.text
    assert "is running over stdio" in caplog.text
