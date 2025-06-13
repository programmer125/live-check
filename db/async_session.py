# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/5/15 16:18
# @File : async_session.py
import aioredis

from configs.settings import settings


log_pool = aioredis.ConnectionPool.from_url(
    settings.log_redis_uri,
    decode_responses=True,
    max_connections=50,  # 最大连接数
    socket_keepalive=True,  # 保持长连接
    retry_on_timeout=True,  # 超时重试
    health_check_interval=30,  # 健康检查间隔
)
