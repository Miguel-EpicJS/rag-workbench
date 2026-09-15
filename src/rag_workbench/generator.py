"""Optional OpenAI-compatible generation for local or hosted model servers."""

import json
import os
import re
from urllib.request import Request, urlopen


def generate_answer(question: str, results: list[dict]) -> str:
    """Generate a grounded answer when LLM_BASE_URL is configured."""
    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        if not results:
            return "Baseline mode: no matching evidence was found."
        first_sentence = re.split(r"(?<=[.!?])\s+", results[0]["text"].strip())[0]
        return f"Baseline mode: {first_sentence} [1]"

    context = "\n\n".join(
        f"[{index}] {item['title']} / {item['section']}: {item['text']}"
        for index, item in enumerate(results, start=1)
    )
    payload = {
        "model": os.getenv("LLM_MODEL", "local-model"),
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "Answer only from the supplied evidence. Cite claims with [n]. If it is insufficient, say so.",
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


def validate_citations(answer: str, evidence_count: int) -> dict:
    """Validate that citations point to evidence returned for this answer."""
    references = [int(value) for value in re.findall(r"\[(\d+)\]", answer)]
    valid = bool(references) and all(1 <= reference <= evidence_count for reference in references)
    return {"valid": valid, "references": references}
