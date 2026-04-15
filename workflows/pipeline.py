"""
pipeline.py — LangGraph StateGraph pipeline.

Graph structure:
  pm → architect → developer → qa ──(approved)──▶ documenter → END
                                 └─(rejected)──▶ debugger → documenter → END

Routing is driven by the `next_agent` field each node writes into AgentState,
so the LLM itself controls the conditional edges at runtime.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from agents import pm_agent, architect_agent, dev_agent, qa_agent, debugger_agent, doc_agent
from tools.file_writer import write_output_files


# ── Router ────────────────────────────────────────────────────────────────────

def route(state: AgentState) -> str:
    """
    Read next_agent from state and return the name of the next node.
    If next_agent is None or unrecognised, terminate the graph.
    """
    nxt = state.get("next_agent")
    valid = {"architect", "developer", "qa", "debugger", "documenter"}
    if nxt in valid:
        return nxt
    return END


# ── Writer (terminal side-effect node) ────────────────────────────────────────

def write_files(state: AgentState) -> AgentState:
    print("\n💾 Writing generated files to output/generated_app/...")
    write_output_files(state)
    return state


# ── Build graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Register nodes
    g.add_node("pm",          pm_agent.run)
    g.add_node("architect",   architect_agent.run)
    g.add_node("developer",   dev_agent.run)
    g.add_node("qa",          qa_agent.run)
    g.add_node("debugger",    debugger_agent.run)
    g.add_node("documenter",  doc_agent.run)
    g.add_node("write_files", write_files)

    # Entry point
    g.set_entry_point("pm")

    # Fixed sequential edges (no branching needed here)
    g.add_edge("pm",        "architect")
    g.add_edge("architect", "developer")
    g.add_edge("developer", "qa")

    # Conditional edge after QA: debugger OR documenter
    g.add_conditional_edges(
        "qa",
        route,
        {
            "debugger":   "debugger",
            "documenter": "documenter",
            END:          END,
        },
    )

    # Debugger always goes to documenter
    g.add_edge("debugger", "documenter")

    # Documenter triggers file writing, then END
    g.add_edge("documenter", "write_files")
    g.add_edge("write_files", END)

    return g


# ── Public entry point ────────────────────────────────────────────────────────

def run_pipeline(user_request: str) -> AgentState:
    print("=" * 60)
    print("🚀 AI Dev Team Pipeline  (powered by LangGraph)")
    print(f"📌 Task: {user_request}")
    print("=" * 60)

    checkpointer = MemorySaver()
    graph = build_graph().compile(checkpointer=checkpointer)

    # thread_id lets MemorySaver checkpoint this specific run
    config = {"configurable": {"thread_id": "dev-team-run-1"}}

    final_state: AgentState = graph.invoke(
        {"user_request": user_request},
        config=config,
    )

    print("\n" + "=" * 60)
    print("🎉 Pipeline finished successfully!")
    print("=" * 60)

    return final_state

