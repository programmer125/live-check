# coding:utf-8
import uuid

from loguru import logger
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class TraceIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next, *args, **kwargs) -> Response:
        trace_id = request.headers.get("traceid")
        if not trace_id:
            trace_id = uuid.uuid4().hex

        with logger.contextualize(traceid=trace_id):
            try:
                return await call_next(request)
            except Exception as ex:
                raise ex
