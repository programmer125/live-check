# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/8/26 11:11
# @File : neo_room.py
from sqlalchemy import Column, BigInteger, SmallInteger
from models.base_model import Base


class NeoRoom(Base):
    __tablename__ = "n_room"
    __table_args__ = {"comment": "直播间"}

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    has_checked = Column(SmallInteger, comment="是否检测过")
