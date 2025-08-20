# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_rt_room_global_element import RoomGlobalElement
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomGlobalElement(CRUDBase[RoomGlobalElement]):
    pass


neo_rt_room_global_element = CRUDRoomGlobalElement(
    RoomGlobalElement, engine="neoailive"
)
