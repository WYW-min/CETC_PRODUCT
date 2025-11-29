from loguru import logger

from cetc_product.core.pipeline import Pipeline
from cetc_product.data_model.task_type import TaskTypeEnum


def main():
    """主入口函数,支持命令行参数"""
    from cetc_product.tools.setup_argparse import setup_argparse, load_task_params
    
    # 解析命令行参数
    args = setup_argparse()
    
    # 加载任务参数
    task_params = load_task_params(args)
    
    # 创建 Pipeline
    pipe = Pipeline(log_dir=args.log_dir)
    
    # 绑定任务
    task_type = TaskTypeEnum[args.task.upper()]
    pipe.bind(task_type, task_params)
    
    # 运行任务
    result = pipe.run(test=args.test)
    
    logger.success(f"任务完成: {result}")
    
if __name__ == "__main__":
    main()