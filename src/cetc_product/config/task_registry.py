from typing import Any, Dict, Type

from pydantic import BaseModel

from cetc_product.data_model.NER_for_event import NetFluctuationSample
from cetc_product.data_model.NER_for_org import OrganizationInfo
from cetc_product.data_model.NER_for_person import PersonInfo
from cetc_product.data_model.NER_for_social import ExtractionSample
from cetc_product.data_model.enhance_for_domain import EnhancedDomain
from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.protocol.implement.task1 import Task1
from cetc_product.protocol.implement.task2 import Task2
from cetc_product.protocol.implement.task3 import Task3
from cetc_product.protocol.implement.task5 import Task5
from cetc_product.protocol.base import BaseLangChainTask
from cetc_product.protocol.implement.task_domain_enhance import TaskDomainEnhance


class TaskConfig:
    """任务配置类"""

    def __init__(
        self,
        task_class: Type[BaseLangChainTask],
        data_model: Type[BaseModel],
        require_params: set,
        optional_params: Dict[str, Any] = None,
    ):
        self.task_class = task_class
        self.data_model = data_model
        self.require_params = require_params
        self.optional_params = optional_params or {}


# 任务注册表 - 集中管理所有任务配置
TASK_REGISTRY: Dict[TaskTypeEnum, TaskConfig] = {
    TaskTypeEnum.TASK1: TaskConfig(
        task_class=Task1,
        data_model=OrganizationInfo,
        require_params={"inpath", "outpath", "prompt_path"},
        optional_params={
            "read_batch_size": 2,
            "llm_name": "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths": None,
        },
    ),
    TaskTypeEnum.TASK2: TaskConfig(
        task_class=Task2,
        data_model=PersonInfo,
        require_params={"inpath", "outpath", "prompt_path"},
        optional_params={
            "read_batch_size": 2,
            "llm_name": "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths": None,
        },
    ),
    TaskTypeEnum.DOMAIN_ENHANCE: TaskConfig(
        task_class=TaskDomainEnhance,  # 领域增强任务
        data_model=EnhancedDomain,
        require_params={"inpath", "outpath", "prompt_path"},
        optional_params={
            "domain_enhance_map_path": None,
            "read_batch_size": 2,
            "llm_name": "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths": None,
        },
    ),
    TaskTypeEnum.TASK3: TaskConfig(
        task_class=Task3,  #
        data_model=ExtractionSample,  # 假设有一个领域增强的数据模型
        require_params={"inpath", "outpath", "prompt_path"},
        optional_params={
            "read_batch_size": 2,
            "llm_name": "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths": None,
        },
    ),
    TaskTypeEnum.TASK5: TaskConfig(
        task_class=Task5,  #
        data_model=NetFluctuationSample,  # 假设有一个领域增强的数据模型
        require_params={"inpath", "outpath", "prompt_path"},
        optional_params={
            "read_batch_size": 2,
            "llm_name": "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths": None,
        },
    ),
}
