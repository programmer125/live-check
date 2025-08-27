# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/30 10:48
# @File : sync_video_synthesis_result.py
import sys
import json
import threading
import traceback
from time import sleep
from pathlib import Path
from datetime import datetime

import redis
import loguru

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
import crud
from configs.settings import settings
from libs.log_client import Logger


logger = Logger(__file__)


class MonitorPushError(object):
    def monitor_realtime(self):
        with loguru.logger.contextualize(traceid="monitor_push_error"):
            conn = redis.StrictRedis.from_url(settings.realtime_playlist_redis_uri)
            while True:
                try:
                    record = conn.lpop("rt-playlist:all:room_push_error_records")
                    if not record:
                        sleep(1)
                        continue

                    body = json.loads(record)
                    history = crud.neo_live_check.fetch_one(
                        room_id=body["room_id"], fields=["id", "push_error_count"]
                    )
                    if history:
                        crud.neo_live_check.update_by_id(
                            record_id=history["id"],
                            data={"push_error_count": history["push_error_count"] + 1},
                        )
                except Exception as e:
                    logger.error("消费失败：\nexc: {}".format(traceback.format_exc()))
                    raise e

    def run(self):
        self.monitor_realtime()


if __name__ == "__main__":
    MonitorPushError().run()
