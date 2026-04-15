"""
architect_agent.py — Architect node.
Reads the PRD from state and designs the REST API architecture.
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior Software Architect.
You receive a PRD and design the technical architecture for a REST API.

Output a JSON object with these fields:
{
  "architecture": {
    "style": "REST",
    "framework": "...",
    "endpoints": [
      {"method": "GET/POST/PUT/DELETE", "path": "/...", "description": "..."}
    ],
    "data_models": [
      {"name": "...", "fields": {"field_name": "type"}}
    ],
    "file_structure": ["list of files to create"]
  },
  "implementation_notes": ["..."],
  "next_agent": "developer"
}

Respond ONLY with valid JSON. No markdown, no explanation."""


def run(state: AgentState) -> AgentState:
    print("\n🏗️  [Architect Agent] Designing system architecture...")

    prd = json.dumps(state.get("pm_agent", {}), indent=2)

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"PRD:\n{prd}\n\nOriginal request: {state['user_request']}"},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "Architect Agent")
    arch = result.get("architecture", {})
    print(f"   ✓ Framework: {arch.get('framework')}")
    print(f"   ✓ Endpoints: {len(arch.get('endpoints', []))}")
    print(f"   ✓ Models   : {len(arch.get('data_models', []))}")

    return {
        **state,
        "architect_agent": result,
        "next_agent":      result.get("next_agent", "developer"),
    }
