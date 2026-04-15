"""
state.py — Shared state schema for the LangGraph pipeline.

AgentState is the single typed dict that flows through every node.
Each agent reads from it and merges its output back into it.
"""

from typing import Optional, Any
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    # The original user request — set once, never mutated
    user_request: str

    # Each agent writes its result under its own key
    pm_agent:        Optional[dict[str, Any]]
    architect_agent: Optional[dict[str, Any]]
    developer_agent: Optional[dict[str, Any]]
    qa_agent:        Optional[dict[str, Any]]
    debugger_agent:  Optional[dict[str, Any]]
    doc_agent:       Optional[dict[str, Any]]

    # Routing signal — the currently active agent sets this to
    # tell the router which node should run next (or None to end)
    next_agent: Optional[str]
