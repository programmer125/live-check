# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_rt_room_extend_element_material_relation import (
    RtRoomExtendElementMaterialRelation,
)
from crud.async_crud.base_crud import CRUDBase


class CRUDRtRoomExtendElementMaterialRelation(
    CRUDBase[RtRoomExtendElementMaterialRelation]
):
    pass


neo_rt_room_extend_element_material_relation = CRUDRtRoomExtendElementMaterialRelation(
    RtRoomExtendElementMaterialRelation, engine="neoailive"
)
