"""
qa_agent.py — QA node.
Reviews the generated code and writes a pytest suite.
Sets next_agent to "debugger" if issues are critical, else "documenter".
"""

import json
from .openai_client import get_openai_client, parse_json_response
from state import AgentState

SYSTEM_PROMPT = """You are a Senior QA Engineer.
You review code and produce a test suite plus a quality report.

Output a JSON object with these fields:
{
  "quality_report": {
    "overall_score": 0-100,
    "issues": ["list of bugs or concerns found"],
    "suggestions": ["list of improvements"]
  },
  "test_files": {
    "test_app.py": "full pytest test file contents"
  },
  "approved": true or false,
  "next_agent": "debugger" if approved is false, else "documenter"
}

Rules:
- Write real pytest tests covering all endpoints
- Be thorough but constructive in the quality report
- Only set approved=false if there are CRITICAL bugs
- Respond ONLY with valid JSON. No markdown fences in JSON values."""


def run(state: AgentState) -> AgentState:
    print("\n🧪 [QA Agent] Reviewing code and writing tests...")

    arch = json.dumps(state.get("architect_agent", {}), indent=2)
    dev  = json.dumps(state.get("developer_agent", {}), indent=2)

    response = get_openai_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Architecture:\n{arch}\n\nGenerated Code:\n{dev}\n\nOriginal request: {state['user_request']}"},
        ],
    )

    result = parse_json_response(response.choices[0].message.content, "QA Agent")
    report = result.get("quality_report", {})
    print(f"   ✓ Quality score: {report.get('overall_score')}/100")
    print(f"   ✓ Issues found : {len(report.get('issues', []))}")
    print(f"   ✓ Approved     : {result.get('approved')}")
    print(f"   ✓ Routing to   : {result.get('next_agent')}")

    return {
        **state,
        "qa_agent":   result,
        "next_agent": result.get("next_agent", "documenter"),
    }
