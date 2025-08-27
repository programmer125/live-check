# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/6/13 14:27
# @File : check.py
import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from configs.settings import settings
from libs.sync_es_client import ESClient
from libs.sync_mysql_client import MysqlClient


class Check(object):
    def __init__(self):
        self.es_manager = ESClient(
            host=settings.es_host, user=settings.es_user, password=settings.es_password
        )
        self.neo_db = MysqlClient(settings.neoailive_db_uri)
        self.playlist_db = MysqlClient(settings.playlist_db_uri)

        self.log_file = settings.log_path + "/start_room_{}.log"

    def check_tts(self):
        total_count = 0

        messages = defaultdict(list)
        api_count = defaultdict(int)
        error_api_count = defaultdict(int)
        word_count = defaultdict(int)
        error_word_count = defaultdict(int)

        for start_time, end_time in [
            ("2025-08-18T00:00:00.000Z", "2025-08-18T09:00:00.000Z"),
            ("2025-08-17T00:00:00.000Z", "2025-08-18T00:00:00.000Z"),
            ("2025-08-16T08:00:00.000Z", "2025-08-17T00:00:00.000Z"),
            ("2025-08-16T00:00:00.000Z", "2025-08-16T00:00:00.000Z"),
        ]:
            page_num = 1
            page_size = 500
            while True:
                _, logs = self.es_manager.search(
                    "qiyin-tts-service",
                    body={
                        "from": (page_num - 1) * page_size,
                        "size": page_size,
                        "sort": [
                            {
                                "@timestamp": {
                                    "order": "desc",
                                    "unmapped_type": "boolean",
                                }
                            }
                        ],
                        "version": True,
                        "fields": [
                            {"field": "*", "include_unmapped": "true"},
                            {
                                "field": "@timestamp",
                                "format": "strict_date_optional_time",
                            },
                        ],
                        "stored_fields": ["*"],
                        "_source": ["message", "@timestamp"],
                        "query": {
                            "bool": {
                                "must": [],
                                "filter": [
                                    {
                                        "range": {
                                            "@timestamp": {
                                                "gte": start_time,
                                                "lt": end_time,
                                                "format": "strict_date_optional_time",
                                            }
                                        }
                                    }
                                ],
                                "should": [],
                                "must_not": [],
                            }
                        },
                    },
                )

                if logs:
                    for log in logs:
                        total_count += 1

                        try:
                            message = json.loads(log["message"])

                            point = datetime.strptime(
                                log["@timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
                            ) + timedelta(hours=8)
                            hour_key = "{}{}".format(
                                point.day, str(point.hour).zfill(2)
                            )
                            # messages[hour_key].append(log["message"])

                            api_count[hour_key] += 1

                            request = message.get("request")
                            if isinstance(request, str):
                                error_api_count[hour_key] += 1
                                continue

                            text = request.get("text")
                            response = message.get("response")

                            if response.get("status") == 200:
                                if "cut_points" in response:
                                    flag = True
                                    for elm in response["cut_points"]:
                                        words = elm.get("words")
                                        if not (
                                            words
                                            and isinstance(words, list)
                                            and len(words) > 0
                                        ):
                                            flag = False
                                            break
                                else:
                                    words = response.get("words")
                                    if not (
                                        words
                                        and isinstance(words, list)
                                        and len(words) > 0
                                    ):
                                        flag = False
                                    else:
                                        flag = True
                            else:
                                flag = False

                            word_count[hour_key] += len(text)
                            if not flag:
                                error_word_count[hour_key] += len(text)
                                messages[hour_key].append(log["message"])
                        except Exception as exc:
                            print("解析失败：{} {}".format(exc, log))

                    page_num += 1

                    print(total_count)
                else:
                    break

        print(total_count)

        for day in [18, 17, 16]:
            for hour in range(23, -1, -1):
                key = "{}{}".format(day, str(hour).zfill(2))
                print(
                    "\t".join(
                        [
                            key,
                            str(word_count[key]),
                            str(error_word_count[key]),
                            str(word_count[key] - error_word_count[key]),
                        ]
                    )
                )

                if messages[key]:
                    with open(
                        "/root/live-check/scripts/logs/{}.log".format(key), "a"
                    ) as f:
                        for message in messages[key]:
                            f.write(message + "\n")

    def check(self):
        self.check_tts()


if __name__ == "__main__":
    Check().check()
