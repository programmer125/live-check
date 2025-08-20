# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_rt_room_element_material_relation import RtRoomElementMaterialRelation
from crud.async_crud.base_crud import CRUDBase


class CRUDRtRoomQA(CRUDBase[RtRoomElementMaterialRelation]):
    pass


neo_rt_room_element_material_relation = CRUDRtRoomQA(
    RtRoomElementMaterialRelation, engine="neoailive"
)
