"""App factory: build a fully wired FastAPI app from settings."""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import APIRouter, FastAPI

from hardenhelp.api.errors import register_error_handlers
from hardenhelp.api.middleware import request_context
from hardenhelp.api.routes import chat, documents, health, ingest
from hardenhelp.config import Settings, get_settings
from hardenhelp.db.llm_calls import make_recorder
from hardenhelp.db.session import make_engine, make_sessionmaker
from hardenhelp.llm.gateway import build_gateway
from hardenhelp.logging_setup import setup_logging

logger = logging.getLogger("hardenhelp")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging(settings.log_level)
    engine = make_engine(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("starting", extra={"status": settings.app_env})
        worker = None

        if settings.worker_in_api:
            from hardenhelp.workers.main import run_embedded

            worker = asyncio.create_task(run_embedded(settings))

        yield

        if worker:
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker

        if getattr(app.state, "queue", None):
            await app.state.queue.close()

        await engine.dispose()

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)

    app.state.system_prompt = chat.load_prompt(settings.prompts_dir)
    app.state.classifier_prompt = chat.load_prompt(
        settings.prompts_dir,
        chat.CLASSIFIER_PROMPT_FILE,
    )

    app.state.gateway = build_gateway(
        settings,
        make_recorder(app.state.sessionmaker),
    )

    app.middleware("http")(request_context)
    register_error_handlers(app)

    v1 = APIRouter(prefix="/v1")
    v1.include_router(documents.router)
    v1.include_router(chat.router)
    v1.include_router(ingest.router)

    app.include_router(health.router)
    app.include_router(v1)

    return app
