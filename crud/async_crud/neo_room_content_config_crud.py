# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_room_content_config import RoomContentConfig
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomContentConfig(CRUDBase[RoomContentConfig]):
    pass


neo_room_content_config = CRUDRoomContentConfig(RoomContentConfig, engine="neoailive")
