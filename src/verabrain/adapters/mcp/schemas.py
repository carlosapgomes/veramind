"""Initial MCP tool schemas for the VeraBrain adapter."""

SAVE_MEMORY_TOOL = {
    "name": "save_memory",
    "description": (
        "Persist a durable memory about the user, preferences, decisions, "
        "habits, or active project context. Do not use this for general notes "
        "or task lists."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "type": {
                "type": "string",
                "enum": [
                    "preference",
                    "decision",
                    "project",
                    "habit",
                    "followup",
                    "profile",
                ],
            },
            "scope": {"type": "string", "enum": ["short", "medium", "long"]},
            "source": {"type": "string"},
            "salience": {"type": "number"},
            "metadata": {"type": "object"},
        },
        "required": ["text", "type", "scope", "source"],
        "additionalProperties": False,
    },
}

SEARCH_MEMORY_TOOL = {
    "name": "search_memory",
    "description": "Search durable memories for bounded retrieval.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 25},
            "min_salience": {"type": "number"},
        },
        "required": ["text"],
        "additionalProperties": False,
    },
}

CAPTURE_KNOWLEDGE_TOOL = {
    "name": "capture_knowledge",
    "description": (
        "Capture a durable knowledge item such as a note, reference, "
        "research artifact, or supporting document."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "text": {"type": "string"},
            "kind": {"type": "string"},
            "source": {"type": "string"},
            "metadata": {"type": "object"},
        },
        "required": ["title", "text", "kind", "source"],
        "additionalProperties": False,
    },
}

SEARCH_KNOWLEDGE_TOOL = {
    "name": "search_knowledge",
    "description": "Search knowledge items by text query.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 25},
            "related_to": {"type": "string"},
        },
        "required": ["text"],
        "additionalProperties": False,
    },
}

LINK_KNOWLEDGE_ITEMS_TOOL = {
    "name": "link_knowledge_items",
    "description": "Create an explicit semantic relationship between two knowledge items.",
    "parameters": {
        "type": "object",
        "properties": {
            "left_id": {"type": "string"},
            "right_id": {"type": "string"},
            "relation": {"type": "string"},
            "metadata": {"type": "object"},
        },
        "required": ["left_id", "right_id", "relation"],
        "additionalProperties": False,
    },
}

SAVE_EXECUTION_TOOL = {
    "name": "save_execution",
    "description": (
        "Create or update a workflow-neutral execution item such as a task, "
        "review item, or open loop."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "kind": {"type": "string"},
            "state": {"type": "string"},
            "source": {"type": "string"},
            "project_id": {"type": "string"},
            "due_at": {"type": "string", "format": "date-time"},
            "review_at": {"type": "string", "format": "date-time"},
            "metadata": {"type": "object"},
        },
        "required": ["title", "kind", "state", "source"],
        "additionalProperties": False,
    },
}

SEARCH_EXECUTION_TOOL = {
    "name": "search_execution",
    "description": "Search execution items by state, project, or due windows.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            "states": {"type": "array", "items": {"type": "string"}},
            "project_id": {"type": "string"},
            "due_before": {"type": "string", "format": "date-time"},
            "review_before": {"type": "string", "format": "date-time"},
        },
        "additionalProperties": False,
    },
}

GET_CONTEXT_BUNDLE_TOOL = {
    "name": "get_context_bundle",
    "description": (
        "Retrieve a bounded cross-domain context bundle grouped by memory, "
        "knowledge, and execution."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "memory_limit": {"type": "integer", "minimum": 1, "maximum": 10},
            "knowledge_limit": {"type": "integer", "minimum": 1, "maximum": 10},
            "execution_limit": {"type": "integer", "minimum": 1, "maximum": 10},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}

LIST_REVIEW_QUEUE_TOOL = {
    "name": "list_review_queue",
    "description": "List execution items that are due for review at a reference time.",
    "parameters": {
        "type": "object",
        "properties": {
            "reference_at": {"type": "string", "format": "date-time"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "required": ["reference_at"],
        "additionalProperties": False,
    },
}

INITIAL_MCP_TOOLS = (
    SAVE_MEMORY_TOOL,
    SEARCH_MEMORY_TOOL,
    CAPTURE_KNOWLEDGE_TOOL,
    SEARCH_KNOWLEDGE_TOOL,
    LINK_KNOWLEDGE_ITEMS_TOOL,
    SAVE_EXECUTION_TOOL,
    SEARCH_EXECUTION_TOOL,
    GET_CONTEXT_BUNDLE_TOOL,
    LIST_REVIEW_QUEUE_TOOL,
)
