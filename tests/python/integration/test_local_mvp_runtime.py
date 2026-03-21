from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
import pytest

from verabrain.application import MemoryEmbeddingProvider, VeraBrainApplication
from verabrain.infrastructure import InMemoryUnitOfWork, PostgresRuntimeConfigurationError
from verabrain.runtime.local_mvp import run_local_mvp


def _now() -> datetime:
    return datetime(2026, 3, 20, 12, 0, tzinfo=UTC)


def _id_sequence() -> Iterator[str]:
    for value in ("mem-1", "mem-2", "mem-3"):
        yield value


class StubMemoryEmbeddingProvider(MemoryEmbeddingProvider):
    def embed_memory_text(self, text: str) -> tuple[float, ...] | None:
        return (0.1, 0.2, 0.3)


class RecordingMCPServer:
    def __init__(self, server_name: str, *, json_response: bool = True) -> None:
        self.server_name = server_name
        self.json_response = json_response
        self.handlers: dict[str, Callable[..., dict[str, object]]] = {}
        self.transports: list[str] = []

    def tool(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[[Callable[..., dict[str, object]]], Callable[..., dict[str, object]]]:
        del description

        def decorator(
            handler: Callable[..., dict[str, object]]
        ) -> Callable[..., dict[str, object]]:
            if name is not None:
                self.handlers[name] = handler
            return handler

        return decorator

    def run(self, *, transport: str = "stdio") -> None:
        self.transports.append(transport)


class FakeStartupConnection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


@dataclass
class StubRuntimeApplicationFactory:
    startup_connection: FakeStartupConnection
    application: VeraBrainApplication

    @property
    def connection_factory(self) -> object:
        return SimpleNamespace(
            open_startup_connection=lambda: self.startup_connection,
        )

    def create_application(
        self,
        *,
        memory_embedding_provider=None,
        memory_query_embedding_provider=None,
    ) -> VeraBrainApplication:
        del memory_embedding_provider, memory_query_embedding_provider
        return self.application


def _build_application() -> VeraBrainApplication:
    ids = _id_sequence()
    return VeraBrainApplication(
        unit_of_work=InMemoryUnitOfWork(),
        clock=_now,
        id_generator=lambda: next(ids),
        memory_embedding_provider=StubMemoryEmbeddingProvider(),
    )


def test_local_mvp_launcher_exposes_mcp_tools_for_smoke_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_connection = FakeStartupConnection()
    application = _build_application()
    runtime_factory = StubRuntimeApplicationFactory(startup_connection, application)
    bootstrap_calls: list[object] = []
    created_servers: list[RecordingMCPServer] = []

    def fake_from_settings(_settings: object, *, connector=None) -> StubRuntimeApplicationFactory:
        del connector
        return runtime_factory

    def fake_bootstrap(connection: FakeStartupConnection, *, settings: object) -> None:
        bootstrap_calls.append((connection, settings))

    def server_factory(
        server_name: str,
        *,
        json_response: bool = True,
    ) -> RecordingMCPServer:
        server = RecordingMCPServer(server_name, json_response=json_response)
        created_servers.append(server)
        return server

    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.PostgresRuntimeApplicationFactory.from_settings",
        fake_from_settings,
    )
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.bootstrap_postgres_runtime_schema",
        fake_bootstrap,
    )

    exit_code = run_local_mvp(
        env={
            "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
            "VERABRAIN_MCP_SERVER_NAME": "VeraBrain Local",
        },
        server_factory=server_factory,
    )

    assert exit_code == 0
    assert len(bootstrap_calls) == 1
    assert startup_connection.closed is True
    assert len(created_servers) == 1
    server = created_servers[0]
    assert server.server_name == "VeraBrain Local"
    assert server.transports == ["stdio"]

    save_memory = server.handlers["save_memory"]
    search_memory = server.handlers["search_memory"]
    get_context_bundle = server.handlers["get_context_bundle"]

    save_response = save_memory(
        text="User prefers concise updates.",
        type="preference",
        scope="long",
        source="manual",
    )
    assert save_response["ok"] is True

    search_response = search_memory(text="concise", limit=1)
    assert search_response["ok"] is True
    search_result = search_response["result"]
    assert isinstance(search_result, dict)
    items = search_result["items"]
    assert isinstance(items, list)
    assert len(items) == 1

    bundle_response = get_context_bundle(query="concise", memory_limit=1)
    assert bundle_response["ok"] is True
    bundle_result = bundle_response["result"]
    assert isinstance(bundle_result, dict)
    memories = bundle_result["memories"]
    assert isinstance(memories, list)
    assert len(memories) == 1


def test_local_mvp_launcher_does_not_start_mcp_when_bootstrap_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    startup_connection = FakeStartupConnection()
    runtime_factory = StubRuntimeApplicationFactory(startup_connection, _build_application())
    created_servers: list[RecordingMCPServer] = []

    def fake_from_settings(_settings: object, *, connector=None) -> StubRuntimeApplicationFactory:
        del connector
        return runtime_factory

    def failing_bootstrap(connection: FakeStartupConnection, *, settings: object) -> None:
        del connection, settings
        raise PostgresRuntimeConfigurationError("schema not ready")

    def server_factory(
        server_name: str,
        *,
        json_response: bool = True,
    ) -> RecordingMCPServer:
        server = RecordingMCPServer(server_name, json_response=json_response)
        created_servers.append(server)
        return server

    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.PostgresRuntimeApplicationFactory.from_settings",
        fake_from_settings,
    )
    monkeypatch.setattr(
        "verabrain.runtime.local_mvp.bootstrap_postgres_runtime_schema",
        failing_bootstrap,
    )

    with pytest.raises(PostgresRuntimeConfigurationError, match="schema not ready"):
        run_local_mvp(
            env={
                "VERABRAIN_POSTGRES_DSN": "postgresql://verabrain:test@localhost/verabrain",
            },
            server_factory=server_factory,
        )

    assert startup_connection.closed is True
    assert created_servers == []
