import os
import json
from openai import OpenAI


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


def get_openai_client():
    if not os.getenv("OPENAI_API_KEY"):
        load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it before running the app."
        )
    return OpenAI()


def _strip_json_fences(text: str) -> str:
    if not text:
        return ""
    content = text.strip()
    if content.startswith("```"):
        fence_body = content.strip("`").strip()
        if fence_body.startswith("json"):
            fence_body = fence_body[4:].strip()
        content = fence_body
    return content


def parse_json_response(text: str, source: str) -> object:
    cleaned = _strip_json_fences(text)
    if not cleaned:
        raise ValueError(f"{source} returned an empty response or no JSON content.")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{source} returned invalid JSON.\n"
            f"Cleaned response:\n{cleaned}\n\n"
            f"Original response:\n{text}"
        ) from exc
