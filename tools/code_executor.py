"""
code_executor.py — Safely executes generated code in a subprocess for validation.
"""

import subprocess
import os
import sys
import tempfile

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "generated_app")


def install_requirements(requirements_txt: str = None) -> dict:
    """Install dependencies from requirements.txt content or file."""
    req_file = os.path.join(OUTPUT_DIR, "requirements.txt")

    if requirements_txt:
        with open(req_file, "w") as f:
            f.write(requirements_txt)
    elif not os.path.exists(req_file):
        return {"success": False, "error": "No requirements.txt found"}

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"],
        capture_output=True,
        text=True,
        timeout=120
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def run_tests(test_file: str = "test_app.py") -> dict:
    """Run pytest on the generated test file."""
    test_path = os.path.join(OUTPUT_DIR, test_file)

    if not os.path.exists(test_path):
        return {"success": False, "error": f"Test file not found: {test_path}"}

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=OUTPUT_DIR,
        timeout=60
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0
    }


def syntax_check(filepath: str) -> dict:
    """Check Python file for syntax errors."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", filepath],
        capture_output=True,
        text=True
    )

    return {
        "valid": result.returncode == 0,
        "error": result.stderr if result.returncode != 0 else None
    }


def syntax_check_all() -> dict:
    """Syntax-check all .py files in the output directory."""
    results = {}
    for fname in os.listdir(OUTPUT_DIR):
        if fname.endswith(".py"):
            fpath = os.path.join(OUTPUT_DIR, fname)
            results[fname] = syntax_check(fpath)
    return results
