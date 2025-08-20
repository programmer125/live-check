# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_room_product import RoomProduct
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomProduct(CRUDBase[RoomProduct]):
    pass


neo_room_product = CRUDRoomProduct(RoomProduct, engine="neoailive")
