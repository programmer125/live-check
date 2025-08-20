# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/12 17:11
# @File : sync_mysql_client.py
# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/2/28 17:25
# @File : mysql_client.py
from sqlalchemy import text


class MysqlClient(object):
    def __init__(self, db_session):
        # 创建连接
        self.db_session = db_session

    def fetch_one(self, sql):
        with self.db_session.begin():
            response = self.db_session.execute(text(sql))
            results = response.mappings().all()
            return results[0]

    def fetch_all(self, sql):
        with self.db_session.begin():
            response = self.db_session.execute(text(sql))
            results = response.mappings().all()
            return results

    def fetch_count(self, sql):
        with self.db_session.begin():
            response = self.db_session.execute(text(sql))
            results = response.mappings().all()
            return results[0]["cnt"]


if __name__ == "__main__":
    from db.session import PlaylistSessionLocal

    instance = MysqlClient(PlaylistSessionLocal())
    print(instance.fetch_count("select count(*) as cnt from rt_room limit 10"))
