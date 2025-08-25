# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/27 15:26
# @File : settings.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 基础配置
    api_host: str = ""
    api_port: str = ""
    reload: bool = False

    # 服务名称
    service_name: str = "live-check-service"

    # 环境
    env: str = os.environ.get("LIVE_CHECK_ENV", "local")

    # mysql 地址
    playlist_db_uri: str = ""
    neoailive_db_uri: str = ""
    db_echo: bool = False

    # 日志接收地址
    log_redis_uri: str = ""
    log_redis_key: str = ""

    # rocketmq配置
    rocketmq_name_server: str = ""
    rocketmq_access_key: str = ""
    rocketmq_access_secret: str = ""
    rocketmq_live_room_comments_topic: str = ""
    rocketmq_live_room_comments_live_check_consumer: str = ""
    rocketmq_ai_qa_results_topic: str = ""
    rocketmq_ai_qa_results_live_check_consumer: str = ""

    normal_playlist_redis_uri: str = ""
    realtime_playlist_redis_uri: str = ""

    # es配置
    es_host: str = ""
    es_user: str = ""
    es_password: str = ""

    # 停止推流任务api
    stop_push_task_api: str = ""

    # 实时版推流日志路径
    log_path: str = "/root/rt-playlist-control/logs"

    # 从配置文件中重写settings参数
    project_root: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )
    model_config = SettingsConfigDict(
        env_file=os.path.join(project_root, f"configs/.env_{env}"),
        env_file_encoding="utf-8",
        extra="allow",  # 添加这一行以允许额外的输入字段
    )


settings = Settings()
