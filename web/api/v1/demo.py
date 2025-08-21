# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/3/28 13:52
# @File : demo.py
import traceback

from fastapi import APIRouter, Query

import crud
from web.schemas.response_schema import ResponseModel
from libs.log_client import Logger


logger = Logger(__file__)
router = APIRouter()


@router.get("/manual_ignore", response_model=ResponseModel)
def manual_ignore(room_id: int = Query(...)):
    try:
        room = crud.neo_live_check.fetch_one(room_id=room_id)
        if not room:
            logger.info(f"直播间不存在，无法开播")
            return ResponseModel(code=400, message="直播间不存在")

        # 设置待预热
        crud.neo_live_check.update_by_id(record_id=room["id"], data={"is_ignore": 1})

        logger.info(f"忽略成功：room_id={room_id}")
        return ResponseModel(message="忽略成功", data=room)
    except Exception as exc:
        logger.error(f"忽略失败:{traceback.format_exc()}")
        return ResponseModel(code=500, message=f"忽略失败：{exc}")
