# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_room_qa import RoomQA
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomQA(CRUDBase[RoomQA]):
    pass


neo_room_qa = CRUDRoomQA(RoomQA, engine="neoailive")
