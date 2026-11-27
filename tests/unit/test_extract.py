"""Metadata extraction tests using a fake LLM gateway."""

import json

import pytest

from hardenhelp.llm.doc_meta import DocMeta
from hardenhelp.llm.extract import (
    extract_metadata,
    normalize_payload,
    parse_json_response,
)
from hardenhelp.llm.gateway import LLMResult

VALID_METADATA = {
    "doc_kind": "rule",
    "year": 2024,
    "language": "en",
    "summary": "A security rule that configures and validates Linux audit settings.",
    "topics": ["linux security"],
    "stig_id": ["OL08-00-010000"],
    "rule_id": ["xccdf_org.ssgproject.content_rule_audit"],
    "cci": ["CCI-000015"],
    "ssg_rule": ["audit_rules"],
    "severity": ["medium"],
    "os": ["Oracle Linux 8"],
}


class FakeGateway:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    async def generate(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        response = self.responses.pop(0)

        return LLMResult(
            text=response,
            provider="gemini",
            model="fake-gemini",
            tokens_in=10,
            tokens_out=20,
            cost_inr=0.001,
            latency_ms=10,
            attempts=1,
            fallback_used=False,
        )


def test_parse_json_response_accepts_plain_json():
    assert parse_json_response('{"doc_kind": "rule"}') == {"doc_kind": "rule"}


def test_parse_json_response_accepts_markdown_json():
    raw = '```json\n{"doc_kind": "rule"}\n```'
    assert parse_json_response(raw) == {"doc_kind": "rule"}


def test_parse_json_response_rejects_non_object():
    with pytest.raises(ValueError, match="JSON object"):
        parse_json_response('["rule"]')


def test_normalize_payload_converts_guide_alias():
    payload, changed = normalize_payload({"doc_kind": "guide"})

    assert payload["doc_kind"] == "guideline"
    assert changed is True


def test_doc_meta_validates_metadata_contract():
    parsed = DocMeta.model_validate(VALID_METADATA)

    assert parsed.doc_kind == "rule"
    assert parsed.rule_id == ["xccdf_org.ssgproject.content_rule_audit"]
    assert parsed.severity == ["medium"]


async def test_extract_metadata_returns_valid_response():
    gateway = FakeGateway(json.dumps(VALID_METADATA))

    parsed, results, repaired = await extract_metadata(
        gateway,
        "Extract metadata.",
        "Linux audit document.",
    )

    assert parsed.rule_id == VALID_METADATA["rule_id"]
    assert len(results) == 1
    assert repaired is False
    assert gateway.calls[0][1]["purpose"] == "metadata_extraction"


async def test_extract_metadata_repairs_invalid_response_once():
    invalid = {"doc_kind": "unknown"}
    gateway = FakeGateway(
        json.dumps(invalid),
        json.dumps(VALID_METADATA),
    )

    parsed, results, repaired = await extract_metadata(
        gateway,
        "Extract metadata.",
        "Linux audit document.",
    )

    assert parsed.doc_kind == "rule"
    assert len(results) == 2
    assert repaired is True
    assert gateway.calls[1][1]["purpose"] == "metadata_extraction_repair"


async def test_extract_metadata_normalizes_guide_without_repair():
    payload = dict(VALID_METADATA)
    payload["doc_kind"] = "guide"

    gateway = FakeGateway(json.dumps(payload))

    parsed, results, repaired = await extract_metadata(
        gateway,
        "Extract metadata.",
        "Security guide.",
    )

    assert parsed.doc_kind == "guideline"
    assert len(results) == 1
    assert repaired is True


# ADD THE NEW TEST HERE
async def test_extract_metadata_repairs_empty_topics():
    invalid = dict(VALID_METADATA)
    invalid["topics"] = []

    repaired_metadata = dict(VALID_METADATA)
    repaired_metadata["topics"] = ["linux auditing"]

    gateway = FakeGateway(
        json.dumps(invalid),
        json.dumps(repaired_metadata),
    )

    parsed, results, repaired = await extract_metadata(
        gateway,
        "Extract metadata.",
        "Linux audit configuration document.",
    )

    assert parsed.topics == ["linux auditing"]
    assert len(results) == 2
    assert repaired is True
    assert gateway.calls[1][1]["purpose"] == "metadata_extraction_repair"


async def test_extract_repairs_empty_topics():
    from hardenhelp.llm.extract import extract

    invalid = dict(VALID_METADATA)
    invalid["topics"] = []

    repaired_metadata = dict(VALID_METADATA)
    repaired_metadata["topics"] = ["linux auditing"]

    gateway = FakeGateway(
        json.dumps(invalid),
        json.dumps(repaired_metadata),
    )

    result = await extract(
        gateway,
        DocMeta,
        "Extract metadata.",
        "extract_metadata_v1",
        "Linux audit configuration",
        "Configure audit log directory permissions.",
    )

    assert result.record is not None
    assert result.record.topics == ["linux auditing"]
    assert result.errors == []
    assert len(gateway.calls) == 2
    assert gateway.calls[1][1]["purpose"] == "document_extraction_repair"
