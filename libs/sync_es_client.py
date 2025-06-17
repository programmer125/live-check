# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/12 17:48
# @File : sync_es_client.py
from typing import Dict, List

import requests


class ESClient:
    def __init__(self, host: str, user: str = None, password: str = None):
        """初始化 ES 索引管理器"""
        self.host = host.rstrip("/")
        self.session = requests.Session()

        # 设置认证
        if user and password:
            self.session.auth = (user, password)

        # 设置通用请求头
        self.session.headers.update({"Content-Type": "application/json"})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送请求并处理错误"""
        url = f"{self.host}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e.response, "text"):
                print(f"错误详情: {e.response.text}")
            raise

    def format_result(self, data):
        result = []
        for elm in data.get("hits", {}).get("hits", []):
            result.append(elm["_source"])

        return result

    def search(self, index: str, body: Dict) -> List:
        response = self._make_request(
            "GET",
            f"/{index}-*/_search",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        return self.format_result(response.json())

    def search_count(self, index: str, body: Dict) -> int:
        response = self._make_request(
            "GET",
            f"/{index}-*/_search",
            json=body,
            headers={"Content-Type": "application/json"},
        )
        data = response.json()
        return data.get("hits", {})
