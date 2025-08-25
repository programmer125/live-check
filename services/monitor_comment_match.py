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


class MonitorLiveCommentMatch(object):
    def __init__(self):
        self.rocketmq = {
            "group_name": settings.rocketmq_ai_qa_results_live_check_consumer,
            "name_server": settings.rocketmq_name_server,
            "access_key": settings.rocketmq_access_key,
            "access_secret": settings.rocketmq_access_secret,
        }
        self.topic = settings.rocketmq_ai_qa_results_topic
        self.minor_step = "monitor_comment_match"

    def process(self, msg: Message):
        with loguru.logger.contextualize(traceid=self.minor_step):
            try:
                body = json.loads(msg.body)
                if body.get("intent_type") == "atmosphere":
                    pass
                elif body.get("dependent_data", {}).get("reply_type") == 90:
                    pass
                else:
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
        instance = MonitorLiveCommentMatch()
        instance.consume()
