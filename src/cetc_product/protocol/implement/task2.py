from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
from typing import Callable, Dict, List, Protocol, Any, Set, TypeVar, Generic, override, runtime_checkable
from loguru import logger
from pydantic import BaseModel
import yaml

from cetc_product.data_model.entity import DomainEnum, EntityType, PersonSubtype, RegionEnum
from cetc_product.data_model.run_mode import ChainRunModeEnum
from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.protocol.base import BaseLangChainTask
from cetc_product.tools.tiny_tool import safe_get
from cetc_product.tools.func_tools import Funcs


# 模块级函数 - 天然可序列化
def _validate_task2_data(
    data: Dict[str, Any],
    target_domains: Set[str],
    target_regions: Set[str]
) -> bool:
    """
    Task1 验证函数
    
    Args:
        data: 输入数据
        target_domains: 目标领域集合
        target_regions: 目标区域集合
    
    Returns:
        是否通过验证
    """
    entity_info = data.get("entity_classification", {}).get("result", {})
    if (entity_info.get("type") != EntityType.PERSON) or \
        (entity_info.get("subtype") == PersonSubtype.FICTIONAL):
        return False
    
    domains = safe_get(data, ["domain_and_region_classifier", "result", "domains"], None)
    if domains is None or not (set(domains) & target_domains):
        return False
    
    regions = safe_get(data, ["domain_and_region_classifier", "result", "regions"], None)
    if regions is None or not (set(regions) & target_regions):
        return False
    
    return True


class Task2(BaseLangChainTask):
    """task1 任务类"""
    
    def __init__(self, chain: object):
        super().__init__(chain, task_name = TaskTypeEnum.TASK1)
        self.target_domains = {d.value for d in DomainEnum.get_target_domains()}
        self.target_regions = {r.value for r in RegionEnum.get_target_regions()}
        
    @override
    def get_serializable_validator(self) -> Callable[[Dict[str, Any]], bool]:
        """
        返回一个可序列化的验证函数
        
        Returns:
            验证函数(使用 functools.partial)
        """
        from functools import partial
        
        # 使用 partial 绑定参数,返回可序列化的函数
        return partial(
            _validate_task2_data,
            target_domains=self.target_domains,
            target_regions=self.target_regions
        )
    
    def get_input(self, data: Dict[str,Any]) -> None|Any:
        """子类必须实现：准备输入"""
        infobox_info = safe_get(data, ["infoboxes_info"], None)
        if not infobox_info:
            infobox_info = ""
        else:
            infobox_info = yaml.safe_dump(infobox_info[0], allow_unicode=True, sort_keys=False)
        
        raw_text_path = Path(data.get("markdown_path",None))
        if raw_text_path.exists():
            fragment = raw_text_path.read_text(encoding="utf-8")[:1000]
        else:
            fragment = f"# {data['title']}\n\n{data['abstract']}"
        return {"wiki_text" : f"<infobox>{infobox_info}</infobox>\n\n{fragment}"}
    
    
    
    def get_output(self,input_data:Any, result: Any) -> Any:
        """子类必须实现：处理输出"""
        return {
            "id" : Funcs.wiki_dict_getid(input_data),
            "out" : result
        }