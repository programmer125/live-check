# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/3/28 13:52
# @File : demo.py
import json
import time
import asyncio

from fastapi import APIRouter, Request, Query
from web.schemas.response_schema import ResponseModel
from crud import async_crud

router = APIRouter()


@router.post("/any_forward", response_model=ResponseModel)
async def any_forward(request: Request):
    body_bytes = await request.body()
    body = json.loads(body_bytes)

    roles = [
        {"name": "admin"},
        {"name": "user"},
        {"name": "guest"},
    ]
    users = [
        {"username": "admin", "phone": "12345678901", "role_name": "admin"},
        {"username": "user", "phone": "12345678902", "role_name": "user"},
    ]

    res = await async_crud.user.create_with_role(users=users, roles=roles)

    return ResponseModel(data=body)


@router.get("/async_hello", response_model=ResponseModel)
async def async_hello():
    return ResponseModel(data="async hello world")


@router.get("/sync_hello", response_model=ResponseModel)
def sync_hello():
    return ResponseModel(data="sync hello world")


@router.get("/async_block", response_model=ResponseModel)
async def async_block(interval: int = Query(...), is_sync: bool = Query(...)):
    if is_sync:
        time.sleep(interval)
    else:
        await asyncio.sleep(interval)

    return ResponseModel(data="async sleep end")


@router.get("/sync_block", response_model=ResponseModel)
def sync_block(interval: int = Query(...)):
    time.sleep(interval)

    return ResponseModel(data="sync sleep end")
