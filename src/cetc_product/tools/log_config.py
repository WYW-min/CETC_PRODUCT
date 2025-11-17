from pathlib import Path
from loguru import logger
import sys
from datetime import datetime


class LoggerConfig:
    """日志配置管理器"""
    
    _initialized = False
    
    @classmethod
    def setup(
        cls,
        log_dir: Path | str | None = None,
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        error_level: str = "ERROR",
        rotation: str = "00:00",
        retention: str = "30 days",
        compression: str = "zip",
        date_partition: bool = True  # 新增: 是否按日期分区
    ):
        """
        配置 loguru 日志
        
        Args:
            log_dir: 日志根目录,None 则只输出到控制台
            console_level: 控制台日志级别
            file_level: 文件日志级别
            error_level: 错误日志级别
            rotation: 日志轮转时间
            retention: 日志保留时间
            compression: 日志压缩格式
            date_partition: 是否按日期创建子文件夹 (默认: True)
        """
        if cls._initialized:
            logger.warning("日志已初始化,跳过重复配置")
            return
        
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sink=sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level=console_level,
            colorize=True
        )
        
        # 如果指定了日志目录,添加文件日志
        if log_dir:
            log_dir = Path(log_dir)
            
            # 根据是否启用日期分区,决定日志文件路径
            if date_partition:
                # 按日期创建子文件夹: logs/2025-11-17/
                current_date = datetime.now().strftime("%Y-%m-%d")
                log_subdir = log_dir / current_date
                log_subdir.mkdir(parents=True, exist_ok=True)
                
                # 日志文件路径使用时间戳
                general_log_path = log_subdir / "pipeline_{time:HH-mm-ss}.log"
                error_log_path = log_subdir / "error_{time:HH-mm-ss}.log"
            else:
                # 不分区,直接在根目录创建
                log_dir.mkdir(parents=True, exist_ok=True)
                general_log_path = log_dir / "pipeline_{time:YYYY-MM-DD_HH-mm-ss}.log"
                error_log_path = log_dir / "error_{time:YYYY-MM-DD_HH-mm-ss}.log"
            
            # 通用日志文件(所有级别)
            logger.add(
                sink=str(general_log_path),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=file_level,
                rotation=rotation,
                retention=retention,
                compression=compression,
                encoding="utf-8",
                enqueue=True  # 异步写入
            )
            
            # 错误日志文件(只记录 ERROR 及以上)
            logger.add(
                sink=str(error_log_path),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
                level=error_level,
                rotation=rotation,
                retention="90 days",  # 错误日志保留更久
                compression=compression,
                encoding="utf-8",
                backtrace=True,  # 显示完整堆栈
                diagnose=True,   # 显示变量值
                enqueue=True
            )
            
            if date_partition:
                logger.info(f"日志目录(按日期分区): {log_subdir.absolute()}")
            else:
                logger.info(f"日志目录: {log_dir.absolute()}")
        
        cls._initialized = True
        logger.success("日志系统初始化完成")
    
    @classmethod
    def reset(cls):
        """重置日志配置"""
        logger.remove()
        cls._initialized = False
        logger.info("日志系统已重置")


# 提供便捷函数
def setup_logger(log_dir: Path | str | None = None, **kwargs):
    """
    便捷的日志配置函数
    
    示例:
        # 默认按日期分区
        setup_logger("/path/to/logs")
        
        # 不使用日期分区
        setup_logger("/path/to/logs", date_partition=False)
        
        # 自定义日志级别
        setup_logger("/path/to/logs", console_level="DEBUG")
    """
    LoggerConfig.setup(log_dir, **kwargs)