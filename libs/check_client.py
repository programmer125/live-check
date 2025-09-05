import json
from datetime import datetime

import redis

from configs.settings import settings


class CheckClient(object):

    def __init__(self):
        self.redis_client = redis.StrictRedis.from_url(settings.redis_uri)
        self.cookie_client = redis.StrictRedis.from_url(settings.cookie_redis_uri)

    def get_comment_crawl_time(self):
        comment_crawl_time = self.redis_client.get(
            "live-check:reset_comment_crawl_time"
        )
        if comment_crawl_time:
            return datetime.fromtimestamp(float(comment_crawl_time.decode())).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            return "2025-08-20 00:00:00"

    def get_record_cache(self, room_id):
        info = self.redis_client.hget("live-check:record_info", str(room_id))
        if info:
            return json.loads(info)
        else:
            return {}

    def set_record_cache(self, room_id, info):
        self.redis_client.hset("live-check:record_info", str(room_id), json.dumps(info))

    def delete_record_cache(self, room_id):
        self.redis_client.hdel("live-check:record_info", str(room_id))

    def get_alert_settings(self, room_id):
        info = self.redis_client.hget("live-check:alert_settings", str(room_id))
        if info:
            return json.loads(info)
        else:
            return {}

    def set_alert_settings(self, room_id, info):
        self.redis_client.hset(
            "live-check:alert_settings", str(room_id), json.dumps(info)
        )

    def delete_alert_settings(self, room_id):
        self.redis_client.hdel("live-check:alert_settings", str(room_id))

    def is_cookie_expired(self, platform, short_name):
        if platform not in {"TB", "PDD"}:
            return False

        results = self.cookie_client.hgetall(f"{platform}:{short_name}")
        if results:
            return False

        return True

    def get_room_id_by_msg_id(self, msg_id):
        room_id = self.redis_client.get("live-check:room_id:{}".format(msg_id))
        if room_id:
            return int(room_id.decode())
        else:
            return None

    def set_room_id_by_msg_id(self, msg_id, room_id):
        # 48小时自动删除
        self.redis_client.setex(
            "live-check:room_id:{}".format(msg_id), 60 * 60 * 24 * 2, str(room_id)
        )
