"""
debugger_agent.py — Debugger node.
Fixes all issues flagged by the QA agent then hands off to documenter.
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior Debugger / Code Reviewer.
You receive code that failed QA review and must fix all identified issues.

Output a JSON object with these fields:
{
  "fixes_applied": ["description of each fix made"],
  "files": {
    "filename.py": "full corrected file contents"
  },
  "next_agent": "documenter"
}

Rules:
- Fix ALL issues listed in the QA report
- Return the complete corrected files (not diffs)
- Respond ONLY with valid JSON. No markdown fences in JSON values."""


def run(state: AgentState) -> AgentState:
    print("\n🐛 [Debugger Agent] Fixing issues identified by QA...")

    dev = json.dumps(state.get("developer_agent", {}), indent=2)
    qa  = json.dumps(state.get("qa_agent", {}),        indent=2)

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Original code:\n{dev}\n\nQA Report:\n{qa}\n\nOriginal request: {state['user_request']}"},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "Debugger Agent")
    print(f"   ✓ Fixes applied: {len(result.get('fixes_applied', []))}")
    for fix in result.get("fixes_applied", []):
        print(f"     - {fix}")

    return {
        **state,
        "debugger_agent": result,
        "next_agent":     result.get("next_agent", "documenter"),
    }
