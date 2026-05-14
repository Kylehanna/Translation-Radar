from __future__ import annotations

import json
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from translation_radar_api.config import settings
from translation_radar_api.models import RagAnswer, RagTechnologyResult


def _build_fallback_answer(query: str, results: list[RagTechnologyResult]) -> RagAnswer:
    if results:
        org_names = sorted({result.organization_name for result in results})
        return RagAnswer(
            summary=(
                f"Found {len(results)} technology matches for '{query}' across "
                f"{', '.join(org_names)}. Results are ranked with lightweight keyword overlap and include direct-source evidence."
            ),
            model="heuristic-retrieval-v1",
            generated_at=date.today(),
        )

    return RagAnswer(
        summary=(
            f"No seeded technology records matched '{query}'. Adjust filters or ingest more catalog records before relying on RAG retrieval."
        ),
        model="heuristic-retrieval-v1",
        generated_at=date.today(),
    )


def _llm_is_configured() -> bool:
    return bool(settings.rag_llm_api_url and settings.rag_llm_model)


def _build_messages(query: str, results: list[RagTechnologyResult]) -> list[dict[str, str]]:
    evidence_lines: list[str] = []
    for index, result in enumerate(results[:5], start=1):
        evidence_text = result.evidence[0].text if result.evidence else result.summary
        evidence_lines.append(
            "\n".join(
                [
                    f"Result {index}",
                    f"Title: {result.title}",
                    f"Institution: {result.organization_name}",
                    f"Catalog family: {result.catalog_family}",
                    f"Licensing status: {result.licensing_status}",
                    f"Source URL: {result.source_url}",
                    f"Summary: {result.summary}",
                    f"Evidence: {evidence_text}",
                ]
            )
        )

    return [
        {
            "role": "system",
            "content": (
                "You are a commercialization intelligence assistant. Answer only from the provided evidence. "
                "Be concise. Do not invent institutions, claims, or licensing status. If the evidence is weak, say so."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Query: {query}\n\n"
                "Use the retrieved technology evidence below to produce a short grounded answer for a scout. "
                "Mention the strongest matching institutions and technologies.\n\n"
                + "\n\n".join(evidence_lines)
            ),
        },
    ]


def _call_openai_compatible_chat(messages: list[dict[str, str]]) -> str:
    headers = {"Content-Type": "application/json"}
    if settings.rag_llm_api_key:
        headers["Authorization"] = f"Bearer {settings.rag_llm_api_key}"

    payload = {
        "model": settings.rag_llm_model,
        "messages": messages,
        "temperature": 0.2,
    }
    request = Request(
        settings.rag_llm_api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.rag_llm_timeout_seconds) as response:  # noqa: S310
            body = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"LLM request failed: {exc}") from exc

    choices = body.get("choices", [])
    if not choices:
        raise RuntimeError("LLM response did not include choices")

    message = choices[0].get("message", {})
    content = message.get("content", "").strip()
    if not content:
        raise RuntimeError("LLM response did not include message content")
    return content


def build_rag_answer(query: str, results: list[RagTechnologyResult]) -> RagAnswer:
    fallback = _build_fallback_answer(query, results)
    if not results or not _llm_is_configured():
        return fallback

    messages = _build_messages(query, results)
    try:
        summary = _call_openai_compatible_chat(messages)
    except RuntimeError:
        return fallback

    return RagAnswer(
        summary=summary,
        model=settings.rag_llm_model,
        generated_at=date.today(),
    )