#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/12/4  上午11:54
# @Author  : tangshuqian
# @File    : room_dao.py
# @Software: PyCharm
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, JSON
from models.base_model import Base


class NeoLiveComment(Base):
    __tablename__ = "n_live_comment"
    __table_args__ = {"comment": "直播评论表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    room_id = Column(Integer, nullable=True, comment="绑定内容ID")
    comment_id = Column(String(128), default="", comment="直播间标题")
    question = Column(JSON, nullable=True, comment="绑定内容ID")
    answer = Column(JSON, nullable=True, comment="绑定内容ID")
    is_match = Column(Integer, nullable=True, comment="绑定内容ID")
    crawl_time = Column(TIMESTAMP, nullable=True, default=None, comment="开始时间")
    match_time = Column(TIMESTAMP, nullable=True, default=None, comment="结束时间")
    effect_time = Column(TIMESTAMP, nullable=True, default=None, comment="结束时间")
    create_time = Column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
