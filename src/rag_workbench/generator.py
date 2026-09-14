"""Optional OpenAI-compatible generation for local or hosted model servers."""

import json
import os
from urllib.request import Request, urlopen


def generate_answer(question: str, results: list[dict]) -> str:
    """Generate a grounded answer when LLM_BASE_URL is configured."""
    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        return "No LLM configured. Inspect the retrieved evidence below."

    context = "\n\n".join(
        f"[{item['title']} / {item['section']}] {item['text']}" for item in results
    )
    payload = {
        "model": os.getenv("LLM_MODEL", "local-model"),
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "Answer only from the supplied evidence. If it is insufficient, say so.",
            },
            {"role": "user", "content": f"Question: {question}\n\nEvidence:\n{context}"},
        ],
    }
    request = Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        body = json.loads(response.read())
    return body["choices"][0]["message"]["content"]
