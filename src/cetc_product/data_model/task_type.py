from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class TaskTypeEnum(str, Enum):
    TASK1 = "机构信息抽取"
    TASK2 = "人物信息抽取"
    TASK3 = "行为体信息抽取"
    TASK5 = "网络波动事件抽取"
    TASK6 = "军人图片"
    TASK7 = "各国军事政要员人脸图"
    TASK8 = "维基百科的页面快照"
    DOMAIN_ENHANCE = "领域增强任务"
