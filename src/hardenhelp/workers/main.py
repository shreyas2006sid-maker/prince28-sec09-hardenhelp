"""The worker process:  uv run arq hardenhelp.workers.main.WorkerSettings

It runs the same code as the API, with the same settings and the same database. The only
difference is where its work comes from: Redis instead of HTTP.
"""

import asyncio
import logging

from arq.worker import Worker

from hardenhelp.config import Settings, get_settings
from hardenhelp.db.ingest_jobs import IngestRepository
from hardenhelp.db.llm_calls import make_recorder
from hardenhelp.db.session import make_engine, make_sessionmaker
from hardenhelp.ingest.fetch import make_client
from hardenhelp.llm.doc_meta import DocMeta
from hardenhelp.llm.extract import PROMPT_VERSION
from hardenhelp.llm.gateway import build_gateway
from hardenhelp.llm.prompts import load_prompt
from hardenhelp.logging_setup import setup_logging
from hardenhelp.workers.ingest import Pace, ingest_document
from hardenhelp.workers.queue import Queue, redis_settings

logger = logging.getLogger("hardenhelp.worker")


async def startup(ctx: dict) -> None:
    settings: Settings = ctx["settings"]
    if not ctx.get("embedded"):  # inside the API, logging is already set up
        setup_logging(settings.log_level)
        logging.getLogger("arq").handlers.clear()
    logging.getLogger("httpx").setLevel(logging.WARNING)

    engine = make_engine(settings)
    ctx["engine"], ctx["sessionmaker"] = engine, make_sessionmaker(engine)
    ctx["gateway"] = build_gateway(settings, make_recorder(ctx["sessionmaker"]))
    ctx["http"] = make_client(2)
    ctx["pace"] = Pace(settings.ingest_rpm)
    ctx["extract"] = None

    if ctx["gateway"].providers:
        try:
            prompt = load_prompt(settings.prompts_dir, PROMPT_VERSION)
        except FileNotFoundError:
            logger.warning(
                "prompt file %s.md not found: documents are parsed, not extracted",
                PROMPT_VERSION,
            )
        else:
            ctx["extract"] = {
                "schema": DocMeta,
                "prompt": prompt,
                "version": PROMPT_VERSION,
                "chars": 6000,
            }

    # Redis may have forgotten jobs (a restart without persistence). Postgres has not.
    async with ctx["sessionmaker"]() as session:
        lost = await Queue(ctx["redis"]).put(await IngestRepository(session).open_item_ids())
    logger.info("worker ready, %s unfinished item(s) put back in the queue", lost)


async def shutdown(ctx: dict) -> None:
    await ctx["http"].aclose()
    await ctx["engine"].dispose()


def worker_options(settings: Settings, *, embedded: bool = False) -> dict:
    return {
        "functions": [ingest_document],
        "on_startup": startup,
        "on_shutdown": shutdown,
        "redis_settings": redis_settings(settings.redis_url),
        "ctx": {"settings": settings, "embedded": embedded},
        "max_jobs": settings.ingest_concurrency,
        "job_timeout": settings.ingest_job_timeout,
        "max_tries": settings.ingest_max_tries,
        "keep_result": 0,
        "poll_delay": 1.0,
    }


async def run_embedded(settings: Settings) -> None:
    """A worker inside the API process, for hosts that offer no free worker service."""
    worker = Worker(**worker_options(settings, embedded=True), handle_signals=False)
    try:
        await worker.async_run()
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("the embedded worker stopped: is REDIS_URL right?")
    finally:
        await worker.close()


# What the `arq` command reads. Built from .env like everything else.
WorkerSettings = worker_options(get_settings())
