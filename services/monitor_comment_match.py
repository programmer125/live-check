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
                # 节省空间不存储挂袋列表
                if body.get("dependent_data", {}).get("cart_list"):
                    body["dependent_data"].pop("cart_list")

                if not body.get("dependent_data"):
                    return ConsumeStatus.CONSUME_SUCCESS
                if body.get("intent_type") == "atmosphere":
                    return ConsumeStatus.CONSUME_SUCCESS
                elif body.get("dependent_data", {}).get("reply_type") == 90:
                    return ConsumeStatus.CONSUME_SUCCESS

                dependent_data = body.pop("dependent_data")
                comment_id = get_text_md5(
                    "{}-{}".format(body.get("question"), dependent_data.get("time"))
                )

                is_match = 1 if body.get("is_match") else 2
                crud.neo_live_comment.update_by_condition(
                    room_id=int(dependent_data.get("room_id")),
                    comment_id=comment_id,
                    data={
                        "answer": body,
                        "match_time": datetime.now(),
                        "is_match": is_match,
                        "reason": body.get("reason"),
                        "traceid": body.get("traceid"),
                    },
                )

                logger.info(json.dumps(body, ensure_ascii=False))
            except Exception:
                logger.error(
                    "消费失败：\nexc: {}\nbody: {}".format(
                        traceback.format_exc(), msg.body
                    )
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
