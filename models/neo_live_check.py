#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/12/4  上午11:54
# @Author  : tangshuqian
# @File    : room_dao.py
# @Software: PyCharm
from sqlalchemy import Column, Integer, SmallInteger, String, TIMESTAMP, text, DECIMAL
from models.base_model import Base


class NeoLiveCheck(Base):
    __tablename__ = "n_live_check"
    __table_args__ = {"comment": "直播检查表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    room_id = Column(Integer, nullable=True, comment="绑定内容ID")
    room_status = Column(Integer, nullable=True, comment="绑定内容ID")
    room_live_status = Column(Integer, nullable=True, comment="绑定内容ID")
    room_start_type = Column(Integer, nullable=True, comment="绑定内容ID")
    room_start_time = Column(TIMESTAMP, nullable=True, default=None, comment="开始时间")
    room_end_time = Column(TIMESTAMP, nullable=True, default=None, comment="结束时间")
    room_live_id = Column(String(128), default="", comment="直播间标题")
    content_id = Column(Integer, nullable=True, comment="绑定内容ID")
    content_status = Column(Integer, nullable=True, comment="绑定内容ID")
    content_live_status = Column(Integer, nullable=True, comment="绑定内容ID")
    content_is_rt = Column(SmallInteger, default=0, comment="状态：0正常；1删除")
    playlist_push_status = Column(Integer, nullable=True, comment="绑定内容ID")
    playlist_live_id = Column(String(128), default="", comment="直播间标题")
    playlist_live_url = Column(String(255), default="", comment="直播间标题")
    playlist_push_log = Column(String(255), default="", comment="直播间标题")
    auth_platform_id = Column(Integer, nullable=True, comment="绑定内容ID")
    auth_shop_name = Column(String(128), default="", comment="直播间标题")
    auth_short_name = Column(String(255), default="", comment="直播间标题")
    max_not_match_time = Column(TIMESTAMP, nullable=True, default=None, comment="结束时间")
    match_success_rate = Column(DECIMAL, nullable=True, default=None, comment="结束时间")
    effect_rate = Column(DECIMAL, nullable=True, default=None, comment="结束时间")
    effect_duration = Column(DECIMAL, nullable=True, default=None, comment="结束时间")
    pop_bag_time = Column(TIMESTAMP, nullable=True, default=None, comment="开始时间")
    push_error_count = Column(Integer, nullable=True, comment="绑定内容ID")
    is_error = Column(Integer, nullable=True, comment="绑定内容ID")
    error_msg = Column(String(255), default="", comment="直播间标题")
    is_ignore = Column(SmallInteger, default=0, comment="状态：0正常；1删除")
    status = Column(SmallInteger, default=0, comment="状态：0正常；1删除")
    create_time = Column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )
