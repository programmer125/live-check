# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/28 16:55
# @File : redis_logger.py
import json
import logging
import socket
from time import time
from typing import Any, Dict
from logging import LogRecord
from datetime import datetime

from configs.settings import settings
from libs.redis_client import RedisManager


class RedisHandler(logging.Handler):
    def __init__(self, redis_uri: str, redis_key: str):
        super().__init__()
        self.redis_uri = redis_uri
        self.redis_key = redis_key

        self.host = socket.gethostname()
        self.env = settings.env

    def build_log(self, record: LogRecord) -> Dict[str, Any]:
        # 基础日志信息
        data = {
            "host": self.host,
            "env": self.env,
            "file": record.name,
            "log_level": record.levelname,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        message = json.loads(record.getMessage())
        data.update(message)

        if settings.env == "local":
            print(data["message"])

        return data

    def emit(self, record: LogRecord) -> None:
        try:
            # 构建日志消息
            log = self.build_log(record)
            # 写入redis
            with RedisManager(self.redis_uri) as client:
                client.rpush(self.redis_key, json.dumps(log))
        except Exception as e:
            print(f"Error writing to Redis: {str(e)}")


class RoomLifespanLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name, level)
        self.redis_uri = settings.prod_log_redis_uri
        self.redis_key = settings.prod_log_redis_key

        self.freeze_fields = {
            "service_name": "mirror-room-lifespan",
        }

        # 添加处理器
        handler = RedisHandler(self.redis_uri, self.redis_key)
        self.addHandler(handler)

    def build_log(self, *args, **kwargs):
        if kwargs:
            message = dict(kwargs)
        else:
            message = {}
        message.update(self.freeze_fields)
        message["timestamp_ms"] = int(time() * 1000000)
        message["message"] = args[0]

        return message

    def info(self, *args, **kwargs):
        message = self.build_log(*args, **kwargs)
        super().info(json.dumps(message))

    def error(self, *args, **kwargs):
        message = self.build_log(*args, **kwargs)
        super().error(json.dumps(message))

    def critical(self, *args, **kwargs):
        message = self.build_log(*args, **kwargs)
        super().critical(json.dumps(message))
