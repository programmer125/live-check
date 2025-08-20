# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from models.neo_user import User
from crud.async_crud.base_crud import CRUDBase


class CRUDUser(CRUDBase[User]):
    pass


neo_user = CRUDUser(User, engine="neoailive")
