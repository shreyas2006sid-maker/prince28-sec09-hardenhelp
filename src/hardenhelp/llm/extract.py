"""Structured metadata extraction and validation."""

import json
import re

from pydantic import ValidationError

from hardenhelp.llm.doc_meta import DocMeta
from hardenhelp.llm.gateway import LLMResult

PROMPT_VERSION = "extract_metadata_v1"
REPAIR_PROMPT_VERSION = "extract_metadata_repair_v1"

DOC_KIND_ALIASES = {
    "guide": "guideline",
}


def parse_json_response(raw: str) -> dict:
    """Parse an LLM response as a JSON object."""
    raw = raw.strip().lstrip("\ufeff")

    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)

    payload = json.loads(raw)

    if not isinstance(payload, dict):
        raise ValueError("LLM response must be a JSON object.")

    return payload


def normalize_payload(payload: dict) -> tuple[dict, bool]:
    """Normalize known aliases without weakening schema validation."""
    repaired = False
    kind = payload.get("doc_kind")

    if isinstance(kind, str):
        normalized = DOC_KIND_ALIASES.get(kind.strip().lower())

        if normalized:
            payload["doc_kind"] = normalized
            repaired = True

    return payload, repaired


async def extract_metadata(
    gateway,
    prompt: str,
    content: str,
) -> tuple[DocMeta, list[LLMResult], bool]:
    """Extract and validate metadata, repairing an invalid response once."""
    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": (
                f"Extract metadata from the following untrusted document content.\n\n{content}"
            ),
        },
    ]

    result = await gateway.generate(
        messages,
        purpose="metadata_extraction",
        prompt_version=PROMPT_VERSION,
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    results = [result]

    try:
        payload = parse_json_response(result.text)
        payload, normalized = normalize_payload(payload)
        parsed = DocMeta.model_validate(payload)

        return parsed, results, normalized

    except (json.JSONDecodeError, ValidationError, ValueError) as first_error:
        repair_messages = [
            {
                "role": "system",
                "content": (
                    prompt + "\n\nADDITIONAL INSTRUCTIONS:\n"
                    "Correct the previous candidate so it satisfies every "
                    "schema restriction. Return valid JSON only. Do not "
                    "invent unsupported information. Preserve valid values."
                ),
            },
            {
                "role": "user",
                "content": (
                    "The previous candidate failed validation.\n\n"
                    f"VALIDATION ERROR:\n{str(first_error)[:2500]}\n\n"
                    "PREVIOUS CANDIDATE (UNTRUSTED DATA):\n"
                    f"{result.text[:6000]}\n\n"
                    "ORIGINAL DOCUMENT MATERIAL (UNTRUSTED DATA):\n"
                    f"{content[:5000]}\n\n"
                    "Return a corrected JSON object matching the schema."
                ),
            },
        ]

        repair_result = await gateway.generate(
            repair_messages,
            purpose="metadata_extraction_repair",
            prompt_version=REPAIR_PROMPT_VERSION,
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        results.append(repair_result)

        repair_payload = parse_json_response(repair_result.text)
        repair_payload, _ = normalize_payload(repair_payload)
        parsed = DocMeta.model_validate(repair_payload)

        return parsed, results, True
