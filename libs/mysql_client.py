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

    def exec_sql(self, sql):
        with self.engine.connect() as conn:
            response = conn.execute(text(sql))
            results = response.mappings().all()
            return results

    def exec_cnt_sql(self, sql):
        with self.engine.connect() as conn:
            response = conn.execute(text(sql))
            results = response.mappings().all()
            return results[0]["cnt"]


if __name__ == "__main__":
    sql = "SELECT count(*) as cnt FROM jd_crawl.tb_comments where STREAM_ID = '508704193583';"
    res = MysqlClient(settings.sync_jd_crawl_db_uri).exec_cnt_sql(sql)
    print(type(res))
    print(res)

    sql = "SELECT count(*) as cnt FROM pandora_db.t_command where live_id = '508704193583';"
    res = MysqlClient(settings.sync_pandora_db_uri).exec_cnt_sql(sql)
    print(type(res))
    print(res)
