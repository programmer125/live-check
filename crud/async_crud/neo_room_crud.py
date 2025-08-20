# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : neo_room_crud.py
from models.neo_room import NeoRoom
from crud.async_crud.base_crud import CRUDBase


class CRUDNeoRoom(CRUDBase[NeoRoom]):
    pass


neo_room = CRUDNeoRoom(NeoRoom, engine="neoailive")
