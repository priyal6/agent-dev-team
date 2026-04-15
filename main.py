"""
main.py — Entry point for the AI Dev Team pipeline (LangGraph edition).

Usage:
    python main.py
    python main.py "Build a task management REST API with CRUD operations"

Set your OpenAI API key:
    export OPENAI_API_KEY=sk-...
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_dotenv(dotenv_path: str | None = None) -> None:
    if dotenv_path is None:
        dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if ((value.startswith("\"") and value.endswith("\""))
                    or (value.startswith("'") and value.endswith("'"))):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value

DEFAULT_TASK = (
    "Build a simple REST API for a Todo app. "
    "It should support creating, reading, updating, and deleting todos. "
    "Each todo has a title, description, and completed status. "
    "Use FastAPI and store data in-memory."
)


def main():
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        print("No task provided — using default demo task.\n")
        user_request = DEFAULT_TASK

    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("   Windows PowerShell: setx OPENAI_API_KEY \"sk-...\"")
        print("   macOS/Linux: export OPENAI_API_KEY=sk-...")
        print("   Or add OPENAI_API_KEY to a .env file in the project folder.")
        sys.exit(1)

    from workflows.pipeline import run_pipeline, build_graph

    # Optional: print the Mermaid graph diagram before running
    if "--diagram" in sys.argv:
        graph = build_graph().compile()
        print("\n📊 LangGraph pipeline diagram (Mermaid):")
        print(graph.get_graph().draw_mermaid())
        print()

    final_state = run_pipeline(user_request)

    # Summary
    agents_ran = [k for k in final_state if k.endswith("_agent") and final_state[k]]
    print("\n📊 Agents that ran:")
    for agent in agents_ran:
        print(f"   ✅ {agent}")

    output_dir = os.path.join(os.path.dirname(__file__), "output", "generated_app")
    print(f"\n📁 Output written to: {output_dir}")


if __name__ == "__main__":
    main()

