# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 17:39
# @File : session.py
import redis
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

from configs.settings import settings


playlist_engine = create_engine(
    settings.playlist_db_uri,
    echo=False,
    pool_size=2,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=QueuePool,
)
PlaylistSessionLocal = sessionmaker(bind=playlist_engine)


neoailive_engine = create_engine(
    settings.neoailive_db_uri,
    echo=False,
    pool_size=2,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=QueuePool,
)
NeoailiveSessionLocal = sessionmaker(bind=neoailive_engine)


log_pool = redis.ConnectionPool.from_url(
    settings.log_redis_uri,
    decode_responses=True,
    max_connections=50,  # 最大连接数
    socket_keepalive=True,  # 保持长连接
    retry_on_timeout=True,  # 超时重试
    health_check_interval=30,  # 健康检查间隔
)
