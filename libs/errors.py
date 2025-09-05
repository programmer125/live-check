from typing import List
from collections import namedtuple


ERROR = namedtuple("ERROR", ["code", "priority", "message", "threshold"])

AUTO_OPEN_FAIL = ERROR(101, 1, "预约开播失败", 5 * 60)
NOT_NORMAL_CLOSE = ERROR(102, 1, "非正常原因关播", 0)
PUSH_REPEAT = ERROR(103, 1, "同一个直播间多路推流", 0)
COOKIE_EXPIRE = ERROR(104, 1, "cookie已过期", 0)
LONG_TIME_NO_QA = ERROR(105, 1, "长时间不互动", 10 * 60)
QA_EFFECT_RATE_TOO_LOW = ERROR(106, 1, "互动响应率过低", 0.8)
QA_EFFECT_DURATION_TOO_LONG = ERROR(107, 1, "互动平均响应时长过高", 15)
PUSH_STATUS_INCONSISTENT = ERROR(108, 1, "直播间与推流状态不一致", 0)
AUTO_CLOSE_FAIL = ERROR(109, 1, "预约下播失败", 5 * 60)
QA_MATCH_RATE_TOO_LOW = ERROR(110, 1, "互动匹配率过低", 0.5)
LONG_TIME_NO_POP_BAG = ERROR(111, 1, "长时间不弹袋", 60 * 60)
SCHEDULE_TIME_TOO_SHORT = ERROR(112, 1, "预约直播时长过短", 30 * 60)
NEO_STATUS_INCONSISTENT = ERROR(201, 2, "直播内容与直播间状态不一致", 0)


def get_error_by_code(code):
    code_mappings = {
        101: AUTO_OPEN_FAIL,
        102: NOT_NORMAL_CLOSE,
        103: PUSH_REPEAT,
        104: COOKIE_EXPIRE,
        105: LONG_TIME_NO_QA,
        106: QA_EFFECT_RATE_TOO_LOW,
        107: QA_EFFECT_DURATION_TOO_LONG,
        108: PUSH_STATUS_INCONSISTENT,
        109: AUTO_CLOSE_FAIL,
        110: QA_MATCH_RATE_TOO_LOW,
        111: LONG_TIME_NO_POP_BAG,
        112: SCHEDULE_TIME_TOO_SHORT,
        201: NEO_STATUS_INCONSISTENT,
    }
    return code_mappings[code]


def get_send_error_wait_time(codes):
    priority = 99
    for code in codes:
        priority = min(priority, get_error_by_code(code).priority, priority)

    if priority <= 1:
        return 0
    else:
        return 40 * 60


def get_error_codes(errors: List[ERROR]):
    codes = []
    for error in errors:
        codes.append(error.code)

    return codes


def get_error_msg(errors: List[ERROR]):
    msgs = []
    for error in errors:
        msgs.append(error.message)

    return "\n".join(msgs)
