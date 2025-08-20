# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_rt_room_qa import RtRoomQA
from crud.async_crud.base_crud import CRUDBase


class CRUDRtRoomQA(CRUDBase[RtRoomQA]):
    pass


neo_rt_room_qa = CRUDRtRoomQA(RtRoomQA, engine="neoailive")
