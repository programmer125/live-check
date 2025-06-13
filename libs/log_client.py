# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/10 13:16
# @File : log_client.py
import sys
import json
import socket
from datetime import datetime

from loguru import logger

from configs.settings import settings
from libs.sync_remote_logger import LogFilter


# 移除默认的处理器
logger.remove()

# 添加控制台处理器
log_filter = LogFilter()
logger.add(sys.stdout, filter=log_filter)


class Logger:
    def __init__(self, file):
        self.file = file
        self.env = settings.env
        self.service_name = settings.service_name
        self.host = socket.gethostname()

        self.debug = self._wrap_log(logger.debug)
        self.info = self._wrap_log(logger.info)
        self.warning = self._wrap_log(logger.warning)
        self.error = self._wrap_log(logger.error)
        self.exception = self._wrap_log(logger.exception)

    def _wrap_log(self, log_func):
        def wrapped(*args, **kwargs):
            message = self.build_log(args[0])
            return log_func(message, **kwargs)

        return wrapped

    def build_log(self, msg):
        real_message = {
            "host": self.host,
            "env": self.env,
            "file": self.file,
            "service_name": self.service_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": msg,
        }
        return json.dumps(real_message)


if __name__ == "__main__":
    # 创建日志器实例
    instance = Logger(__name__)

    # instance.info("这是一条无traceid的日志")
    with logger.contextualize(traceid="12312"):
        instance.info("这是一条有traceid的日志")
