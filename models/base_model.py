# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/23 20:20
# @File : base_model.py
from sqlalchemy import Column, Integer, TIMESTAMP, text
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    create_time = Column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    update_time = Column(
        TIMESTAMP,
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
