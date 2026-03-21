"""MCP server composition over the wired VeraBrain adapter surface."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, cast

from verabrain.application import VeraBrainApplication

from .handlers import MCPApplicationAdapter

MCPResponse = dict[str, object]
ToolDefinition = Mapping[str, object]
ToolHandler = Callable[[Mapping[str, object]], MCPResponse]
LOGGER = logging.getLogger(__name__)


class MCPAdapterProtocol(Protocol):
    """Behavior needed from the wired MCP adapter."""

    def list_tools(self) -> tuple[dict[str, object], ...]:
        ...

    def dispatch(self, tool_name: str, args: Mapping[str, object]) -> MCPResponse:
        ...


class ToolDecorator(Protocol):
    """Decorator returned by MCP server implementations for tool registration."""

    def __call__(
        self, handler: Callable[..., MCPResponse]
    ) -> Callable[..., MCPResponse]:
        ...


class MCPServerProtocol(Protocol):
    """Small protocol for the server features needed by this adapter."""

    def tool(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> ToolDecorator:
        ...

    def run(self, *, transport: str = "stdio") -> None:
        ...


class MCPServerFactory(Protocol):
    """Factory protocol used to instantiate MCP server implementations."""

    def __call__(
        self, server_name: str, *, json_response: bool = True
    ) -> MCPServerProtocol:
        ...


class MissingMCPDependencyError(ImportError):
    """Raised when the optional MCP SDK is required but unavailable."""


@dataclass(frozen=True, slots=True)
class MCPToolBinding:
    """Bound MCP tool declaration ready for transport registration."""

    name: str
    description: str
    input_schema: Mapping[str, object]
    handler: ToolHandler


@dataclass(frozen=True, slots=True)
class MCPServerDefinition:
    """Transport-ready MCP server definition over the VeraBrain adapter."""

    name: str
    tools: tuple[MCPToolBinding, ...]


def build_server_definition(
    adapter: MCPAdapterProtocol,
    *,
    server_name: str = "VeraBrain",
) -> MCPServerDefinition:
    """Bind the wired MCP adapter surface into a server definition."""

    bindings: list[MCPToolBinding] = []
    for tool in adapter.list_tools():
        bindings.append(
            MCPToolBinding(
                name=_require_str(tool, "name"),
                description=_require_str(tool, "description"),
                input_schema=_require_mapping(tool, "parameters"),
                handler=_bind_tool_handler(
                    adapter=adapter,
                    tool_name=_require_str(tool, "name"),
                ),
            )
        )
    return MCPServerDefinition(name=server_name, tools=tuple(bindings))


def create_mcp_server(
    application: VeraBrainApplication,
    *,
    server_name: str = "VeraBrain",
    server_factory: MCPServerFactory | None = None,
) -> MCPServerProtocol:
    """Create an MCP server over the callable VeraBrain application services."""

    definition = build_server_definition(
        MCPApplicationAdapter(application=application),
        server_name=server_name,
    )
    return build_mcp_server(definition, server_factory=server_factory)


def build_mcp_server(
    definition: MCPServerDefinition,
    *,
    server_factory: MCPServerFactory | None = None,
) -> MCPServerProtocol:
    """Instantiate and register the VeraBrain MCP tool surface."""

    factory = server_factory or _load_server_factory()
    server = factory(definition.name, json_response=True)
    for tool in definition.tools:
        _register_tool(server, tool)
    LOGGER.debug(
        "Built MCP server '%s' with tools=%s",
        definition.name,
        [tool.name for tool in definition.tools],
    )
    return server


def run_stdio_server(
    application: VeraBrainApplication,
    *,
    server_name: str = "VeraBrain",
    server_factory: MCPServerFactory | None = None,
) -> MCPServerProtocol:
    """Run the VeraBrain MCP server over stdio transport."""

    LOGGER.debug("Starting VeraBrain MCP server over stdio as '%s'", server_name)
    server = create_mcp_server(
        application,
        server_name=server_name,
        server_factory=server_factory,
    )
    server.run(transport="stdio")
    LOGGER.debug("VeraBrain MCP server '%s' is running over stdio", server_name)
    return server


def _load_server_factory() -> MCPServerFactory:
    try:
        from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
    except ImportError as exc:  # pragma: no cover - depends on optional package
        raise MissingMCPDependencyError(
            "The optional MCP SDK is not installed. "
            "Install it with `uv add 'mcp[cli]'` or run with `uv run --with mcp`."
        ) from exc

    def factory(server_name: str, *, json_response: bool = True) -> MCPServerProtocol:
        return cast(
            MCPServerProtocol,
            FastMCP(name=server_name, json_response=json_response),
        )

    return factory


def _register_tool(server: MCPServerProtocol, tool: MCPToolBinding) -> None:
    def handler(**kwargs: object) -> MCPResponse:
        return tool.handler(kwargs)

    handler.__name__ = _pythonize_name(tool.name)
    handler.__doc__ = tool.description
    setattr(handler, "__verabrain_input_schema__", dict(tool.input_schema))
    server.tool(name=tool.name, description=tool.description)(handler)


def _bind_tool_handler(*, adapter: MCPAdapterProtocol, tool_name: str) -> ToolHandler:
    def handler(args: Mapping[str, object]) -> MCPResponse:
        return adapter.dispatch(tool_name, args)

    return handler


def _pythonize_name(name: str) -> str:
    return name.replace("-", "_").replace(".", "_")


def _require_str(tool: ToolDefinition, key: str) -> str:
    value = tool.get(key)
    if isinstance(value, str) and value:
        return value
    raise ValueError(f"MCP tool definition must include a non-empty '{key}'")


def _require_mapping(tool: ToolDefinition, key: str) -> Mapping[str, object]:
    value = tool.get(key)
    if isinstance(value, Mapping):
        return {str(nested_key): nested_value for nested_key, nested_value in value.items()}
    raise ValueError(f"MCP tool definition must include an object '{key}'")
