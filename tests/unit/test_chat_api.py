"""Tests for /v1/chat classification, streaming, and /v1/usage."""

import json

from hardenhelp.llm.gateway import LLMError


def events(body: str) -> list[tuple[str, dict]]:
    """Parse a server-sent-event body into (event name, data) pairs."""
    out = []
    for block in body.strip().split("\n\n"):
        name = ""
        for line in block.splitlines():
            if line.startswith("event:"):
                name = line[6:].strip()
            elif line.startswith("data:"):
                out.append((name, json.loads(line[5:])))
    return out


def test_chat_without_streaming_returns_json(client, llm):
    llm.script = ["docs", "Use curly braces in the path."]

    r = client.post(
        "/v1/chat",
        json={
            "message": "How do I declare a path parameter?",
            "stream": False,
        },
    )

    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "Use curly braces in the path."
    assert body["category"] == "docs"
    assert body["provider"] == "fake"
    assert body["tokens_out"] == 6
    assert "cost_inr" in body
    assert "classification" in body


def test_chat_streams_pieces_and_ends_with_done_event(client, llm):
    llm.script = ["docs", "Use curly braces in the path."]

    r = client.post(
        "/v1/chat",
        json={"message": "How do I declare a path parameter?"},
    )

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    received = events(r.text)
    text = "".join(data["delta"] for name, data in received if name == "")

    assert text.strip() == "Use curly braces in the path."
    assert received[-1][0] == "done"
    assert received[-1][1]["model"] == "fake-1"
    assert received[-1][1]["category"] == "docs"
    assert "classification" in received[-1][1]


def test_personal_question_returns_fixed_json_without_answer_call(client, llm):
    llm.script = ["personal"]

    r = client.post(
        "/v1/chat",
        json={
            "message": "What are my current failing STIG rules?",
            "stream": False,
        },
    )

    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "personal"
    assert "cannot access your actual systems" in body["answer"]
    assert "classification" in body
    assert llm.calls == 1


def test_off_topic_question_returns_fixed_json_without_answer_call(client, llm):
    llm.script = ["off_topic"]

    r = client.post(
        "/v1/chat",
        json={"message": "Who won the cricket match?", "stream": False},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "off_topic"
    assert "outside HardenHelp" in body["answer"]
    assert llm.calls == 1


def test_personal_question_supports_streaming(client, llm):
    llm.script = ["personal"]

    r = client.post(
        "/v1/chat",
        json={"message": "Show my current system configuration."},
    )

    assert r.status_code == 200
    received = events(r.text)

    text = "".join(data["delta"] for name, data in received if name == "")
    assert "cannot access your actual systems" in text
    assert received[-1][0] == "done"
    assert received[-1][1]["category"] == "personal"
    assert llm.calls == 1


def test_both_prompt_files_are_loaded(client):
    assert "not sure" in client.app.state.system_prompt

    classifier_prompt = client.app.state.classifier_prompt.lower()
    assert "docs" in classifier_prompt
    assert "personal" in classifier_prompt
    assert "off_topic" in classifier_prompt


def test_an_empty_message_is_a_422_problem(client):
    r = client.post("/v1/chat", json={"message": ""})

    assert r.status_code == 422
    assert r.headers["content-type"] == "application/problem+json"


def test_classifier_failure_returns_503(client, llm):
    llm.script = [LLMError("HTTP 401: invalid API key", retryable=False)]

    r = client.post(
        "/v1/chat",
        json={"message": "How do I secure SSH?"},
    )

    assert r.status_code == 503
    assert "No model could classify" in r.json()["detail"]


def test_invalid_classifier_category_returns_502(client, llm):
    llm.script = ["unknown"]

    r = client.post(
        "/v1/chat",
        json={"message": "How do I secure SSH?"},
    )

    assert r.status_code == 502
    assert "Invalid classifier response" in r.json()["detail"]


def test_failure_in_answer_stream_is_reported_as_error_event(client, llm):
    llm.script = [
        "docs",
        ("partial", LLMError("HTTP 503: overloaded", retryable=True)),
    ]

    r = client.post(
        "/v1/chat",
        json={"message": "How do I secure SSH?"},
    )

    assert r.status_code == 200
    assert events(r.text)[-1][0] == "error"


def test_usage_reports_tokens_and_rupees_per_day(client):
    r = client.get("/v1/usage")

    assert r.status_code == 200
    body = r.json()
    assert body["days"][0]["tokens_in"] == 300
    assert body["total_cost_inr"] == 0.0642
    assert body["calls"] == 3
