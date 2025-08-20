# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/8/20 11:35
# @File : monitor_all_rooms.py
import crud
from db.session import PlaylistSessionLocal, NeoailiveSessionLocal
from libs.sync_mysql_client import MysqlClient


class MonitorAllRooms(object):
    def __init__(self):
        self.playlist_session = PlaylistSessionLocal()
        self.playlist_client = MysqlClient(self.playlist_session)

        self.neoailive_session = NeoailiveSessionLocal()
        self.neoailive_client = MysqlClient(self.neoailive_session)

    # 查找销销所有未关闭的直播，与推流未结束的直播间，取并集
    def get_neo_rooms(self):
        stander_rooms = self.playlist_client.fetch_all(
            "SELECT bind_id FROM playlist_control.room where status not in (3, 4)"
        )
        realtime_rooms = self.playlist_client.fetch_all(
            "SELECT bind_id FROM playlist_control.rt_room where status not in (4, 5, 10)"
        )
        pushing_bind_ids = []
        for room in stander_rooms + realtime_rooms:
            pushing_bind_ids.append(room["bind_id"])

        neo_rooms = self.neoailive_client.fetch_all(
            "SELECT * FROM neoailive_db.n_room where live_real_status not in (40, 80) and `status` = 0"
        )
        result = [dict(elm) for elm in neo_rooms]

        extra_bind_ids = list(
            set(pushing_bind_ids) - set([elm["id"] for elm in result])
        )
        if extra_bind_ids:
            bind_ids = ",".join([str(elm) for elm in extra_bind_ids])
            neo_rooms = self.neoailive_client.fetch_all(
                f"SELECT * FROM neoailive_db.n_room where id in ({bind_ids})"
            )
            for elm in neo_rooms:
                result.append(dict(elm))

        return result

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
            room["is_rt"] = 0
            room["push_status"] = self.convert_stander_status(room["status"])
            result[room["bind_id"]] = room

        for room in realtime_rooms:
            room = dict(room)
            room["is_rt"] = 1
            room["push_status"] = self.convert_realtime_status(room["status"])
            result[room["bind_id"]] = room

        return result

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
        for neo_room in neo_rooms:
            if neo_room["live_real_status"] == 20:
                running_content_ids.append(neo_room["bind_content_id"])

        result = []
        for neo_room in neo_rooms:
            neo_content = neo_contents.get(neo_room["bind_content_id"], {})
            neo_auth = neo_auths.get(neo_content["outside_auth_id"], {})
            playlist_room = playlist_rooms.get(neo_room["id"], {})

            # 直播间是定时中，直播内容如果确实是直播中，则修改状态
            if (
                neo_room["live_real_status"] == 25
                and neo_content.get("live_status") == 20
                and neo_room["bind_content_id"] in running_content_ids
            ):
                neo_content["live_status"] = 25

            result.append(
                {
                    "room_id": neo_room["id"],
                    "room_status": neo_room["status"],
                    "room_live_status": neo_room.get("live_real_status"),
                    "room_start_time": neo_room["start_time"],
                    "room_end_time": neo_room["end_time"],
                    "room_live_id": neo_room["live_id"],
                    "content_id": neo_content.get("id"),
                    "content_status": neo_content.get("status"),
                    "content_live_status": neo_content.get("live_status"),
                    "playlist_push_status": playlist_room.get("push_status"),
                    "playlist_live_id": playlist_room.get("live_id"),
                    "playlist_live_url": playlist_room.get("live_url"),
                    "auth_shop_name": neo_auth.get("shop_name"),
                    "auth_short_name": neo_auth.get("short_name"),
                }
            )

        return result

    def run(self):
        records = self.get_records()
        for elm in records:
            print(elm)
            crud.neo_live_check.create(data=elm)


if __name__ == "__main__":
    MonitorAllRooms().run()
