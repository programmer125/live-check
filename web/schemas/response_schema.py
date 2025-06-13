# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/28 14:10
# @File : response_schema.py
from typing import Generic, TypeVar, Optional

from fastapi import status
from pydantic import BaseModel

# 泛型定义
T = TypeVar("T")


# 统一响应模型
class ResponseModel(BaseModel, Generic[T]):
    code: int = status.HTTP_200_OK
    message: str = "success"
    data: Optional[T] = None
