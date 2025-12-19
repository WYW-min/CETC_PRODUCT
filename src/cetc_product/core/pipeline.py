from pathlib import Path
from typing import Any, Dict, List, Tuple

from loguru import logger
import orjson
from cetc_product.config.run_stats import RunStats
from cetc_product.config.task_registry import TASK_REGISTRY, TaskConfig
from cetc_product.protocol.base import BaseLangChainTask
from cetc_product.tools.func_tools import Funcs
import xopen

from cetc_product.data_model.NER_for_org import OrganizationInfo
from cetc_product.data_model.params import ChainParams, IoParams
from cetc_product.data_model.run_mode import ChainRunModeEnum
from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.tools.IO_tool import read_data_batched
from cetc_product.protocol.implement.task1 import Task1
from cetc_product.config.log_config import setup_logger
from cetc_product.tools.tiny_tool import pretty_dict
from cetc_product.protocol.implement.task2 import Task2
from cetc_product.data_model.NER_for_person import PersonInfo
from cetc_product.tools.file_checkpoint import FileCheckpoint


class Pipeline:

    def __init__(self, log_dir: Path | str = "./logs"):
        setup_logger(log_dir=log_dir)
        self.cur_task: TaskTypeEnum | None = None
        self.task: BaseLangChainTask | None = None
        self.checkpoint: FileCheckpoint | None = None
        self.cur_params: Dict[str, Any] = {
            "io_params": None, 
            "chain_params": None
        }
        logger.success("Pipeline 初始化完成")

    def bind(self, task_type: TaskTypeEnum, task_params: Dict[str, Any]):
        """
        绑定任务类型和参数
        
        Args:
            task_type: 任务类型
            task_params: 任务参数
        """
        logger.info(f"绑定任务: {task_type.value}")
        
        # 获取任务配置
        task_config = TASK_REGISTRY.get(task_type)
        if task_config is None:
            logger.error(f"不支持的任务类型: {task_type}")
            raise ValueError(f"不支持的任务: {task_type}")
        
        self.cur_task = task_type
        
        try:
            self._init_task(task_config, task_params)
            logger.success(f"任务 {task_type.value} 初始化成功")
        except Exception as e:
            logger.exception(f"任务 {task_type.value} 初始化失败")
            raise
        


    def run(self, test: bool = False) -> Dict[str, Any]:
        """
        运行任务        
        Args:
            test: 是否为测试模式
        Returns: 运行统计信息
        """
        self._validate_task()
        
        outpath = self._prepare_output()
        stats = RunStats()
        
        try:
            with open(outpath, "wb") as fout:
                self._process_data(fout, stats, test)
        finally:
            self._finalize(stats)
        
        return stats.to_dict()



#region private_methods
    def _init_task(self, config: TaskConfig, task_params: Dict[str, Any]):
        """
        统一的任务初始化逻辑
        
        Args:
            config: 任务配置
            task_params: 任务参数
        """
        # 1. 解析参数
        parsed_params = self._parse_params(
            task_params, 
            config.require_params, 
            config.optional_params
        )
        
        # 2. 初始化 checkpoint
        self._init_checkpoint(parsed_params)
        
        # 3. 初始化 IO 参数
        self.cur_params["io_params"] = IoParams(
            inpath=parsed_params["inpath"],
            read_batch_size=parsed_params["read_batch_size"],
            outpath=parsed_params["outpath"],
        )
        logger.debug(f"输入路径: {self.cur_params['io_params'].inpath}")
        logger.debug(f"输出路径: {self.cur_params['io_params'].outpath_with_now}")
        
        # 4. 初始化 Chain 参数
        self.cur_params["chain_params"] = ChainParams(
            llm_name=parsed_params["llm_name"],
            prompt_path=parsed_params["prompt_path"],
            data_model=config.data_model,
        )
        logger.debug(f"LLM: {parsed_params['llm_name']}")
        logger.debug(f"Prompt: {parsed_params['prompt_path']}")
        
        # 5. 初始化任务实例
        self.task = config.task_class(self.cur_params["chain_params"].chain)
        logger.info(f"任务 {self.cur_task.value} 初始化完成")
        
        # 6. ✅ 初始化任务独特参数
        self.task.init_extra_params(parsed_params)

    def _parse_params(
        self,
        actual_params: Dict[str, Any],
        require_params: set,
        optional_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析并验证参数"""
        # 检查必需参数
        missing = require_params - set(actual_params.keys())
        if missing:
            raise ValueError(f"缺少必需参数: {missing}")
        
        # 合并参数（可选参数 + 实际参数）
        merged = optional_params.copy()
        merged.update(actual_params)
        
        logger.info(f"任务参数:\n{pretty_dict(merged)}")
        return merged

    def _init_checkpoint(self, task_params: Dict[str, Any]):
        """统一的 checkpoint 初始化逻辑"""
        checkpoint_path = task_params.get("checkpoint_path")

        if checkpoint_path is None:
            logger.warning("未配置 checkpoint_path，跳过断点续传功能")
            self.checkpoint = None
            return

        def read_writed_data(path: Path) -> List[Dict]:
            records = []
            with xopen.xopen(path, "r") as fin:
                for line in fin:
                    try:
                        records.append(orjson.loads(line))
                    except Exception as e:
                        logger.debug(f"解析行失败: {e}")
                        continue
            logger.debug(f"从 {path} 读取了 {len(records)} 条记录")
            return records

        self.checkpoint = FileCheckpoint(
            file_path=checkpoint_path,
            writed_data_paths=task_params.get("writed_data_paths"),
            read_writed_data_func=read_writed_data,
            backfill_get_id=Funcs.simple_dict_getid,
            backfill_is_good=Funcs.simple_dict_good,  # ✅ 传入真实的读取函数
        )
        logger.info(f"Checkpoint 组件初始化完成: {checkpoint_path}")
        
    def _validate_task(self):
        """验证任务是否已绑定"""
        if self.task is None:
            logger.error("未绑定任务,请先调用 bind() 方法")
            raise RuntimeError("未绑定任务")
        
        logger.info(f"{'='*60}")
        logger.info(f"运行任务: {self.cur_task.value}")
        logger.info(f"{'='*60}")

    def _prepare_output(self) -> Path:
        """准备输出目录"""
        outpath = self.cur_params["io_params"].outpath_with_now
        outpath.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出文件: {outpath}")
        return outpath
        
    def _process_data(self, fout, stats: "RunStats", test: bool):
        """处理数据的核心逻辑"""
        buffer = []
        batch_size = self.cur_params["io_params"].read_batch_size
        validator = self.task.get_serializable_validator()
        
        for _, indata_list in read_data_batched(
            self.cur_params["io_params"].inpaths,
            n=batch_size,
            filter_func=validator,
        ):
            # 使用 checkpoint 过滤
            filtered = self._filter_with_checkpoint(indata_list, stats)
            buffer.extend(filtered)
            
            # 提交任务
            submit_size = batch_size if not test else len(buffer)
            response, buffer = self._submit_batch(buffer, submit_size, fout)
            
            # 更新 checkpoint
            self._update_checkpoint(fout.name, response, stats)
            
            if test and response:
                logger.info(f"测试输出:\n{pretty_dict(response[0])}")
                break
        else:
            # 处理剩余数据
            if buffer:
                response, _ = self._submit_batch(buffer, 1, fout)
                self._update_checkpoint(fout.name, response, stats)

    def _filter_with_checkpoint(
        self, 
        data_list: List[Dict], 
        stats: "RunStats"
    ) -> List[Dict]:
        """使用 checkpoint 过滤数据"""
        if self.checkpoint is None:
            return data_list
        
        filtered, skipped = self.checkpoint.filter(
            data_list, 
            get_id=Funcs.wiki_dict_getid
        )
        stats.skipped += skipped
        return filtered

    def _submit_batch(
        self, 
        buffer: List[Dict], 
        batch_size: int, 
        fout
    ) -> Tuple[List[Any], List[Dict]]:
        """提交一批数据处理"""
        if len(buffer) < batch_size:
            return [], buffer
        
        batch = buffer[:batch_size]
        remaining = buffer[batch_size:]
        
        response = self.task.run(batch, ChainRunModeEnum.ABATCH)
        
        if fout and response:
            fout.write(b"\n".join(orjson.dumps(r) for r in response))
            fout.write(b"\n")
        
        return response, remaining
    
    def _update_checkpoint(
        self, 
        outpath: Path, 
        response: List[Any], 
        stats: "RunStats"
    ):
        """更新 checkpoint"""
        if self.checkpoint is None or not response:
            return
        
        marked, failed = self.checkpoint.update(
            outpath,
            response,
            is_good=Funcs.simple_dict_good,
            get_id=Funcs.simple_dict_getid,
        )
        
        stats.processed += marked
        stats.failed += failed
        
        logger.info(
            f"本批成功: {marked}, 总计: {stats.processed}, "
            f"失败: {failed}, 跳过: {stats.skipped}"
        )

    def _finalize(self, stats: "RunStats"):
        """完成处理,保存 checkpoint"""
        if self.checkpoint:
            self.checkpoint.save()
            logger.success(f"Checkpoint 已保存: {self.checkpoint.file_path}")
        
        logger.info(f"{'='*60}")
        logger.info(f"任务完成: 处理 {stats.processed}, 失败 {stats.failed}, 跳过 {stats.skipped}")
        logger.info(f"{'='*60}")



if __name__ == "__main__":
    ...
    # 测试任务1
    pipe = Pipeline()
    task1_params = {
        "inpath": "/mnt/samba_shared/wyw/code/中电科_分类/data/domain_and_region/enwiki/1/*.jsonl.zst",
        "read_batch_size": 80,
        "outpath": "/Data_two/wyw/code/CETC_product/data/out",
        "llm_name": "doubao_thinking",
        "prompt_path": "/Data_two/wyw/code/CETC_product/data/prompts/NER_for_org.txt",
    }
    pipe.bind(TaskTypeEnum.TASK1, task1_params)
    result = pipe.run(test=True)
    print(result)

    # 测试任务2
