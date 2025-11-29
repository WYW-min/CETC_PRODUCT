from abc import ABC, abstractmethod
import asyncio
from typing import (
    Callable,
    Dict,
    List,
    Any,
)

from cetc_product.data_model.run_mode import ChainRunModeEnum
from cetc_product.data_model.task_type import TaskTypeEnum


# 默认过滤函数(模块级)
def _default_validator(data: Any) -> bool:
    """默认验证函数 - 检查数据是否为真值"""
    return bool(data)


# 基础抽象类（提供通用逻辑）
class BaseLangChainTask(ABC):
    """LangChain 任务基类"""

    def __init__(self, chain: object, task_name: TaskTypeEnum):

        assert isinstance(
            task_name, TaskTypeEnum
        ), f"task_name必须为类型TaskTypeEnum，当前输入类型：{type(task_name)}"
        self._chain = chain
        self._task_type = task_name

    @property
    def chain(self) -> Any:
        return self._chain

    @property
    def task_type(self) -> TaskTypeEnum:
        return self._task_type

    def get_serializable_validator(self) -> Callable[[Dict[str, Any]], bool]:
        """
        返回一个可序列化的验证函数

        默认实现返回 bool 检查函数
        子类应该重写此方法提供具体的验证逻辑

        Returns:
            验证函数
        """
        return _default_validator

    @abstractmethod
    def get_input(self, data: Any) -> None | Any:
        """子类必须实现：准备输入"""
        pass

    def run(
        self,
        input_data: Dict | List[Dict],
        run_mode: ChainRunModeEnum = ChainRunModeEnum.INVOKE,
    ) -> Any | List[Any]:
        """默认实现：调用 chain.invoke"""
        # 进行筛选

        if not isinstance(input_data, list):
            input_data = [input_data]

        chain_inputs = [self.get_input(data) for data in input_data]

        if run_mode == ChainRunModeEnum.INVOKE:
            chain_outputs = self.chain.batch(chain_inputs)
        elif run_mode == ChainRunModeEnum.ABATCH:
            chain_outputs = asyncio.run(self.chain.abatch(chain_inputs))

        else:
            raise NotImplementedError(f"未实现的调用模式: {run_mode}")

        return [
            self.get_output(in_data, out_data)
            for in_data, out_data in zip(input_data, chain_outputs)
        ]

    @abstractmethod
    def get_output(self, input_data: Any, result: Any) -> Any:
        """子类必须实现：处理输出"""
        pass
