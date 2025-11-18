


from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

from loguru import logger
import orjson
from cetc_product.tools.func_tools import Funcs
import xopen
import orjsonl

from cetc_product.data_model.NER_for_org import OrganizationInfo
from cetc_product.data_model.params import ChainParams, IoParams
from langchain_core.runnables import Runnable
from cetc_product.data_model.run_mode import ChainRunModeEnum
from cetc_product.data_model.task_type import TaskTypeEnum
from cetc_product.tools.IO_tool import read_data_batched
from cetc_product.protocol.implement.task1 import Task1
from cetc_product.tools.log_config import setup_logger
from cetc_product.tools.tiny_tool import pretty_dict, safe_get
from cetc_product.protocol.implement.task2 import Task2
from cetc_product.data_model.NER_for_person import PersonInfo
from cetc_product.tools.file_checkpoint import FileCheckpoint
class Pipeline:
    
    
    
    def __init__(self, log_dir: Path | str = "./logs"):
        setup_logger(log_dir = log_dir)
        self.init_func_map = {
            TaskTypeEnum.TASK1 : self._init_task1,
            TaskTypeEnum.TASK2 : self._init_task2,
        }    
        self.test = True
        self.cur_task = None
        self.task = None
        self.cur_params = {
            "io_params" : None,
            "chain_params" : None
        }
        logger.success("Pipeline 初始化完成")
        
    def bind(self, task_type:TaskTypeEnum, task_params:Dict[str, str]):     # 在这里进行checkpoint组件的初始化
        logger.info(f"绑定任务: {task_type.value}")
        
        self.cur_task = task_type
        self.cur_task_params = task_params
        init_func = self.init_func_map.get(task_type, None)
        
        # 在这里进行checkpoint组件的初始化
        
        
        if init_func is None:
            logger.error(f"不支持的任务类型: {task_type}")
            raise ValueError(f"不支持的任务: {task_type}")
        
        try:
            init_func(task_params)
            logger.success(f"任务 {task_type.value} 初始化成功")
        except Exception as e:
            logger.exception(f"任务 {task_type.value} 初始化失败")
            raise

    def _task_params_parse(
        self, 
        actual_params: Dict[str, Any], 
        require_params: set, 
        optional_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        解析任务参数
        
        Args:
            actual_params: 实际参数
            require_params: 必需参数集合
            optional_params: 可选参数字典
        
        Returns:
            合并后的参数字典
        """
        optional_params = optional_params or {}
        
        # 检查必需参数
        missing_params = require_params - set(actual_params.keys())
        if missing_params:
            logger.error(f"任务 {self.cur_task.value} 缺少必需参数: {missing_params}")
            raise ValueError(f"任务 {self.cur_task.value} 缺少参数: {missing_params}")
        
        # 合并参数
        _actual_params = optional_params | actual_params.copy()
        
        logger.debug(f"任务 <{self.cur_task.value}> 参数解析完成")
        logger.info(f"任务参数:\n{pretty_dict(_actual_params)}")
        
        return _actual_params
    def _init_checkpoint(self, task_params: Dict[str, Any]):
        """统一的 checkpoint 初始化逻辑"""
        checkpoint_path = task_params.get("checkpoint_path")
        
        if checkpoint_path is None:
            logger.warning("未配置 checkpoint_path，跳过断点续传功能")
            self.checkpoint = None
            return
        
        # ✅ 实现读取历史数据的函数
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
            backfill_is_good=Funcs.simple_dict_good  # ✅ 传入真实的读取函数
        )
        logger.info(f"Checkpoint 组件初始化完成: {checkpoint_path}")
    def _init_task1(self, task_params:Dict[str,Any]):
        # 扫描参数
        require_params = {"inpath", "outpath", "prompt_path"}
        optional_params = {
            "read_batch_size": 2,
            "llm_name" : "doubao_flash",
            "checkpoint_path": None,
            "writed_data_paths" : None
        }
        task_params = self._task_params_parse(task_params, require_params, optional_params)
        # 记录参数
        
        
        self._init_checkpoint(task_params)
        
        self.cur_params["io_params"] = IoParams(
            inpath = task_params["inpath"], 
            read_batch_size = task_params["read_batch_size"], 
            outpath = task_params["outpath"]
            )
        logger.debug(f"输入路径: {self.cur_params['io_params'].inpath}")
        logger.debug(f"输出路径: {self.cur_params['io_params'].outpath_with_now}")


        self.cur_params["chain_params"] = ChainParams(
            llm_name = task_params["llm_name"], 
            prompt_path=task_params["prompt_path"], 
            data_model=OrganizationInfo
            )
        
        
        logger.debug(f"LLM: {task_params['llm_name']}")
        logger.debug(f"Prompt: {task_params['prompt_path']}")
        
        # 初始化任务
        self.task = Task1(self.cur_params["chain_params"].chain)
        logger.info("任务1初始化完成")

    def _init_task2(self, task_params:Dict[str,Any]):
        # 扫描参数
        require_params = {"inpath", "outpath", "prompt_path"}
        optional_params = {
            "read_batch_size": 2,
            "llm_name" : "doubao_flash"
        }
        task_params = self._task_params_parse(task_params, require_params, optional_params)
        self._init_checkpoint(task_params)
        
        
        self.cur_params["io_params"] = IoParams(
            inpath = task_params["inpath"], 
            read_batch_size = task_params["read_batch_size"], 
            outpath = task_params["outpath"]
            )
        logger.debug(f"输入路径: {self.cur_params['io_params'].inpath}")
        logger.debug(f"输出路径: {self.cur_params['io_params'].outpath_with_now}")


        self.cur_params["chain_params"] = ChainParams(
            llm_name = task_params["llm_name"], 
            prompt_path=task_params["prompt_path"], 
            data_model=PersonInfo
            )
        
        
        logger.debug(f"LLM: {task_params['llm_name']}")
        logger.debug(f"Prompt: {task_params['prompt_path']}")
        
        # 初始化任务
        self.task = Task2(self.cur_params["chain_params"].chain)
        logger.info("任务2初始化完成")

        
    def run(self, test = False)->Dict[str, Any]:
        if self.task is None:
            logger.error("未绑定任务,请先调用 bind() 方法")
            raise RuntimeError("未绑定任务")
        logger.info(f"{'='*60}")
        logger.info(f"{'测试' if test else '正式'}运行任务: {self.cur_task.value}")
        logger.info(f"{'='*60}")
        
        # 创建输出目录
        outpath = self.cur_params["io_params"].outpath_with_now
        outpath.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出文件: {outpath}")
        
        
        read_buffer = []
        read_batch_size = self.cur_params["io_params"].read_batch_size
        
        
        
        try:
            with open(outpath, "wb") as fout:
                checkpoint_log = {"total_processed": 0, "total_skipped": 0}
                for inpath_list, indata_list in read_data_batched(
                    self.cur_params["io_params"].inpaths, 
                    n =read_batch_size,
                    filter_func=self.task.get_serializable_validator()
                    ):
                    

                    # 使用checkpoint组件过滤数据并添加到缓冲区
                    if self.checkpoint:
                        filtered_data, skipped = self.checkpoint.filter(
                            indata_list,
                            get_id=Funcs.wiki_dict_getid
                        )
                        checkpoint_log["total_skipped"] += skipped
                        read_buffer.extend(filtered_data)
                    else:
                        read_buffer.extend(indata_list)
                        
                        
                    task_response, read_buffer = self._task_submit(read_buffer, 
                                                                   read_batch_size if not self.test else len(read_buffer), 
                                                                   fout)
                    
                    if self.checkpoint and task_response:
                        marked, failed = self.checkpoint.update(
                            outpath,
                            task_response,
                            is_good=Funcs.simple_dict_good,
                            get_id=Funcs.simple_dict_getid
                        )

                        checkpoint_log["total_processed"] += marked
                        
                        logger.info(f"本批成功: {marked} / {checkpoint_log['total_processed']} 条, 跳过: {failed} / {checkpoint_log['total_skipped']} 条")
                    if test:
                        logger.info(task_response[0])
                        break
                    
                    
                else:
                    self._task_submit(read_buffer, 1, fout)
        finally:
            # ✅ 确保最终保存
            if self.checkpoint:
                self.checkpoint.save()
                logger.success(f"Checkpoint 已保存: {self.checkpoint.file_path}")

    def _task_submit(self, buffer, in_size, fout)->Tuple[List[Any], List[Any]]:
        if len(buffer) < in_size:
            return [], buffer
        task_response = self.task.run(buffer[:in_size], ChainRunModeEnum.ABATCH)
        if fout:
            fout.write(b"\n".join([orjson.dumps(r) for r in task_response]))
        return task_response, buffer[in_size:]
            
if __name__ == "__main__":
    ...
    # 测试任务1
    pipe = Pipeline()
    task1_params = {
        "inpath" : "/mnt/samba_shared/wyw/code/中电科_分类/data/domain_and_region/enwiki/1/*.jsonl.zst",
        "read_batch_size" : 80,
        "outpath" : "/Data_two/wyw/code/CETC_product/data/out",
        "llm_name" : "doubao_thinking",
        "prompt_path" : "/Data_two/wyw/code/CETC_product/data/prompts/NER_for_org.txt"
    }
    pipe.bind(TaskTypeEnum.TASK1, task1_params)
    pipe.run(test = True)
    
    
    # 测试任务2
    