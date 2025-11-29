from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


TimestampFactory = Callable[[], datetime]


@dataclass
class TimestampProvider:
    """
    提供可注入的时间戳生成器，便于在不同组件间共享时间配置或做单元测试。
    """

    factory: TimestampFactory = field(default=datetime.now)

    def set_factory(self, factory: TimestampFactory) -> None:
        """设置新的时间戳生成函数。"""
        self.factory = factory

    def now(self) -> datetime:
        """返回当前时间。"""
        return self.factory()

    def format(self, fmt: str) -> str:
        """按指定格式返回当前时间字符串。"""
        return self.now().strftime(fmt)


# 默认的全局时间戳提供者，保持与 datetime.now 相同的行为
default_timestamp_provider = TimestampProvider()
