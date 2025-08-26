# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/1/14 16:38
# @File : sync_js_spider_client.py
from typing import Dict

import requests

from configs.settings import settings


class AlertClient:
    def __init__(self, max_retry=3, timeout=3):
        self.max_retry = max_retry
        self.timeout = timeout

        self.host = settings.alert_service_host

    def _request(self, route, body):
        """
        公共请求方法
        """
        url = "{}{}".format(self.host, route)

        try:
            exception = None
            for _ in range(self.max_retry):
                response = requests.post(url, json=body, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                exception = response.text

            raise Exception("重试多次失败: {}".format(exception))
        except Exception as exc:
            raise Exception("请求neoailive失败\nexc: {}\nurl: {}".format(exc, url))

    def send_error_message(self, message: str) -> Dict:
        body = {"status": 1, "title": "直播间发生异常", "description": message}
        data = self._request(f"/alert-forward/program_alert", body)
        if data["code"] != 0:
            raise Exception("发送消息失败，{}".format(data))
        return data["data"]

    def send_success_message(self, message: str) -> Dict:
        body = {"status": 2, "title": "直播间恢复正常", "description": message}
        data = self._request(f"/alert-forward/program_alert", body)
        if data["code"] != 0:
            raise Exception("发送消息失败，{}".format(data))
        return data["data"]


if __name__ == "__main__":
    AlertClient().send_error_message("测试")
