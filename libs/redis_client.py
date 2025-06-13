# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/28 17:03
# @File : redis_client.py
from typing import Optional

import redis
from redis.client import Redis as SyncRedis
import aioredis
from aioredis import Redis as AsyncRedis


class RedisManager:
    def __init__(self, connection_pool):
        """初始化时接收预配置的连接池"""
        self.connection_pool = connection_pool
        self.redis_client: Optional[SyncRedis] = None

    def __enter__(self) -> SyncRedis:
        # 从连接池获取连接
        self.redis_client = redis.Redis(connection_pool=self.connection_pool)
        # 测试连接
        self.redis_client.ping()

        return self.redis_client

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.redis_client:
            # 关闭Redis连接
            self.redis_client.close()
            self.redis_client = None


class AsyncRedisManager:
    def __init__(self, connection_pool):
        """初始化时接收预配置的连接池"""
        self.connection_pool = connection_pool
        self.redis_client: Optional[AsyncRedis] = None

    async def __aenter__(self) -> AsyncRedis:
        # 从连接池获取连接
        self.redis_client = aioredis.Redis(connection_pool=self.connection_pool)
        # 测试连接
        await self.redis_client.ping()

        return self.redis_client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
