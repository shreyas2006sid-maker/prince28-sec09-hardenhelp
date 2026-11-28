"""Extract structured metadata from HardenHelp documents."""

import argparse
import asyncio
import time
import uuid

from pydantic import ValidationError
from sqlalchemy import func, select

from hardenhelp.config import get_settings
from hardenhelp.db.llm_calls import make_recorder
from hardenhelp.db.models import Document, Page
from hardenhelp.db.session import make_engine, make_sessionmaker
from hardenhelp.llm.extract import extract_metadata
from hardenhelp.llm.gateway import LLMUnavailable, build_gateway
from hardenhelp.logging_setup import request_id_ctx

MAX_DOCUMENT_CHARS = 18000


def load_prompt(path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Metadata prompt not found: {path}")
    return path.read_text(encoding="utf-8")


async def load_document_snapshot(session_factory, document_id, force):
    """Read document data and release the DB connection before calling an LLM."""
    async with session_factory() as session:
        document = await session.get(Document, document_id)

        if document is None:
            return None

        metadata = dict(document.metadata_ or {})

        if metadata.get("quarantined") is True:
            return None

        if not force and "extracted" in metadata:
            return None

        result = await session.scalars(
            select(Page.text).where(Page.document_id == document_id).order_by(Page.page_no)
        )

        page_text = "\n\n".join(result.all())

        import json

        metadata_text = json.dumps(
            metadata,
            ensure_ascii=False,
            default=str,
        )

        content = (
            f"DOCUMENT TITLE:\n{document.title}\n\n"
            f"DOCUMENT TYPE:\n{document.doc_type}\n\n"
            f"EXISTING METADATA:\n{metadata_text}\n\n"
            f"DOCUMENT TEXT:\n{page_text}"
        )

        return {
            "id": document.id,
            "title": document.title,
            "sha256": document.sha256,
            "content": content[:MAX_DOCUMENT_CHARS],
        }


def record_usage(stats: dict, result) -> None:
    stats["tokens_in"] += result.tokens_in
    stats["tokens_out"] += result.tokens_out
    stats["cost_inr"] += result.cost_inr


async def extract_one(
    session_factory,
    gateway,
    prompt,
    document_id,
    stats,
    force,
) -> str:
    request_token = request_id_ctx.set(uuid.uuid4().hex)

    started_in = stats["tokens_in"]
    started_out = stats["tokens_out"]
    started_cost = stats["cost_inr"]

    try:
        snapshot = await load_document_snapshot(
            session_factory,
            document_id,
            force,
        )

        if snapshot is None:
            return "skipped"

        parsed, results, repaired = await extract_metadata(
            gateway,
            prompt,
            snapshot["content"],
        )

        for result in results:
            record_usage(stats, result)

        final_result = results[-1]

        async with session_factory() as session, session.begin():
            document = await session.scalar(
                select(Document).where(Document.id == document_id).with_for_update()
            )

            if document is None:
                return "skipped"

            current_metadata = dict(document.metadata_ or {})

            if current_metadata.get("quarantined") is True:
                return "skipped"

            if not force and "extracted" in current_metadata:
                return "skipped"

            if document.sha256 != snapshot["sha256"]:
                print(
                    f"SKIPPED STALE: {document_id} | {snapshot['title']}",
                    flush=True,
                )
                return "skipped"

            current_metadata["extracted"] = parsed.model_dump(mode="json")
            document.metadata_ = current_metadata

        label = "REPAIRED" if repaired else "EXTRACTED"

        print(
            f"{label}: {document_id} | {snapshot['title']} | "
            f"{final_result.provider}/{final_result.model} | "
            f"tokens_in={stats['tokens_in'] - started_in} "
            f"tokens_out={stats['tokens_out'] - started_out} "
            f"cost=Rs {stats['cost_inr'] - started_cost:.6f}",
            flush=True,
        )

        return "repaired" if repaired else "extracted"

    except LLMUnavailable as exc:
        print(f"LLM UNAVAILABLE: {document_id} | {exc}", flush=True)
        return "unavailable"

    except (ValidationError, ValueError) as exc:
        print(f"INVALID: {document_id} | {exc}", flush=True)
        return "invalid"

    except Exception as exc:
        print(
            f"FAILED: {document_id} | {type(exc).__name__}: {exc}",
            flush=True,
        )
        return "failed"

    finally:
        request_id_ctx.reset(request_token)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured metadata from HardenHelp documents."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of documents to process.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract existing metadata, excluding quarantined documents.",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than 0")

    settings = get_settings()
    prompt = load_prompt(settings.prompts_dir / "extract_metadata_v1.md")

    engine = make_engine(settings)
    session_factory = make_sessionmaker(engine)

    gateway = build_gateway(
        settings,
        make_recorder(session_factory),
    )

    if not gateway.providers:
        await engine.dispose()
        raise RuntimeError(
            "No LLM providers are configured. Check GEMINI_API_KEY and GROQ_API_KEY."
        )

    provider_order = []

    if settings.gemini_api_key:
        provider_order.append(f"gemini/{settings.llm_primary_model}")

    if settings.groq_api_key:
        provider_order.append(f"groq/{settings.llm_fallback_model}")

    stats = {
        "extracted": 0,
        "repaired": 0,
        "skipped": 0,
        "invalid": 0,
        "failed": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "cost_inr": 0.0,
    }

    stopped = False
    started = time.perf_counter()
    documents = []

    try:
        async with session_factory() as session:
            statement = (
                select(Document.id)
                .where(~Document.metadata_.contains({"quarantined": True}))
                .order_by(Document.id)
            )

            if not args.force:
                statement = statement.where(~Document.metadata_.has_key("extracted"))

            if args.limit is not None:
                statement = statement.limit(args.limit)

            documents = list((await session.scalars(statement)).all())

        print(f"Provider order: {' -> '.join(provider_order)}", flush=True)
        print(f"Documents selected: {len(documents)}", flush=True)

        for document_id in documents:
            outcome = await extract_one(
                session_factory,
                gateway,
                prompt,
                document_id,
                stats,
                args.force,
            )

            if outcome == "extracted":
                stats["extracted"] += 1
            elif outcome == "repaired":
                stats["repaired"] += 1
            elif outcome == "skipped":
                stats["skipped"] += 1
            elif outcome == "invalid":
                stats["invalid"] += 1
            elif outcome == "unavailable":
                stats["failed"] += 1
                stopped = True
                print(
                    "Stopping because all configured LLM providers are unavailable.",
                    flush=True,
                )
                break
            else:
                stats["failed"] += 1

    finally:
        for provider in gateway.providers:
            await provider._client.aclose()

        await engine.dispose()

    elapsed = time.perf_counter() - started

    count_engine = make_engine(settings)

    try:
        async with make_sessionmaker(count_engine)() as session:
            pending = await session.scalar(
                select(func.count())
                .select_from(Document)
                .where(
                    ~Document.metadata_.contains({"quarantined": True}),
                    ~Document.metadata_.has_key("extracted"),
                )
            )

            total = await session.scalar(select(func.count()).select_from(Document))

            quarantined = await session.scalar(
                select(func.count())
                .select_from(Document)
                .where(Document.metadata_.contains({"quarantined": True}))
            )
    finally:
        await count_engine.dispose()

    print("\nMetadata extraction summary:")
    print(f"Total documents: {total}")
    print(f"Quarantined:    {quarantined}")
    print(f"Extracted:      {stats['extracted']}")
    print(f"Repaired:       {stats['repaired']}")
    print(f"Skipped:        {stats['skipped']}")
    print(f"Invalid:        {stats['invalid']}")
    print(f"Failed:         {stats['failed']}")
    print(f"Pending:        {pending}")
    print(f"Tokens in:      {stats['tokens_in']}")
    print(f"Tokens out:     {stats['tokens_out']}")
    print(f"Cost:           Rs {stats['cost_inr']:.6f}")
    print(f"Seconds:        {elapsed:.1f}")

    if stopped:
        print("Status: Stopped because all configured LLM providers are unavailable")
    elif stats["invalid"] or stats["failed"]:
        print("Status: Completed with errors")
    else:
        print("Status: Completed")


if __name__ == "__main__":
    asyncio.run(main())
