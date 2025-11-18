import argparse
from pathlib import Path
from typing import Dict, Any, Tuple
import tomllib
from loguru import logger

from cetc_product.tools.tiny_tool import safe_get


class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self, config_path: Path | str):
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """加载 TOML 配置文件"""
        if self._config is None:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, "rb") as f:
                self._config = tomllib.load(f)
            
            logger.info(f"成功加载配置文件: {self.config_path}")
        
        return self._config
    TASK_KEYS = Tuple[str, str]
    def _enhance_config(self, task_key:TASK_KEYS, task_config: Dict[str, Any]) -> Dict[str, Any]:
        enhanced_config = task_config.copy()
        
        if "outpath" in enhanced_config:
            enhanced_config["outpath"] = str(Path(enhanced_config["outpath"]) / task_key[0] / task_key[1])
            
        if "checkpoint_path" in enhanced_config:
            enhanced_config["checkpoint_path"] = str(Path(enhanced_config["checkpoint_path"]) / task_key[0] / task_key[1])
            
        if isinstance(enhanced_config.get("writed_data_paths"), str):
            glob_path = enhanced_config["writed_data_paths"]
            enhanced_config["writed_data_paths"] = sorted(list(Path(glob_path).parent.glob(Path(glob_path).name)))
        return enhanced_config  
    
    def get_task_config(self, task: str, source: str) -> Dict[str, Any]:
        """
        获取指定任务和数据源的配置
        
        Args:
            task: 任务名称,如 "task1"
            source: 数据源名称,如 "zhwiki"
        
        Returns:
            任务配置字典
        """
        config = self.load()
        cur_config = config
        task_key = [task, source]
        for k in task_key:
            if k not in cur_config:
                available_tasks = [k for k in config.keys() if k.startswith(task)]
                raise KeyError(
                    f"配置中未找到 [{task_key}]\n"
                    f"可用的配置: {available_tasks}"
                )
            else:
                cur_config = cur_config[k]
        
            
        
        task_config = safe_get(config, task_key)
        task_config = self._enhance_config(task_key, task_config)
        
        logger.info(f"加载配置: [{task_key}]")
        
        return task_config


def setup_argparse() -> argparse.Namespace:
    """
    设置命令行参数解析
    
    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="CETC 产品数据处理管道",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行 task1 的 zhwiki 数据
  python -m cetc_product.core.pipeline --task task1 --source zhwiki
  
  # 测试模式
  python -m cetc_product.core.pipeline --task task1 --source zhwiki --test
  
  # 指定配置文件
  python -m cetc_product.core.pipeline --task task1 --source zhwiki --config /path/to/config.toml
  
  # 自定义日志目录
  python -m cetc_product.core.pipeline --task task1 --source zhwiki --log-dir ./logs
        """
    )
    
    # 必需参数
    parser.add_argument(
        "--task",
        "-t",
        type=str,
        required=True,
        help="任务类型 (如: task1, task2)"
    )
    
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        required=True,
        help="数据源 (如: zhwiki, enwiki)"
    )
    
    # 可选参数
    parser.add_argument(
        "--config",
        type=str,
        default="./config.toml",
        help="配置文件路径 (默认: ./config.toml)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试模式,只处理一批数据"
    )
    
    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="日志目录 (默认: ./logs)"
    )
    
    # 参数覆盖 (可选,用于临时覆盖配置文件中的值)
    parser.add_argument(
        "--inpath",
        type=str,
        help="输入路径 (覆盖配置文件)"
    )
    
    parser.add_argument(
        "--outpath",
        type=str,
        help="输出路径 (覆盖配置文件)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        help="批处理大小 (覆盖配置文件)"
    )
    
    parser.add_argument(
        "--llm-name",
        "-llm",
        type=str,
        help="LLM 名称 (覆盖配置文件)"
    )
    
    args = parser.parse_args()
    
    return args


def load_task_params(args: argparse.Namespace) -> Dict[str, Any]:
    """
    根据命令行参数加载任务配置
    
    Args:
        args: 命令行参数
    
    Returns:
        任务参数字典
    """
    # 加载配置文件
    loader = ConfigLoader(args.config)
    task_params = loader.get_task_config(args.task, args.source)
    
    # 命令行参数覆盖配置文件
    overrides = {
        "inpath": args.inpath,
        "outpath": args.outpath ,
        "read_batch_size": args.batch_size,
        "llm_name": args.llm_name,
    }
    
    # 只保留非 None 的覆盖值
    overrides = {k: v for k, v in overrides.items() if v is not None}
    
    if overrides:
        logger.info(f"命令行参数覆盖: {overrides}")
        task_params.update(overrides)
    
    return task_params


if __name__ == "__main__":
    # 测试
    args = setup_argparse()
    print(f"任务: {args.task}")
    print(f"数据源: {args.source}")
    print(f"配置文件: {args.config}")
    print(f"测试模式: {args.test}")
    
    try:
        params = load_task_params(args)
        print(f"\n任务参数: {params}")
    except Exception as e:
        print(f"错误: {e}")