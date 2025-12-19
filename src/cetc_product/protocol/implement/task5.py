from typing import (
    Dict,
    Any,
    override,
)

from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.protocol.base import BaseLangChainTask
from cetc_product.tools.func_tools import Funcs


class Task5(BaseLangChainTask):
    """领域增强任务类"""

    def __init__(self, chain: object):
        super().__init__(chain, task_name=TaskTypeEnum.TASK5)
        self.format_str = (
            "<site>{site_name}</site><title>{title}</title><content>{content}</content>"
        )
        self.keys = "site_name title content".split()

    @override
    def get_input(self, data: Dict[str, Any]) -> None | Any:
        """子类必须实现：准备Chain输入"""
        return {
            "text": self.format_str.format(**{k: data.get(k, "") for k in self.keys})
        }

    @override
    def get_output(self, input_data: Any, result: Any) -> Any:
        """子类必须实现：处理Chain输出"""
        return {"id": Funcs.getid_for_smart_starlight(input_data), "out": result}
