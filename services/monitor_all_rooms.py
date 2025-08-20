# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/8/20 11:35
# @File : monitor_all_rooms.py
from db.session import PlaylistSessionLocal, NeoailiveSessionLocal
from libs.sync_mysql_client import MysqlClient


class MonitorAllRooms(object):
    def __init__(self):
        self.start_time = "2025-08-20 11:35:00"

        self.playlist_session = PlaylistSessionLocal()
        self.playlist_client = MysqlClient(self.playlist_session)

        self.neoailive_session = NeoailiveSessionLocal()
        self.neoailive_client = MysqlClient(self.neoailive_session)

    # 查找销销所有未关闭的直播
    def get_neo_rooms(self):
        neo_rooms = self.neoailive_client.fetch_all(
            "SELECT * FROM neoailive_db.n_room where live_real_status not in (40, 80) and `status` = 0"
        )
        return [dict(elm) for elm in neo_rooms]

    def get_neo_contents(self, content_ids):
        content_ids = ",".join([str(elm) for elm in content_ids])
        contents = self.neoailive_client.fetch_all(
            f"SELECT * FROM neoailive_db.n_room_content where id in ({content_ids})"
        )
        return {elm["id"]: dict(elm) for elm in contents}

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

    def check_running(self):
        neo_rooms = self.get_neo_rooms()
        neo_contents = self.get_neo_contents(
            [room["bind_content_id"] for room in neo_rooms]
        )
        playlist_rooms = self.get_playlist_room_by_bind_id(
            [room["id"] for room in neo_rooms]
        )
        for neo_room in neo_rooms:
            neo_content = neo_contents.get(neo_room["bind_content_id"], {})
            playlist_room = playlist_rooms.get(neo_room["id"], {})

            print(
                neo_room["id"],
                neo_room.get("live_real_status"),
                neo_content.get("status"),
                neo_content.get("live_status"),
                playlist_room.get("status"),
            )

    def run(self):
        self.check_running()


if __name__ == "__main__":
    MonitorAllRooms().run()
