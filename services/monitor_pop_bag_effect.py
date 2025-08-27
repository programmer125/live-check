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


class MonitorLivePopbagEffect(object):
    def monitor_normal(self):
        with loguru.logger.contextualize(traceid="monitor_normal_pop_bag_effect"):
            conn = redis.StrictRedis.from_url(settings.normal_playlist_redis_uri)
            while True:
                try:
                    record = conn.lpop(
                        "playlist-control-service:all:room_pop_bag_effect_records"
                    )
                    if not record:
                        sleep(1)
                        continue

                    body = json.loads(record)
                    crud.neo_live_check.update_by_condition(
                        room_id=body["room_id"],
                        data={"pop_bag_time": datetime.fromtimestamp(body["time"])},
                    )
                except Exception as e:
                    logger.error("消费失败：\nexc: {}".format(traceback.format_exc()))
                    raise e

    def monitor_realtime(self):
        with loguru.logger.contextualize(traceid="monitor_realtime_pop_bag_effect"):
            conn = redis.StrictRedis.from_url(settings.realtime_playlist_redis_uri)
            while True:
                try:
                    record = conn.lpop("rt-playlist:all:room_pop_bag_effect_records")
                    if not record:
                        sleep(1)
                        continue

                    body = json.loads(record)
                    crud.neo_live_check.update_by_condition(
                        room_id=body["room_id"],
                        data={"pop_bag_time": datetime.fromtimestamp(body["time"])},
                    )
                except Exception as e:
                    logger.error("消费失败：\nexc: {}".format(traceback.format_exc()))
                    raise e

    def run(self):
        # 创建守护线程
        thread1 = threading.Thread(target=self.monitor_normal, daemon=True)
        thread2 = threading.Thread(target=self.monitor_realtime, daemon=True)

        # 启动线程
        thread1.start()
        thread2.start()

        # 等待线程结束
        thread1.join()
        thread2.join()


if __name__ == "__main__":
    MonitorLivePopbagEffect().run()
