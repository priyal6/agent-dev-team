"""
file_writer.py — Writes all agent-generated files to output/generated_app/
"""

import os
import json

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "generated_app")


def write_output_files(context):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files_written = []

    # Collect files from developer agent (or debugger if it ran)
    code_source = context.get("debugger_agent") or context.get("developer_agent")
    if code_source:
        for filename, content in code_source.get("files", {}).items():
            _write(filename, content)
            files_written.append(filename)

    # Collect test files from QA agent
    qa = context.get("qa_agent", {})
    for filename, content in qa.get("test_files", {}).items():
        _write(filename, content)
        files_written.append(filename)

    # Collect documentation files
    doc = context.get("doc_agent", {})
    for filename, content in doc.get("files", {}).items():
        _write(filename, content)
        files_written.append(filename)

    # Save full pipeline context as JSON for inspection
    _write("_pipeline_context.json", json.dumps(context, indent=2))
    files_written.append("_pipeline_context.json")

    print(f"   ✓ Written {len(files_written)} files to output/generated_app/")
    for f in files_written:
        print(f"     📄 {f}")

    return files_written


def _write(filename: str, content: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
