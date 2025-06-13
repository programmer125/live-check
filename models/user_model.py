# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/27 17:30
# @File : content_model.py
from sqlalchemy import Column, Integer, String

from models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    username = Column(String(255), nullable=False, comment="用户名")
    phone = Column(String(255), nullable=True, comment="手机")
    role_id = Column(Integer, nullable=False, comment="role_id")
