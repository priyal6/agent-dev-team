"""
pm_agent.py — Product Manager node.
Converts a raw user request into a structured PRD.
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior Product Manager at a software agency.
Your job is to take a raw user request and produce a structured Product Requirements Document (PRD).

Output a JSON object with these fields:
{
  "project_name": "...",
  "summary": "...",
  "goals": ["..."],
  "features": ["..."],
  "tech_stack": ["..."],
  "constraints": ["..."],
  "next_agent": "architect"
}

Respond ONLY with valid JSON. No markdown, no explanation."""


def run(state: AgentState) -> AgentState:
    print("\n📋 [PM Agent] Analysing requirements...")

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"User request: {state['user_request']}"},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "PM Agent")
    print(f"   ✓ Project : {result.get('project_name')}")
    print(f"   ✓ Features: {len(result.get('features', []))}")

    return {
        **state,
        "pm_agent":   result,
        "next_agent": result.get("next_agent", "architect"),
    }
