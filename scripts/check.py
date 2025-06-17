# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/13 14:27
# @File : check.py
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
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

    def check_auth(self, content_id):
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

        return content

    def check_neo_start(self, room_id):
        # 查询最后一次开播
        _, logs = self.es_manager.search(
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

        if logs:
            for log in logs:
                print("开播时间：{}".format(log["timestamp"]))
            return

        print("未检测到开播触发")

    def check_playlist_start(self, room_id, buy_version):
        # 标准版
        if buy_version == 1:
            playlist_room = self.playlist_db.fetch_one(
                "select * from playlist_control.room where bind_id = {}".format(room_id)
            )

            _, logs = self.es_manager.search(
                "room-lifespan",
                body={
                    "size": 1,
                    "sort": [
                        {"@timestamp": {"order": "asc", "unmapped_type": "boolean"}}
                    ],
                    "version": True,
                    "query": {
                        "bool": {
                            "must": [],
                            "filter": [
                                {"match_phrase": {"room_id": playlist_room["bind_id"]}},
                                {"match_phrase": {"minor_step": "video_start"}},
                            ],
                            "should": [],
                            "must_not": [],
                        }
                    },
                },
            )
            if logs:
                print("开播时间：{}".format(logs[0]["timestamp"]))
            else:
                print("推流未开播")
        else:
            playlist_room = self.playlist_db.fetch_one(
                "select * from playlist_control.rt_room where bind_id = {}".format(
                    room_id
                )
            )

        return playlist_room

    def check_third_live(self, playlist_room):
        _, logs = self.es_manager.search(
            "room-lifespan",
            body={
                "size": 1,
                "sort": [{"@timestamp": {"order": "asc", "unmapped_type": "boolean"}}],
                "version": True,
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [
                            {
                                "multi_match": {
                                    "type": "phrase",
                                    "query": "update_live_id_api",
                                    "lenient": True,
                                }
                            },
                            {"match_phrase": {"room_id": playlist_room["bind_id"]}},
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )
        if logs:
            print("关联live_id时间：{}".format(logs[0]["timestamp"]))
        else:
            print("未关联live_id")

        _, logs = self.es_manager.search(
            "room-lifespan",
            body={
                "size": 1,
                "sort": [{"@timestamp": {"order": "asc", "unmapped_type": "boolean"}}],
                "version": True,
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [
                            {
                                "multi_match": {
                                    "type": "phrase",
                                    "query": "update_cart_list_api",
                                    "lenient": True,
                                }
                            },
                            {"match_phrase": {"room_id": playlist_room["bind_id"]}},
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )
        if logs:
            print("关联cart_list时间：{}".format(logs[0]["timestamp"]))
        else:
            print("未关联cart_list")

    def check_playlist_pop_bag(self, playlist_room, buy_version):
        # 标准版
        if buy_version == 1:
            count, logs = self.es_manager.search(
                "room-lifespan",
                body={
                    "size": 1,
                    "sort": [
                        {"@timestamp": {"order": "desc", "unmapped_type": "boolean"}}
                    ],
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
                                                        {
                                                            "match_phrase": {
                                                                "room_id": playlist_room[
                                                                    "bind_id"
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                            {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "match_phrase": {
                                                                "minor_step": "monitor_pop_bag_task"
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                            {
                                                "multi_match": {
                                                    "type": "phrase",
                                                    "query": "触发弹袋",
                                                    "lenient": True,
                                                }
                                            },
                                            {
                                                "multi_match": {
                                                    "type": "phrase",
                                                    "query": "success",
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
        else:
            count = 0
            logs = []

        if count:
            print(f"弹袋次数：{count}")
            print(f"最后一次弹袋时间：{logs[0]['timestamp']}")
        else:
            print("弹袋次数：0")

    def check_playlist_qa(self, playlist_room, buy_version):
        # 标准版
        if buy_version == 1:
            count, logs = self.es_manager.search(
                "room-lifespan",
                body={
                    "size": 5,
                    "sort": [
                        {"@timestamp": {"order": "desc", "unmapped_type": "boolean"}}
                    ],
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
                                                        {
                                                            "match": {
                                                                "room_id": playlist_room[
                                                                    "bind_id"
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                            {
                                                "bool": {
                                                    "should": [
                                                        {"match": {"video_type": 2}}
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                        ]
                                    }
                                },
                                {"match_phrase": {"minor_step": "video_start"}},
                            ],
                            "should": [],
                            "must_not": [],
                        }
                    },
                },
            )
        else:
            count = 0
            logs = []

        if count:
            print(f"强互动次数：{count}")
            for log in logs:
                print(f"强互动时间：{log['timestamp']}")
        else:
            print("强互动次数：0")

    def check_playlist_atmosphere(self, playlist_room, buy_version):
        # 标准版
        if buy_version == 1:
            count, logs = self.es_manager.search(
                "room-lifespan",
                body={
                    "size": 5,
                    "sort": [
                        {"@timestamp": {"order": "desc", "unmapped_type": "boolean"}}
                    ],
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
                                                        {
                                                            "match": {
                                                                "room_id": playlist_room[
                                                                    "bind_id"
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                            {
                                                "bool": {
                                                    "should": [
                                                        {"match": {"video_type": 3}}
                                                    ],
                                                    "minimum_should_match": 1,
                                                }
                                            },
                                        ]
                                    }
                                },
                                {"match_phrase": {"minor_step": "video_start"}},
                            ],
                            "should": [],
                            "must_not": [],
                        }
                    },
                },
            )
        else:
            count = 0
            logs = []

        if count:
            print(f"弱互动次数：{count}")
            for log in logs:
                print(f"弱互动时间：{log['timestamp']}")
        else:
            print("弱互动次数：0")

    def check_neo_stop(self, playlist_room):
        # 手动关播
        _, logs = self.es_manager.search(
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
                                                "query": "停止在播直播房间",
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": str(playlist_room["bind_id"]),
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

        if logs:
            for log in logs:
                print("手动关播时间：{}".format(log["timestamp"]))
            return

        # 自动关播
        _, logs = self.es_manager.search(
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
                                                "query": "自动关闭直播",
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": str(playlist_room["bind_id"]),
                                                "lenient": True,
                                            }
                                        },
                                    ]
                                }
                            },
                            {"match_phrase": {"traceid": "auto_close_live"}},
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )

        if logs:
            for log in logs:
                print("自动关播时间：{}".format(log["timestamp"]))
            return

        # 第三方关播
        _, logs = self.es_manager.search(
            "living-assistant-service",
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
                                                "query": "直播间已关闭",
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": str(playlist_room["bind_id"]),
                                                "lenient": True,
                                            }
                                        },
                                    ]
                                }
                            },
                            {"match_phrase": {"traceid": "check-close"}},
                        ],
                        "should": [],
                        "must_not": [],
                    }
                },
            },
        )

        if logs:
            for log in logs:
                print("第三方关播时间：{}".format(log["timestamp"]))
            return

        print("未检测到关播触发")

    def check_playlist_stop(self, playlist_room, buy_version):
        # 标准版
        if buy_version == 1:
            _, logs = self.es_manager.search(
                "room-lifespan",
                body={
                    "size": 1,
                    "sort": [
                        {"@timestamp": {"order": "asc", "unmapped_type": "boolean"}}
                    ],
                    "version": True,
                    "query": {
                        "bool": {
                            "must": [],
                            "filter": [
                                {"match_phrase": {"room_id": playlist_room["bind_id"]}},
                                {"match_phrase": {"minor_step": "stop_push"}},
                            ],
                            "should": [],
                            "must_not": [],
                        }
                    },
                },
            )
            if logs:
                print("推流结束时间：{}".format(logs[0]["timestamp"]))
            else:
                print("推流未结束")
        else:
            pass

    def check(self, room_id):
        neo_room = self.neo_db.fetch_one(
            "select * from neoailive_db.n_room where id = {}".format(room_id)
        )
        if not neo_room:
            print("直播场次不存在")
            return

        print("授权检测")
        content = self.check_auth(neo_room["bind_content_id"])
        print()

        print("后端开播检测")
        self.check_neo_start(room_id)
        print()

        print("播单控制开播检测")
        playlist_room = self.check_playlist_start(room_id, content["buy_version"])
        print()

        print("第三方直播关联检测")
        self.check_third_live(playlist_room)
        print()

        print("弹袋监测")
        self.check_playlist_pop_bag(playlist_room, content["buy_version"])
        print()

        print("强互动监测")
        self.check_playlist_qa(playlist_room, content["buy_version"])
        print()

        print("弱互动监测")
        self.check_playlist_atmosphere(playlist_room, content["buy_version"])
        print()

        # 检测neo关播
        print("后端关播检测")
        self.check_neo_stop(playlist_room)
        print()

        # 检测播单关播
        print("播单关播检测")
        self.check_playlist_stop(playlist_room, content["buy_version"])
        print()


if __name__ == "__main__":
    # Check().check(6286)
    # Check().check(6576)
    # 标准-开播异常
    # Check().check(6631)
    # 标准-正常
    Check().check(6709)
