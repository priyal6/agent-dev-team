"""
dev_agent.py — Developer node.
Reads PRD + architecture from state and writes all source files.
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior Backend Developer.
You receive a PRD and architecture spec, and write the full working code for a REST API.

Output a JSON object with these fields:
{
  "files": {
    "filename.py": "full file contents as a string",
    "requirements.txt": "...",
    "README.md": "..."
  },
  "entry_point": "main.py or app.py etc",
  "run_command": "python app.py or uvicorn app:app etc",
  "next_agent": "qa"
}

Rules:
- Write complete, working, production-quality code
- Use the exact framework from the architecture spec
- Include requirements.txt with all dependencies
- Add inline comments explaining key sections
- Respond ONLY with valid JSON. No markdown fences in the JSON values."""


def run(state: AgentState) -> AgentState:
    print("\n💻 [Developer Agent] Writing code...")

    prd  = json.dumps(state.get("pm_agent", {}),        indent=2)
    arch = json.dumps(state.get("architect_agent", {}), indent=2)

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"PRD:\n{prd}\n\nArchitecture:\n{arch}\n\nOriginal request: {state['user_request']}"},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "Developer Agent")
    print(f"   ✓ Files generated: {list(result.get('files', {}).keys())}")
    print(f"   ✓ Entry point    : {result.get('entry_point')}")
    print(f"   ✓ Run command    : {result.get('run_command')}")

    return {
        **state,
        "developer_agent": result,
        "next_agent":      result.get("next_agent", "qa"),
    }
