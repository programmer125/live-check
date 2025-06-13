# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 14:29
# @File : main.py
import sys
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.pool import AsyncAdaptedQueuePool
from starlette.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from configs.settings import settings
from web.api.api import api_router as api_router_v1
from web.middlewares.trace_id import TraceIdMiddleware
from web.schemas.response_schema import ResponseModel
from libs.log_client import Logger


logger = Logger(__file__)


# Core Application Instance
app = FastAPI(
    title=settings.service_name,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
)

# Add Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.async_db_uri,
    engine_args={
        "echo": False,
        "poolclass": AsyncAdaptedQueuePool,
        "pool_size": 2,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    },
)
app.add_middleware(TraceIdMiddleware)

# Add Routers
app.include_router(api_router_v1, prefix="/api")


async def exception_handler(_, exc: Exception):
    logger.error(f"全局异常:{traceback.format_exc()}")
    return ResponseModel(code=500, message=str(exc), data=False)


app.add_exception_handler(Exception, exception_handler)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=int(settings.api_port),
        reload=settings.reload,
    )
