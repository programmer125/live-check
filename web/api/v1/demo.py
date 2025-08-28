# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/3/28 13:52
# @File : demo.py
import traceback
from time import time

import redis
from fastapi import APIRouter, Query

import crud
from configs.settings import settings
from web.schemas.response_schema import ResponseModel
from libs.log_client import Logger


logger = Logger(__file__)
router = APIRouter()


@router.get("/manual_ignore", response_model=ResponseModel)
def manual_ignore(room_id: int = Query(...)):
    try:
        room = crud.neo_live_check.fetch_one(room_id=room_id)
        if not room:
            logger.info(f"直播间不存在")
            return ResponseModel(code=400, message="直播间不存在")

        # 忽略异常
        crud.neo_live_check.update_by_id(record_id=room["id"], data={"status": 1})
        crud.neo_room.update_by_id(record_id=room["room_id"], data={"has_checked": 1})

        logger.info(f"忽略成功：room_id={room_id}")
        return ResponseModel(message="忽略成功", data=room)
    except Exception as exc:
        logger.error(f"忽略失败:{traceback.format_exc()}")
        return ResponseModel(code=500, message=f"忽略失败：{exc}")


@router.get("/reset_comment_crawl_time", response_model=ResponseModel)
def reset_comment_crawl_time():
    try:
        conn = redis.from_url(settings.redis_uri)
        conn.set("live-check:reset_comment_crawl_time", str(time()))

        conn.delete("live-check:record_info")
        return ResponseModel(message="重置成功")
    except Exception as exc:
        logger.error(f"重置失败:{traceback.format_exc()}")
        return ResponseModel(code=500, message=f"重置失败：{exc}")
