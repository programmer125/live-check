# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/8/20 11:35
# @File : monitor_all_rooms.py
import sys
from collections import namedtuple, defaultdict
from copy import deepcopy
from time import sleep, time
from pathlib import Path
from datetime import datetime, timedelta

import loguru

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from configs.settings import settings
import crud
from db.session import PlaylistSessionLocal, NeoailiveSessionLocal
from libs.sync_es_client import ESClient
from libs.sync_mysql_client import MysqlClient
from libs.log_client import Logger
from libs.sync_alert_client import AlertClient
from libs.check_client import CheckClient


logger = Logger(__file__)


ERROR = namedtuple("ERROR", ["code", "priority", "message"])
COOKIE_EXPIRE = ERROR(1, 1, "cookie已过期")
NEO_STATUS_INCONSISTENT = ERROR(1, 1, "直播内容与直播间状态不一致")
PUSH_STATUS_INCONSISTENT = ERROR(1, 1, "直播间与推流状态不一致")


class MonitorAllRooms(object):
    def __init__(self):
        self.check_client = CheckClient()
        self.alert_client = AlertClient()

        self.playlist_session = PlaylistSessionLocal()
        self.playlist_client = MysqlClient(self.playlist_session)

        self.neoailive_session = NeoailiveSessionLocal()
        self.neoailive_client = MysqlClient(self.neoailive_session)

        self.es_manager = ESClient(
            host=settings.es_host, user=settings.es_user, password=settings.es_password
        )

        self.comment_crawl_time = self.check_client.get_comment_crawl_time()

        self.link_url = "http://114.132.162.71:3000/d/bew1ihhgk9a80b/e79b91-e68ea7-e5a4a7-e79b98-e8afa6-e68385?folderUid=aeapw6qsrjfggd&orgId=1&from=now-6h&to=now&timezone=browser&refresh=5s&var-query0=&var-room_id={}&tab=transformations"

    def send_alert_message(self, record):
        room_id = record["room_id"]
        cache_info = self.check_client.get_record_cache(room_id)
        if record["is_error"] == 1:
            if cache_info:
                if cache_info.get("last_send_time"):
                    # 已经发送过的记录，每小时提醒一次
                    if time() - cache_info.get("last_send_time") > 60 * 60:
                        self.alert_client.send_error_message(
                            "场次 <a href='{}'>{}</a> ({})\n{}".format(
                                self.link_url.format(room_id),
                                room_id,
                                record["auth_shop_name"],
                                record["error_msg"],
                            )
                        )
                        cache_info["last_send_time"] = time()
                        cache_info["error_msg"] = record["error_msg"]
                        self.check_client.set_record_cache(room_id, cache_info)
                else:
                    # 首次出错持续20分钟后发送提醒
                    if time() - cache_info.get("first_time") > 60 * 20:
                        self.alert_client.send_error_message(
                            "场次 <a href='{}'>{}</a> ({})\n{}".format(
                                self.link_url.format(room_id),
                                room_id,
                                record["auth_shop_name"],
                                record["error_msg"],
                            )
                        )
                        cache_info["last_send_time"] = time()
                        cache_info["error_msg"] = record["error_msg"]
                        self.check_client.set_record_cache(room_id, cache_info)
            else:
                self.check_client.set_record_cache(
                    room_id, {"first_time": time(), "error_msg": record["error_msg"]}
                )
        else:
            if cache_info:
                if cache_info.get("last_send_time"):
                    self.alert_client.send_success_message(
                        "场次 <a href='{}'>{}</a> ({}) 已恢复\n{}".format(
                            self.link_url.format(room_id),
                            room_id,
                            record["auth_shop_name"],
                            cache_info.get("error_msg"),
                        )
                    )
                self.check_client.delete_record_cache(room_id)

    # 查找销销所有未关闭的直播，与推流未结束的直播间，取并集
    def get_neo_rooms(self):
        # 2025-08-19 手动将所有异常状态回正，这之前的弃播不再处理
        neo_rooms = self.neoailive_client.fetch_all(
            "SELECT * FROM neoailive_db.n_room where has_checked = 0 and create_time > '2025-08-19'"
        )
        return [dict(elm) for elm in neo_rooms]

    def get_neo_contents(self, content_ids):
        content_ids = ",".join([str(elm) for elm in content_ids])
        contents = self.neoailive_client.fetch_all(
            f"SELECT * FROM neoailive_db.n_room_content where id in ({content_ids})"
        )
        return {elm["id"]: dict(elm) for elm in contents}

    def get_neo_auths(self, auth_ids):
        auth_ids = ",".join([str(elm) for elm in auth_ids])
        auths = self.neoailive_client.fetch_all(
            f"SELECT * FROM neoailive_db.n_outside_auth where id in ({auth_ids})"
        )
        return {elm["id"]: dict(elm) for elm in auths}

    def convert_stander_status(self, status):
        # 1 初始化、2 已推流、3 结束推流、4 废弃
        return status

    def convert_realtime_status(self, status):
        # 1 待预热、2 待推流、3 推流中、4 待关播、5 已关播、10 异常
        if status in [1, 2]:
            return 1
        elif status == 3:
            return 2
        elif status in [4, 5]:
            return 3
        else:
            return 4

    # 查找销销直播关联的推流任务
    def get_playlist_room_by_bind_id(self, bind_ids):
        bind_ids = ",".join([str(elm) for elm in bind_ids])
        # 标准直播间
        stander_rooms = self.playlist_client.fetch_all(
            f"SELECT * FROM playlist_control.room where bind_id in ({bind_ids})"
        )
        realtime_rooms = self.playlist_client.fetch_all(
            f"SELECT * FROM playlist_control.rt_room where bind_id in ({bind_ids})"
        )

        result = {}
        for room in stander_rooms:
            room = dict(room)
            room["push_status"] = self.convert_stander_status(room["status"])
            result[room["bind_id"]] = room

        for room in realtime_rooms:
            room = dict(room)
            room["push_status"] = self.convert_realtime_status(room["status"])
            result[room["bind_id"]] = room

        return result

    def check_neoailive_reason(self, room_id, reason):
        count, logs = self.es_manager.search(
            "neoailive-api-service",
            body={
                "size": 10,
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
                                                "query": reason,
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

        if count:
            return True
        return False

    def check_assistant_reason(self, room_id, reason):
        count, logs = self.es_manager.search(
            "living-assistant-service",
            body={
                "size": 10,
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
                                                "query": reason,
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

        if count:
            return True
        return False

    # 检查弃播的是否是出于正常原因
    def check_adandon_is_normal(self, neo_room, neo_auth):
        for reason in ["废弃未在播直播房间", "超时关闭直播", "已达最大可开播数量"]:
            if self.check_neoailive_reason(neo_room["id"], reason):
                return True

        if self.check_assistant_reason(neo_room["id"], "开播不成功"):
            return True

        self.alert_client.send_error_message(
            "场次 <a href='{}'>{}</a> ({})\n因为 未知原因 弃播".format(
                self.link_url.format(neo_room["id"]),
                neo_room["id"],
                neo_auth.get("shop_name"),
            )
        )
        return False

    def get_playlist_push_log_url(self, is_rt, room_id, playlist_room):
        if is_rt:
            machine_id = playlist_room.get("machine_id")
            if machine_id == "aliyun01":
                log_url = f"http://8.136.102.77:6860/logs/start_room_{room_id}.log"
            elif machine_id == "aliyun02":
                log_url = f"http://8.149.232.230:6860/logs/start_room_{room_id}.log"
            elif machine_id == "aliyun03":
                log_url = f"http://47.99.167.107:6860/logs/start_room_{room_id}.log"
            elif machine_id == "aliyun04":
                log_url = f"http://120.26.230.58:6860/logs/start_room_{room_id}.log"
            else:
                log_url = ""
        else:
            log_url = ""

        return log_url

    def get_pop_bag_time(self, room_id):
        count, logs = self.es_manager.search(
            "room-lifespan",
            body={
                "size": 1,
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
                                                    {"match": {"room_id": room_id}}
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
                                                "query": "'message': 'success'",
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

        if count:
            return datetime.strptime(logs[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
        return datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    def get_comment_metric(self, room_id):
        # 获取所有评论内容
        comments = self.neoailive_client.fetch_all(
            "select is_match, crawl_time, match_time, effect_time from neoailive_db.n_live_comment where room_id = {} and crawl_time > '{}' order by crawl_time desc".format(
                room_id, self.comment_crawl_time
            )
        )

        # 评论相关的统计
        match_success_count = 0
        match_fail_count = 0
        effect_count = 0
        effect_duration = 0
        for comment in comments:
            if comment["is_match"] == 1:
                # 匹配成功
                match_success_count += 1

                if comment["effect_time"]:
                    effect_count += 1
                    effect_duration += (
                        comment["effect_time"] - comment["crawl_time"]
                    ).total_seconds()
            elif comment["is_match"] == 2:
                # 匹配失败
                match_fail_count += 1
            else:
                pass

        max_not_match_time = None
        for comment in comments:
            if comment["is_match"] == 0:
                max_not_match_time = comment["crawl_time"]
            else:
                break

        if match_success_count + match_fail_count > 0:
            match_success_rate = match_success_count / (
                match_success_count + match_fail_count
            )
        else:
            match_success_rate = 1

        if match_success_count > 0:
            effect_rate = effect_count / match_success_count
        else:
            effect_rate = 1

        if effect_count > 0:
            effect_duration = effect_duration / effect_count
        else:
            effect_duration = 0

        return {
            "max_not_match_time": max_not_match_time,
            "match_success_rate": round(match_success_rate, 2),
            "effect_rate": round(effect_rate, 2),
            "effect_duration": round(effect_duration, 2),
        }

    def get_records(self):
        # 查询非结束的直播间
        neo_rooms = self.get_neo_rooms()
        # 查询关联的直播内容
        neo_contents = self.get_neo_contents(
            [room["bind_content_id"] for room in neo_rooms]
        )
        # 查询关联的授权信息
        neo_auths = self.get_neo_auths(
            [elm["outside_auth_id"] for elm in neo_contents.values()]
        )
        # 查询关联的推流列表
        playlist_rooms = self.get_playlist_room_by_bind_id(
            [room["id"] for room in neo_rooms]
        )

        # 统计正在直播中的直播内容
        running_content_ids = []
        scheduled_content_ids = []
        for neo_room in neo_rooms:
            if neo_room["live_real_status"] == 20 and neo_room["status"] == 0:
                running_content_ids.append(neo_room["bind_content_id"])
            if neo_room["live_real_status"] == 25 and neo_room["status"] == 0:
                scheduled_content_ids.append(neo_room["bind_content_id"])

        result = []
        for neo_room in neo_rooms:
            original_neo_content = neo_contents.get(neo_room["bind_content_id"], {})

            neo_content = deepcopy(original_neo_content)
            neo_auth = neo_auths.get(neo_content["outside_auth_id"], {})
            playlist_room = playlist_rooms.get(neo_room["id"], {})

            # 删除直播间当做结束处理
            if neo_room["status"] != 0:
                neo_room["live_real_status"] = 40

            # 判定弃播原因，如果是正常原因，则修改状态为结束
            if neo_room["live_real_status"] == 80:
                if self.check_adandon_is_normal(neo_room, neo_auth):
                    neo_room["live_real_status"] = 50
                    neo_content["live_status"] = 50

            # 直播间是定时中，直播内容如果确实是直播中，则修改状态
            if (
                neo_room["live_real_status"] == 25
                and neo_content.get("live_status") == 20
                and neo_room["bind_content_id"] in running_content_ids
            ):
                neo_content["live_status"] = 25

            # 直播间是结束，直播内容是定时中，则修改状态
            if (
                neo_room["live_real_status"] == 40
                and neo_content.get("live_status") == 25
                and neo_room["bind_content_id"] in scheduled_content_ids
            ):
                neo_content["live_status"] = 40

            # 直播间是结束，直播内容是已开播，则修改状态
            if (
                neo_room["live_real_status"] == 40
                and neo_content.get("live_status") == 20
                and neo_room["bind_content_id"] in running_content_ids
            ):
                neo_content["live_status"] = 40

            # 直播间是结束，直播内容是已就绪，则修改状态
            if (
                neo_room["live_real_status"] == 40
                and neo_content.get("live_status") == 10
                and neo_room["bind_content_id"] not in running_content_ids
                and neo_room["bind_content_id"] not in scheduled_content_ids
            ):
                neo_content["live_status"] = 40

            is_rt = 0 if neo_content.get("buy_version") == 1 else 1
            playlist_push_log = self.get_playlist_push_log_url(
                is_rt, neo_room["id"], playlist_room
            )
            pop_bag_time = self.get_pop_bag_time(neo_room["id"])
            cookie_expired = self.check_client.is_cookie_expired(
                playlist_room.get("platform"),
                playlist_room.get("shop_short_name"),
            )
            comment_metrics = self.get_comment_metric(neo_room["id"])

            data = {
                "room_id": neo_room["id"],
                "room_status": neo_room["status"],
                "room_live_status": neo_room.get("live_real_status"),
                "room_start_type": neo_room.get("start_type"),
                "room_start_time": neo_room["start_time"],
                "room_end_time": neo_room["end_time"],
                "room_live_id": neo_room["live_id"],
                "content_id": neo_content.get("id"),
                "content_is_rt": is_rt,
                "content_status": neo_content.get("status"),
                "content_live_status": neo_content.get("live_status"),
                "playlist_push_status": playlist_room.get("push_status"),
                "playlist_live_id": playlist_room.get("live_id"),
                "playlist_live_url": playlist_room.get("live_url"),
                "playlist_push_log": playlist_push_log,
                "auth_platform_id": neo_auth.get("platform_id"),
                "auth_shop_name": neo_auth.get("shop_name"),
                "auth_short_name": neo_auth.get("short_name"),
                "pop_bag_time": pop_bag_time,
                "cookie_expired": cookie_expired,
            }
            data.update(comment_metrics)
            result.append(data)

        return result

    def is_normal_close(self, room_id, content_id):
        count, logs = self.es_manager.search(
            "neoailive-api-service",
            body={
                "size": 10,
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
                                                "query": str(room_id),
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": str(content_id),
                                                "lenient": True,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "type": "phrase",
                                                "query": "关播直播返回",
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

        if count:
            return True
        return False

    def check_errors(self, elm, pushing_live_ids):
        # 记录错误
        errors = []
        try:
            # 检查销销直播内容与直播间状态是否一致
            if elm["room_live_status"] != elm["content_live_status"]:
                errors.append("销销直播内容与直播间状态不一致")

            # 检查直播间状态与推流状态是否一致
            if elm["room_live_status"] == 20 and elm["playlist_push_status"] != 2:
                errors.append("直播正常但推流异常")
            if elm["playlist_push_status"] == 2 and elm["room_live_status"] != 20:
                errors.append("推流正常但直播异常")

            # 检查是否存在重复推流
            if (
                len(pushing_live_ids[elm["playlist_live_id"]]) > 1
                and elm["room_id"] in pushing_live_ids[elm["playlist_live_id"]]
            ):
                errors.append("重复推流")

            # 直播中
            if elm["room_live_status"] == 20:
                # 检查cookie
                if elm.pop("cookie_expired"):
                    errors.append("cookie过期")

                # 检查自动下播
                if elm["room_end_time"] and elm["room_end_time"] < datetime.now():
                    errors.append("自动下播失败")

                # 检查互动超时
                if elm["max_not_match_time"]:
                    if datetime.now() > elm["max_not_match_time"] + timedelta(
                        minutes=10
                    ):
                        errors.append("超过10分钟不互动")

                # 检查响应率
                if elm["effect_rate"] < 0.8:
                    errors.append("互动响应率低于80%")

                # 检查平均相应时长
                if elm["effect_duration"] > 15:
                    errors.append("互动响应时长超过15秒")

                # 检查匹配成功率
                if elm["match_success_rate"] < 0.5:
                    errors.append("互动匹配成功率低于50%")

                # 检查弹袋
                if elm["pop_bag_time"] < datetime.now() - timedelta(minutes=60):
                    errors.append("60分钟内没有弹袋")

            # 预约中
            if elm["room_live_status"] == 25:
                # 预约开播未开播
                if elm["room_start_time"] < datetime.now():
                    errors.append("预约开播未开播")

                # 预约时长过短
                if elm["room_end_time"] < elm["room_start_time"] + timedelta(
                    minutes=30
                ):
                    errors.append("预约的直播时长不足30分钟")

            # 结束直播
            if elm["room_live_status"] == 40:
                if not self.is_normal_close(elm["room_id"], elm["content_id"]):
                    errors.append("非正常原因关播")
        except Exception as exc:
            errors.append(str(exc))

        return errors

    def run(self):
        # 最新记录
        records = self.get_records()

        # 正在推流的live_id
        pushing_live_ids = defaultdict(list)
        for elm in records:
            if elm["playlist_push_status"] == 2:
                pushing_live_ids[elm["playlist_live_id"]].append(elm["room_id"])

        # 逐条分析
        for elm in records:
            # 历史记录
            history = crud.neo_live_check.fetch_one(
                fields=["id"], room_id=elm["room_id"]
            )

            # 校验错误
            errors = self.check_errors(elm, pushing_live_ids)

            if errors:
                elm["is_error"] = 1
                elm["error_msg"] = "\n".join(errors)
                elm["status"] = 0
            else:
                elm["is_error"] = 0
                elm["error_msg"] = ""
                if elm["room_live_status"] == 40:
                    elm["status"] = 1
                else:
                    elm["status"] = 0

            # 保存记录
            if history:
                crud.neo_live_check.update_by_id(record_id=history["id"], data=elm)
            else:
                crud.neo_live_check.create(data=elm)

            # 发送告警信息
            self.send_alert_message(elm)

            # 不再监测的直播
            if elm["status"] == 1:
                # 设置neo记录为已校验
                crud.neo_room.update_by_id(
                    record_id=elm["room_id"], data={"has_checked": 1}
                )
                # 清理redis信息
                self.check_client.delete_record_cache(elm["room_id"])
                self.check_client.delete_alert_settings(elm["room_id"])

        logger.info(f"检测直播间 {len(records)} 个")


if __name__ == "__main__":
    while True:
        with loguru.logger.contextualize(traceid="monitor_all_rooms"):
            MonitorAllRooms().run()

        sleep(300)
