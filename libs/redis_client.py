# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/28 17:03
# @File : redis_client.py
from typing import Optional
from redis import StrictRedis as Redis
from redis.exceptions import ConnectionError


class RedisManager:
    def __init__(self, uri: str = ""):
        self.uri = uri
        self.redis_client: Optional[Redis] = None

    def __enter__(self) -> Redis:
        try:
            # 从连接池获取连接
            self.redis_client = Redis.from_url(self.uri)
            # 测试连接
            self.redis_client.ping()

            return self.redis_client
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error connecting to Redis: {str(e)}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.redis_client:
                # 关闭Redis连接
                self.redis_client.close()
                self.redis_client = None
        except Exception as e:
            print(f"Error closing Redis connection: {str(e)}")
