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
PUSHING_BUT_NOT_RUNNING = ERROR(202, 2, "推流中但未开播", 0)


TOTAL_ERRORS = [
    AUTO_OPEN_FAIL,
    NOT_NORMAL_CLOSE,
    PUSH_REPEAT,
    COOKIE_EXPIRE,
    LONG_TIME_NO_QA,
    QA_EFFECT_RATE_TOO_LOW,
    QA_EFFECT_DURATION_TOO_LONG,
    PUSH_STATUS_INCONSISTENT,
    AUTO_CLOSE_FAIL,
    QA_MATCH_RATE_TOO_LOW,
    LONG_TIME_NO_POP_BAG,
    SCHEDULE_TIME_TOO_SHORT,
    NEO_STATUS_INCONSISTENT,
    PUSHING_BUT_NOT_RUNNING,
]


def get_error_by_code(code):
    code_mappings = {elm.code: elm for elm in TOTAL_ERRORS}
    return code_mappings[code]


def get_highest_priority(errors):
    priority = 99
    for error in errors:
        priority = min(priority, error.priority)

    return priority


def get_send_error_wait_time(codes):
    priority = 99
    for code in codes:
        priority = min(priority, get_error_by_code(code).priority)

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


def get_error_extra_elements():
    options = []
    for error in TOTAL_ERRORS:
        options.append(
            {
                "text": {
                    "tag": "plain_text",
                    "content": error.message,
                },
                "value": str(error.code),
                "icon": {
                    "tag": "standard_icon",
                    "token": "signature_outlined",
                },
            },
        )

    return [
        {
            "tag": "form",
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": "忽略如下告警:",
                        "text_size": "normal_v2",
                        "text_align": "left",
                        "text_color": "default",
                    },
                    "margin": "0px 0px 0px 0px",
                },
                {
                    "tag": "multi_select_static",
                    "placeholder": {"tag": "plain_text", "content": "请选择"},
                    "options": options,
                    "type": "default",
                    "width": "default",
                    "name": "MultiSelect_9ijsl8zhftv",
                    "margin": "0px 0px 0px 0px",
                },
                {
                    "tag": "column_set",
                    "columns": [
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "忽略",
                                    },
                                    "type": "primary",
                                    "width": "default",
                                    "confirm": {
                                        "title": {
                                            "tag": "plain_text",
                                            "content": "确认",
                                        },
                                        "text": {
                                            "tag": "plain_text",
                                            "content": "确定忽略吗？",
                                        },
                                    },
                                    "behaviors": [
                                        {
                                            "type": "callback",
                                            "value": {
                                                "callback_event": "ignore_alert_items"
                                            },
                                        }
                                    ],
                                    "form_action_type": "submit",
                                    "name": "Button_mf4su2tf",
                                }
                            ],
                            "vertical_align": "top",
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "重置",
                                    },
                                    "type": "default",
                                    "width": "default",
                                    "form_action_type": "reset",
                                    "name": "Button_mf4su2tg",
                                }
                            ],
                            "vertical_align": "top",
                        },
                    ],
                },
            ],
            "padding": "4px 0px 4px 0px",
            "margin": "0px 0px 0px 0px",
            "name": "Form_mf4su2te",
        }
    ]
