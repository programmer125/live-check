# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 15:00
# @File : api.py
from fastapi import APIRouter
from web.api.v1 import demo


api_router = APIRouter()

api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
