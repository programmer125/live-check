# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : room_crud.py
from models.room_model import Room
from crud.async_crud.base_crud import CRUDBase


class CRUDRoom(CRUDBase[Room]):
    pass


room = CRUDRoom(Room)
