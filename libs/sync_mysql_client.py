# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/12 17:11
# @File : sync_mysql_client.py
# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/2/28 17:25
# @File : mysql_client.py
from sqlalchemy import create_engine, text

from configs.settings import settings


class MysqlClient(object):
    def __init__(self, db_url):
        # 创建连接
        self.engine = create_engine(db_url)

    def fetch_one(self, sql):
        with self.engine.connect() as conn:
            response = conn.execute(text(sql))
            results = response.mappings().all()
            return results[0]

    def fetch_all(self, sql):
        with self.engine.connect() as conn:
            response = conn.execute(text(sql))
            results = response.mappings().all()
            return results

    def fetch_count(self, sql):
        with self.engine.connect() as conn:
            response = conn.execute(text(sql))
            results = response.mappings().all()
            return results[0]["cnt"]
