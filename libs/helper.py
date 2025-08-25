# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2025/2/13 09:34
# @File : helper.py
import hashlib


def get_text_md5(content):
    m = hashlib.md5()
    m.update(content.encode())
    return m.hexdigest()
