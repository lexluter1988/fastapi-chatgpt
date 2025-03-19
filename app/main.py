from __future__ import annotations

import asyncio

from chainlit.utils import mount_chainlit
from fastapi import FastAPI

from app.frontend_api.chats.demon import consume_responses_futures
from app.backend_api.llm_worker.llm_worker_generic import llm_worker_generic
# from app.frontend_api.auth.db import create_db_and_tables
# from app.frontend_api.auth.logic import auth_backend, fastapi_users
# from app.frontend_api.auth.schemas import UserCreate, UserRead
from app.logger import setup_logging
from app.settings import get_settings

settings = get_settings()


async def start_demons():
    # asyncio.create_task(llm_worker_generic()
    asyncio.create_task(consume_responses_futures())


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

    # app.include_router(
    #     fastapi_users.get_auth_router(auth_backend), prefix='/api/auth/jwt', tags=['auth']
    # )
    # app.include_router(
    #     fastapi_users.get_register_router(UserRead, UserCreate),
    #     prefix='/api/auth',
    #     tags=['auth'],
    # )
    # app.add_event_handler('startup', create_db_and_tables)
    app.add_event_handler('startup', start_demons)

    mount_chainlit(app=app, target="app/frontend_api/chats/chainlit.py", path="/api/chat")

    return app


application = get_application()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(application, host='0.0.0.0', port=8000)
