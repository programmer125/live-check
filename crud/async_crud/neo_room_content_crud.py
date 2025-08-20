# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_room_content import RoomContent
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomContent(CRUDBase[RoomContent]):
    pass


neo_room_content = CRUDRoomContent(RoomContent, engine="neoailive")
