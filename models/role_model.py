# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/27 17:30
# @File : role_model.py
from sqlalchemy import Column, Integer, String

from models.base_model import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"
    __table_args__ = {"comment": "角色表"}

    name = Column(String(255), nullable=False, comment="角色名")
    sort_id = Column(Integer, nullable=True, comment="排序id")
