# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/23 10:25
# @File : rocketmq.py
from typing import Optional, Callable, Any
from rocketmq.client import Producer, PushConsumer, Message, ConsumeStatus


class RocketMQProducer:
    def __init__(
        self, group_name: str, name_server: str, access_key: str, access_secret: str
    ):
        self.group_name = group_name
        self.name_server = name_server
        self.access_key = access_key
        self.access_secret = access_secret
        self.producer = None

    def __enter__(self):
        self.producer = Producer(self.group_name)
        self.producer.set_name_server_address(self.name_server)
        self.producer.set_session_credentials(self.access_key, self.access_secret, "")
        self.producer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.producer:
            self.producer.shutdown()

    def send(
        self,
        topic: str,
        message: str,
        keys: Optional[str] = None,
        tags: Optional[str] = None,
        delay_level: Optional[int] = None,
    ) -> bool:
        """
        发送消息
        :param topic: 主题
        :param message: 消息内容
        :param keys: key
        :param tags: tag
        :param delay_level: 延时级别(1-18):
            1=1s, 2=5s, 3=10s, 4=30s, 5=1m, 6=2m, 7=3m, 8=4m, 9=5m, 10=6m,
            11=7m, 12=8m, 13=9m, 14=10m, 15=20m, 16=30m, 17=1h, 18=2h
        :return: 是否发送成功
        """
        msg = Message(topic)
        msg.set_body(message)
        if keys:
            msg.set_keys(keys)
        if tags:
            msg.set_tags(tags)
        if delay_level:
            msg.set_delay_time_level(delay_level)

        return self.producer.send_sync(msg)


class RocketMQConsumer:
    def __init__(
        self, group_name: str, name_server: str, access_key: str, access_secret: str
    ):
        self.group_name = group_name
        self.name_server = name_server
        self.access_key = access_key
        self.access_secret = access_secret
        self.consumer = None

    def __enter__(self):
        self.consumer = PushConsumer(self.group_name)
        self.consumer.set_name_server_address(self.name_server)
        self.consumer.set_session_credentials(self.access_key, self.access_secret, "")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.consumer:
            self.consumer.shutdown()

    def subscribe(self, topic: str, callback: Callable[[Message], Any]):
        """
        订阅主题
        :param topic: 主题
        :param callback: 回调函数，处理接收到的消息
        """
        self.consumer.subscribe(topic, callback)
        self.consumer.start()


# 使用示例
if __name__ == "__main__":
    NAME_SERVER = "rmq-a8e3z45x.rocketmq.gz.qcloud.tencenttdmq.com:8080"
    ACCESS_KEY = "aka8e3z45x543a9ad07f68"
    ACCESS_SECRET = "sk66b103437cf93a2c"
    TOPIC = "live_qa_results_dev"

    def produce():
        # 生产者示例
        with RocketMQProducer(
            "qa_dev", NAME_SERVER, ACCESS_KEY, ACCESS_SECRET
        ) as producer:
            # 发送普通消息
            producer.send(TOPIC, "Hello, RocketMQ!")

            # 发送延时消息（5秒后投递）
            producer.send(TOPIC, "This is a delayed message", delay_level=2)

            # 发送延时消息（1分钟后投递）
            producer.send(
                TOPIC, "This message will be delivered after 1 minute", delay_level=5
            )

    def consume():
        # 消费者示例
        def process_message(msg: Message):
            try:
                print(
                    f"Received message.\n\tmessageId: {msg.id}\n\tbody: {msg.body}\n\ttags: {msg.tags}\n\tkeys: {msg.keys}"
                )

                return ConsumeStatus.CONSUME_SUCCESS
            except Exception:
                # return ConsumeStatus.RECONSUME_LATER
                return ConsumeStatus.CONSUME_SUCCESS

        with RocketMQConsumer(
            "playlist_control_dev", NAME_SERVER, ACCESS_KEY, ACCESS_SECRET
        ) as consumer:
            consumer.subscribe(TOPIC, process_message)

            # 保持运行以接收消息
            import time

            time.sleep(3600)  # 运行60秒后退出

    produce()
    consume()
