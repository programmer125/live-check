# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/30 10:48
# @File : sync_video_synthesis_result.py
import sys
import json
import traceback
from time import sleep
from pathlib import Path

import loguru
from rocketmq.client import Message, ConsumeStatus

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from configs.settings import settings
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

                if body.get("question"):
                    logger.info(json.dumps(body, ensure_ascii=False))

                return ConsumeStatus.CONSUME_SUCCESS
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
