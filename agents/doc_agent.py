"""
doc_agent.py — Documentation node (final step).
Generates README, API reference, and setup guide from all prior state.
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior Technical Writer.
You produce comprehensive documentation for a REST API project.

Output a JSON object with these fields:
{
  "files": {
    "README.md": "full markdown README",
    "API.md": "full API reference documentation",
    "SETUP.md": "installation and setup guide"
  },
  "next_agent": null
}

Rules:
- README: project overview, features, quick start
- API.md: every endpoint with method, path, params, example request/response
- SETUP.md: prerequisites, installation, configuration, running locally
- Use clear markdown with headers, code blocks, tables
- Respond ONLY with valid JSON. No markdown fences wrapping the JSON itself."""


def run(state: AgentState) -> AgentState:
    print("\n📝 [Doc Agent] Writing documentation...")

    prd  = json.dumps(state.get("pm_agent",        {}), indent=2)
    arch = json.dumps(state.get("architect_agent", {}), indent=2)
    code = state.get("debugger_agent") or state.get("developer_agent", {})
    qa   = json.dumps(state.get("qa_agent",        {}), indent=2)

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": (
                f"PRD:\n{prd}\n\nArchitecture:\n{arch}\n\n"
                f"Final Code:\n{json.dumps(code, indent=2)}\n\n"
                f"QA Report:\n{qa}\n\nOriginal request: {state['user_request']}"
            )},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "Doc Agent")
    print(f"   ✓ Docs generated: {list(result.get('files', {}).keys())}")

    return {
        **state,
        "doc_agent":  result,
        "next_agent": None,   # terminal node
    }
