# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/13 14:27
# @File : check.py
from configs.settings import settings
from libs.sync_es_client import ESClient
from libs.sync_mysql_client import MysqlClient


class Check(object):
    def __init__(self):
        self.es_manager = ESClient(
            host=settings.es_host, user=settings.es_user, password=settings.es_password
        )
        self.neo_db = MysqlClient(settings.neoailive_db_uri)
        self.playlist_db = MysqlClient(settings.playlist_db_uri)

    def get_platform_name(self, platform_id):
        if platform_id == 1:
            return "京东"
        elif platform_id == 2:
            return "淘宝"
        elif platform_id == 3:
            return "唯品会"
        elif platform_id == 4:
            return "拼多多"
        else:
            return "未知"

    def check_shop_info(self, content_id):
        print("直播检测")

        content = self.neo_db.fetch_one(
            "select name, outside_auth_id, buy_version from neoailive_db.n_room_content where id = {}".format(
                content_id
            )
        )
        if not content:
            print("直播内容不存在")
            return

        outside_auth = self.neo_db.fetch_one(
            "select platform_id, shop_name from neoailive_db.n_outside_auth where id = {}".format(
                content["outside_auth_id"]
            )
        )
        if not outside_auth:
            print("直播内容授权信息不存在")
            return

        print("授权：{}".format("已授权"))
        print("版本：{}".format("标准版" if content["buy_version"] == 1 else "实时版"))
        print("平台：{}".format(self.get_platform_name(outside_auth["platform_id"])))
        print("店铺：{}".format(outside_auth["shop_name"]))

    def check_neo_start(self, room_id):
        # 查询最后一次开播
        start_rooms = self.es_manager.search(
            "neoailive-api-service",
            body={
                "size": 500,
                "sort": [{"@timestamp": {"order": "desc", "unmapped_type": "boolean"}}],
                "version": True,
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [
                            {
                                "bool": {
                                    "filter": [
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": "开始直播返回",
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": str(room_id),
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": "开播成功",
                                                "lenient": True,
                                            }
                                        },
                                    ]
                                }
                            },
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )
        latest_start_room = self.es_manager.get_first_result(start_rooms)

        print("后端开播检测")
        if latest_start_room:
            print("开播时间：{}".format(latest_start_room["timestamp"]))
            return

        print("未检测到开播触发")

    def check_playlist_start(self, room_id):
        # 查询最后一次开播
        start_rooms = self.es_manager.search(
            "room-lifespan",
            body={
                "size": 500,
                "sort": [{"@timestamp": {"order": "desc", "unmapped_type": "boolean"}}],
                "version": True,
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [
                            {
                                "bool": {
                                    "filter": [
                                        {
                                            "bool": {
                                                "should": [
                                                    {"match": {"room_id": str(room_id)}}
                                                ],
                                                "minimum_should_match": 1,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": "start_push_api",
                                                "lenient": True,
                                            }
                                        },
                                    ]
                                }
                            }
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )
        latest_start_room = self.es_manager.get_first_result(start_rooms)

        print("播单开播检测")
        if latest_start_room:
            print("开播时间：{}".format(latest_start_room["timestamp"]))
            return

        print("未检测到开播触发")

    def check_warm_file(self, room_id):
        pass

    def check(self, room_id):
        neo_room = self.neo_db.fetch_one(
            "select * from neoailive_db.n_room where id = {}".format(room_id)
        )
        if not neo_room:
            print("直播场次不存在")
            return

        self.check_shop_info(neo_room["bind_content_id"])
        print()

        self.check_neo_start(room_id)
        print()

        self.check_playlist_start(room_id)
        print()


if __name__ == "__main__":
    # Check().check(6286)
    Check().check(6576)
