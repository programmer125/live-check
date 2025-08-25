# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/30 10:48
# @File : sync_video_synthesis_result.py
import sys
import json
import traceback
from time import sleep
from pathlib import Path
from datetime import datetime

import loguru
from rocketmq.client import Message, ConsumeStatus

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
import crud
from configs.settings import settings
from libs.helper import get_text_md5
from libs.sync_rocketmq import RocketMQConsumer
from libs.log_client import Logger


logger = Logger(__file__)


class MonitorLiveCommentCrawl(object):
    def __init__(self):
        self.rocketmq = {
            "group_name": settings.rocketmq_live_room_comments_live_check_consumer,
            "name_server": settings.rocketmq_name_server,
            "access_key": settings.rocketmq_access_key,
            "access_secret": settings.rocketmq_access_secret,
        }
        self.topic = settings.rocketmq_live_room_comments_topic
        self.minor_step = "monitor_comment_crawl"

    def process(self, msg: Message):
        with loguru.logger.contextualize(traceid=self.minor_step):
            try:
                body = json.loads(msg.body)
                # 节省空间不存储挂袋列表
                if body.get("user_data", {}).get("cart_list"):
                    body["user_data"].pop("cart_list")

                if not body.get("user_data") or not body.get("question"):
                    return ConsumeStatus.CONSUME_SUCCESS

                user_data = body.get("user_data")
                if (
                    user_data.get("platform_id")
                    and int(user_data.get("platform_id")) == 1
                    and user_data.get("reply_type") == 9
                ):
                    return ConsumeStatus.CONSUME_SUCCESS

                comment_id = get_text_md5(
                    "{}-{}".format(body.get("question"), user_data.get("time"))
                )

                crud.neo_live_comment.create(
                    data={
                        "room_id": int(user_data.get("room_id")),
                        "comment_id": comment_id,
                        "question": body,
                        "crawl_time": datetime.fromtimestamp(user_data.get("time")),
                    }
                )

                logger.info(json.dumps(body, ensure_ascii=False))
            except Exception:
                logger.error(
                    "消费失败：\nexc: {}\nbody: {}".format(traceback.format_exc(), msg.body)
                )

            return ConsumeStatus.CONSUME_SUCCESS

    def consume(self):
        with RocketMQConsumer(**self.rocketmq) as consumer:
            consumer.subscribe(self.topic, self.process)
            sleep(600)


if __name__ == "__main__":
    while True:
        instance = MonitorLiveCommentCrawl()
        instance.consume()
