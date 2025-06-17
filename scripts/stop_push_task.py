# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/16 17:13
# @File : stop_push_task.py
import sys
from pathlib import Path
from datetime import datetime, timedelta

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from configs.settings import settings
from libs.sync_es_client import ESClient
from libs.sync_mysql_client import MysqlClient


class StopPushTask(object):
    def __init__(self):
        self.es_manager = ESClient(
            host=settings.es_host, user=settings.es_user, password=settings.es_password
        )
        self.neo_db = MysqlClient(settings.neoailive_db_uri)
        self.playlist_db = MysqlClient(settings.playlist_db_uri)

    def stop_push(self, room_id):
        response = requests.get("{}{}".format(settings.stop_push_task_api, room_id))
        print(response.text)

    def run(self):
        push_tasks = self.playlist_db.fetch_all(
            "select id, bind_id, real_start_time from playlist_control.room where status = 2"
        )
        for push_task in push_tasks:
            if datetime.now() - timedelta(days=15) > push_task["real_start_time"]:
                self.stop_push(push_task["bind_id"])
                print("直播过期")
            else:
                room_status = self.neo_db.fetch_one(
                    "SELECT live_real_status FROM neoailive_db.n_room where id = {}".format(
                        push_task["bind_id"]
                    )
                )
                if room_status["live_real_status"] in [40, 80]:
                    self.stop_push(push_task["bind_id"])
                    print("销销关播")


if __name__ == "__main__":
    StopPushTask().run()
