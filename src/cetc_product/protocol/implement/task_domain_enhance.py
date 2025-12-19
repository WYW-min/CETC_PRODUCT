from pathlib import Path
from typing import (
    Callable,
    Dict,
    Any,
    Set,
    override,
)
import yaml

from cetc_product.data_model.entity import (
    DomainEnum,
    EnhanceDomainEnum,
    EntityType,
    PersonSubtype,
    RegionEnum,
)
from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.protocol.base import BaseLangChainTask
from cetc_product.tools.IO_tool import load_mapping
from cetc_product.tools.tiny_tool import check_path, safe_get
from cetc_product.tools.func_tools import Funcs


# 模块级函数 - 天然可序列化
def _validate_task_data(
    data: Dict[str, Any],
    enhance_domain_map:Dict[str, EnhanceDomainEnum] | None,
) -> bool:
    """
    Task2 验证函数

    Args:
        data: 输入数据
        enhance_domain_map: 领域增强映射

    Returns:
        是否通过验证
    """
    
    if enhance_domain_map is None:
        return True
    
    raw_domains = safe_get(data, ["entity_description", "domains"])
    if raw_domains and ( set(raw_domains) <= set(enhance_domain_map.keys()) ):
        return False
    return True


class TaskDomainEnhance(BaseLangChainTask):
    """领域增强任务类"""

    def __init__(self, chain: object):
        super().__init__(chain, task_name=TaskTypeEnum.DOMAIN_ENHANCE)
        
         
    @override
    def init_extra_params(self, params: Dict[str, Any]) -> None:
        # 加载独有参数
        domain_enhance_map_path = params.get("domain_enhance_map_path")
        if domain_enhance_map_path and Path(domain_enhance_map_path).is_file():
            self.domain_map = load_mapping(Path(domain_enhance_map_path))
        else:
            self.domain_map = None
    
    @override
    def get_serializable_validator(self) -> Callable[[Dict[str, Any]], bool]:
        """
        返回一个可序列化的验证函数

        Returns:
            验证函数(使用 functools.partial)
        """
        from functools import partial
        return partial(
            _validate_task_data,
            enhance_domain_map=self.domain_map,
        )

    @override
    def get_input(self, data: Dict[str, Any]) -> None | Any:
        """子类必须实现：准备Chain输入"""
        
        
        return {
            "object" : data["title"],
            "desc" : data.get("abstract", "")
        }

    @override
    def get_output(self, input_data: Any, result: Any) -> Any:
        """子类必须实现：处理Chain输出"""
        return {
            "id" : Funcs.wiki_dict_getid(input_data),
            "out": result
        }
