"""POST /v1/chat (streaming) and GET /v1/usage (what the model calls cost)."""

import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from hardenhelp.api.deps import GatewayDep, UsageDep
from hardenhelp.llm.classify import classify_question
from hardenhelp.llm.gateway import LLMResult, LLMUnavailable

router = APIRouter(tags=["chat"])

PROMPT_VERSION = "chat_system_v1"
CLASSIFIER_PROMPT_FILE = "classify_v4.md"

PERSONAL_RESPONSE = (
    "HardenHelp cannot access your actual systems, current configuration, "
    "scan results, or account records yet. It can explain hardening rules "
    "and help interpret relevant information you provide."
)

OFF_TOPIC_RESPONSE = "That question is outside HardenHelp's Linux and Windows hardening scope."


def load_prompt(prompts_dir: Path, filename: str = "chat_system_v1.md") -> str:
    """Load a prompt file from the configured prompts directory."""
    prompt_path = Path(prompts_dir) / filename

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    prompt = prompt_path.read_text(encoding="utf-8")

    if not prompt.strip():
        raise ValueError(f"Prompt file is empty: {prompt_path}")

    return prompt


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    stream: bool = True


def sse(data: dict, event: str = "") -> str:
    """One server-sent event: an optional name, a JSON payload, and a blank line."""
    head = f"event: {event}\n" if event else ""
    return f"{head}data: {json.dumps(data, ensure_ascii=False)}\n\n"


def summary(result: LLMResult) -> dict:
    return {k: v for k, v in asdict(result).items() if k != "text"}


def fixed_stream(
    answer: str,
    category: str,
    classification: LLMResult,
) -> StreamingResponse:
    """Stream a fixed router response without making another model call."""

    async def events() -> AsyncIterator[str]:
        yield sse({"delta": answer})
        yield sse(
            {
                "category": category,
                "classification": summary(classification),
            },
            event="done",
        )

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers=headers,
    )


@router.post("/chat")
async def chat(body: ChatRequest, request: Request, gateway: GatewayDep):
    try:
        category, classification = await classify_question(
            gateway,
            request.app.state.classifier_prompt,
            body.message,
        )
    except LLMUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No model could classify the question: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid classifier response: {exc}",
        ) from exc

    if category == "personal":
        answer = PERSONAL_RESPONSE
        if not body.stream:
            return {
                "answer": answer,
                "category": category,
                "classification": summary(classification),
            }
        return fixed_stream(answer, category, classification)

    if category == "off_topic":
        answer = OFF_TOPIC_RESPONSE
        if not body.stream:
            return {
                "answer": answer,
                "category": category,
                "classification": summary(classification),
            }
        return fixed_stream(answer, category, classification)

    messages = [
        {"role": "system", "content": request.app.state.system_prompt},
        {"role": "user", "content": body.message},
    ]

    try:
        if not body.stream:
            result = await gateway.generate(
                messages,
                prompt_version=PROMPT_VERSION,
            )
            return {
                "answer": result.text,
                "category": category,
                "classification": summary(classification),
                **summary(result),
            }

        stream = gateway.stream(
            messages,
            prompt_version=PROMPT_VERSION,
        )
        first = await anext(stream)

    except LLMUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"No model could answer: {exc}",
        ) from exc

    async def events() -> AsyncIterator[str]:
        item: str | LLMResult = first
        try:
            while True:
                if isinstance(item, LLMResult):
                    yield sse(
                        {
                            **summary(item),
                            "category": category,
                            "classification": summary(classification),
                        },
                        event="done",
                    )
                    return

                yield sse({"delta": item})
                item = await anext(stream)

        except LLMUnavailable as exc:
            yield sse({"detail": str(exc)}, event="error")

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers=headers,
    )


@router.get("/usage")
async def usage(
    repo: UsageDep,
    days: Annotated[int, Query(ge=1, le=90)] = 7,
) -> dict:
    """Tokens and rupees per day, from the llm_calls table."""
    rows = await repo.by_day(days)
    total = round(sum(row["cost_inr"] for row in rows), 4)
    return {
        "days": rows,
        "total_cost_inr": total,
        "calls": sum(row["calls"] for row in rows),
    }
