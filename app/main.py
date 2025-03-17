from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.agent.demon import consume_responses_websockets
from app.agent.llm_worker_generic import llm_worker_generic
from app.auth.db import create_db_and_tables
from app.auth.logic import auth_backend, fastapi_users
from app.auth.schemas import UserCreate, UserRead
from app.logger import setup_logging
from app.settings import get_settings
from app.state import active_connections
from app.test_app.views import test_app_router

settings = get_settings()


async def start_demons():
    asyncio.create_task(llm_worker_generic())
    asyncio.create_task(consume_responses_websockets(active_connections=active_connections))

def get_application() -> FastAPI:
    setup_logging(settings=settings)

    app = FastAPI(
        openapi_url='/api/openapi.json',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        debug=settings.debug,
        version=settings.app_version or '0.1.0',
        title='Starter FastApi with FastApi users',
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix='/api/auth/jwt', tags=['auth']
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix='/api/auth',
        tags=['auth'],
    )
    app.include_router(test_app_router, prefix='/api/test')

    app.add_event_handler('startup', create_db_and_tables)
    app.add_event_handler('startup', start_demons)

    return app


application = get_application()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(application, host='0.0.0.0', port=8000)
