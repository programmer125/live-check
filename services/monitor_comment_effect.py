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
from libs.helper import get_text_md5
from libs.log_client import Logger


logger = Logger(__file__)


class MonitorLiveCommentEffect(object):
    def monitor_normal(self):
        with loguru.logger.contextualize(traceid="monitor_normal_qa_effect"):
            conn = redis.StrictRedis.from_url(settings.normal_playlist_redis_uri)
            while True:
                try:
                    record = conn.lpop(
                        "playlist-control-service:all:room_qa_effect_records"
                    )
                    if not record:
                        sleep(1)
                        continue

                    record = json.loads(record)
                    body = record["body"]
                    dependent_data = body.pop("dependent_data")
                    comment_id = get_text_md5(
                        "{}-{}".format(body.get("question"), dependent_data.get("time"))
                    )

                    crud.neo_live_comment.update_by_condition(
                        room_id=int(dependent_data.get("room_id")),
                        comment_id=comment_id,
                        data={"effect_time": datetime.fromtimestamp(record["time"])},
                    )

                    logger.info(
                        "{}-{}\n{}".format(
                            dependent_data.get("room_id"),
                            comment_id,
                            json.dumps(record, ensure_ascii=False),
                        )
                    )
                except Exception as e:
                    logger.error("消费失败：\nexc: {}".format(traceback.format_exc()))
                    raise e

    def monitor_realtime(self):
        with loguru.logger.contextualize(traceid="monitor_realtime_qa_effect"):
            conn = redis.StrictRedis.from_url(settings.realtime_playlist_redis_uri)
            while True:
                try:
                    record = conn.lpop("rt-playlist:all:room_qa_effect_records")
                    if not record:
                        sleep(1)
                        continue

                    record = json.loads(record)
                    body = record["body"]
                    question = (
                        body["origin_question"]
                        if body.get("origin_question")
                        else body["question"]
                    )
                    comment_id = get_text_md5(
                        "{}-{}".format(question, body.get("create_time"))
                    )

                    crud.neo_live_comment.update_by_condition(
                        room_id=record.get("room_id"),
                        comment_id=comment_id,
                        data={"effect_time": datetime.fromtimestamp(record["time"])},
                    )

                    logger.info(
                        "{}-{}\n{}".format(
                            record.get("room_id"),
                            comment_id,
                            json.dumps(record, ensure_ascii=False),
                        )
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
    MonitorLiveCommentEffect().run()
