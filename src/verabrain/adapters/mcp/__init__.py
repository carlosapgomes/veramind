"""MCP adapter surface for VeraBrain."""

from .handlers import MCPApplicationAdapter
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
from .server import (
    MCPServerDefinition,
    MCPToolBinding,
    MissingMCPDependencyError,
    build_mcp_server,
    build_server_definition,
    create_mcp_server,
    run_stdio_server,
)

__all__ = [
    "INITIAL_MCP_TOOLS",
    "MCPApplicationAdapter",
    "MCPServerDefinition",
    "MCPToolBinding",
    "MissingMCPDependencyError",
    "build_mcp_server",
    "build_server_definition",
    "capture_knowledge_args_to_request",
    "context_bundle_to_mcp",
    "create_mcp_server",
    "execution_record_to_mcp",
    "get_context_bundle_args_to_request",
    "knowledge_link_record_to_mcp",
    "knowledge_record_to_mcp",
    "link_knowledge_args_to_request",
    "list_review_queue_args_to_request",
    "memory_record_to_mcp",
    "run_stdio_server",
    "save_execution_args_to_request",
    "save_memory_args_to_request",
    "search_execution_args_to_request",
    "search_knowledge_args_to_request",
    "search_memory_args_to_request",
]
