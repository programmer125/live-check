# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : room_crud.py
from models.room_model import Room
from crud.async_crud.base_crud import CRUDBase
from models.soft_sugar_files import SoftSugarFiles


class CRUDSoftSugarFiles(CRUDBase[SoftSugarFiles]):
    pass


soft_sugar_files = CRUDSoftSugarFiles(SoftSugarFiles)
