# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_room_reproduction_material import RoomReproductionMaterial
from crud.async_crud.base_crud import CRUDBase


class CRUDRoomReproductionMaterial(CRUDBase[RoomReproductionMaterial]):
    pass


neo_rt_room_reproduction_material = CRUDRoomReproductionMaterial(
    RoomReproductionMaterial, engine="neoailive"
)
