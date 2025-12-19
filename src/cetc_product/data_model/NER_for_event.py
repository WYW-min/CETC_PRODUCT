from __future__ import annotations
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Language(str, Enum):
    """文本语种：用于满足“中文简体、英文、中文繁体”的场景要求。"""

    zh_cn = "中文简体"
    zh_tw = "中文繁体"
    en = "英文"
    other = "其他"


class DataSourceType(str, Enum):
    """数据来源类型：用于满足“网络探测数据、新闻数据、报告数据”等来源要求。"""

    network_probe = "网络探测数据"
    news = "新闻数据"
    report = "报告数据"
    other = "其他"


class Meta(BaseModel):
    """
    样本元信息：用于记录数据来源、语种、时间等信息，
    方便在数据集层面验证“数据来源要求、语种覆盖、近 6 个月”等约束。
    """

    data_source: DataSourceType = Field(
        ...,
        alias="数据来源要求",
        description=(
            "本条样本的数据来源类型：" "网络探测数据 / 新闻数据 / 报告数据 / 其他。"
        ),
    )
    language: Language = Field(
        ...,
        alias="语种",
        description=("文本语种：中文简体 / 英文 / 中文繁体（可选“其他”）。"),
    )
    download_time: Optional[str] = Field(
        None,
        alias="采集时间",
        description=(
            "采集时间，字符串（建议 ISO 8601，例如 2025-11-01T10:00:00Z），"
            "用于判断是否属于近 6 个月采集的数据。"
        ),
    )
    source_url: Optional[str] = Field(
        None,
        alias="来源链接",
        description="原始网页或报告的 URL，用于溯源（可选）。",
    )
    source_title: Optional[str] = Field(
        None,
        alias="来源标题",
        description="原始新闻或报告标题（如有），辅助理解事件摘要。",
    )
    source_id: Optional[str] = Field(
        None,
        alias="来源标识",
        description="内部使用的源数据唯一标识（如爬虫 ID、文件名等，可选）。",
    )


# ========== 二、网络波动事件要素 ==========


class NetFluctuationEvent(BaseModel):
    """
    单个网络波动事件的要素信息。
    关键字段名称与需求中的用词保持一致：
    - 时间区间
    - 影响地点
    - 事件摘要
    - 事件影响设备数量
    - 事件原因
    """

    time_range: Optional[str] = Field(
        None,
        alias="时间区间",
        description=(
            "网络波动事件的时间范围或发生时间描述，"
            "例如：'2025-11-01 10:00~12:30'、'2025年11月上旬'、'北京时间昨晚'。"
        ),
    )
    affected_locations: List[str] = Field(
        default_factory=list,
        alias="影响地点",
        description=(
            "事件影响到的地点列表，如国家、省份、城市、地区、跨境链路、运营商网络范围等，"
            "例如：['中国台湾地区', '美国西海岸', '某云服务可用区']。"
        ),
    )
    summary: Optional[str] = Field(
        None,
        alias="事件摘要",
        description=(
            "对网络波动事件的简要概述，通常 1-3 句，概括发生了什么、影响了什么。"
        ),
    )
    affected_device_count: Optional[int] = Field(
        None,
        alias="事件影响设备数量",
        description=(
            "受影响设备的数量（估计值），例如 12000。"
            "若原文只给出模糊描述（如“大量用户”“部分路由器”），"
            "可以留空或约定用 -1，并在事件摘要或事件原因中补充说明。"
        ),
    )
    cause: Optional[str] = Field(
        None,
        alias="事件原因",
        description=(
            "网络波动事件的原因或诱因，如：光缆被挖断、机房断电、DDoS 攻击、"
            "软件升级失败、配置错误、自然灾害等。"
        ),
    )

    # 为了让要素种类 > 5，再补充一些实用字段（名字可读但不和需求冲突）
    impact_level: Optional[str] = Field(
        None,
        alias="事件影响等级",
        description=(
            "事件影响的严重程度，如：'轻微'、'一般'、'严重'、'特别严重'，"
            "或英文等级（minor / major / critical）。"
        ),
    )
    impacted_services: List[str] = Field(
        default_factory=list,
        alias="受影响业务类型",
        description=(
            "受影响的业务/服务类型，如：'网页访问'、'视频流媒体'、'在线游戏'、'VPN 服务' 等。"
        ),
    )


# ========== 三、顶层样本结构 ==========


class NetFluctuationSample(BaseModel):
    """
    单条输入文本（新闻/报告/探测数据对应的说明）的标注结果：
    - 网络波动事件列表：从文本中抽取出的一个或多个网络波动事件
    """

    events: List[NetFluctuationEvent] | None = Field(
        None,
        alias="网络波动事件列表",
        description=(
            "从当前文本中抽取出的所有网络波动事件列表。"
            "如果文本中未包含任何网络波动事件，则强制为None"
        ),
    )

    why: str = Field(..., description="抽取原因")
