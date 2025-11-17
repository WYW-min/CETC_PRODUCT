
from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ChainRunModeEnum(str, Enum):
    INVOKE = "同步单次调用模式"
    AINVOKE = "异步单次调用模式"
    BATCH = "同步批量处理模式"
    ABATCH = "异步批量处理模式"