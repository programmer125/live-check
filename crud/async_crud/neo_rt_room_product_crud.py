# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_rt_room_product import RTRoomProduct
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomProduct(CRUDBase[RTRoomProduct]):
    pass


neo_rt_room_product = CRUDRoomProduct(RTRoomProduct, engine="neoailive")
