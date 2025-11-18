from functools import partial
import math
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Callable, Generator, List, Set, Tuple, TypeVar
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from cetc_product.tools.json_parser import MyJSONParser
from loguru import logger
import xopen
import orjson
from itertools import batched
from tqdm.auto import tqdm
from multiprocessing import Pool, cpu_count
import sys
T = TypeVar("T")
GE_DATA = Generator[Tuple[Path, Any], None, None]

def count_json_line(inpath:Path, filter_func)->int:
    total_lines = 0
    with xopen.xopen(inpath, "r") as fin:
        for line in fin:
            if line.strip():
                total_lines +=filter_func(orjson.loads(line))

    return total_lines
def count_json_lines_parallel(
    inpaths: List[Path], 
    filter_func: Callable[[Any], bool],
    n_workers: int = None
) -> int:
    """
    并行统计多个文件的 JSON 行数
    
    Args:
        inpaths: 输入文件路径列表
        filter_func: 过滤函数
        n_workers: 工作进程数,None 则使用 CPU 核心数
    
    Returns:
        总行数
    """
    if n_workers is None:
        n_workers = min(cpu_count(), len(inpaths))
    
    # 对于少量文件,不使用多进程
    if len(inpaths) <= 2 or n_workers <= 1:
        logger.debug(f"文件数量较少({len(inpaths)}),使用单进程统计")
        return sum(count_json_line(path, filter_func) for path in inpaths)
    
    logger.info(f"使用 {n_workers} 个进程统计 {len(inpaths)} 个文件的行数")
    
    try:
        # 创建部分应用函数
        count_func = partial(count_json_line, filter_func=filter_func)
        
        # 使用进程池并行处理
        with Pool(processes=n_workers) as pool:
            # 使用 imap_unordered 获取进度
            results = []
            with tqdm(
                total=len(inpaths),
                desc="统计文件行数",
                unit="文件",
                colour="blue",
                ncols=100
            ) as pbar:
                for count in pool.imap_unordered(count_func, inpaths, chunksize=1):
                    results.append(count)
                    pbar.update(1)
            
            total = sum(results)
            logger.success(f"统计完成,共 {total:,} 行")
            return total
            
    except Exception as e:
        logger.exception(f"并行统计失败,回退到单进程: {e}")
        return sum(count_json_line(path, filter_func) for path in inpaths)

# 添加一个checkpoint组件
def read_data_batched(inpaths, n = 2, filter_func = lambda x: bool(x))->Generator:
    total = count_json_lines_parallel(inpaths, filter_func)
    
    pbar = tqdm(
        desc="读取数据",
        unit="条",           # 单位
        unit_scale=True,    # 自动缩放（1000 -> 1k）
        ncols=100,          # 进度条宽度
        position=0,
        leave=True,
        colour="green",     # 颜色
        dynamic_ncols=False,   # 自动适应终端宽度
        ascii=False,
        file = sys.stdout,
        mininterval=0.5,
        total = total
    )
    for batch in batched(read_data(inpaths, filter_func), n = n):
        if batch:
            pbar.update(len(batch))

            yield  (
                [b[0] for b in batch],
                [b[1] for b in batch]
                )
        
        



def read_data(inpaths:List[Path], filter_func:Callable[[Any], bool])->GE_DATA:
    logger.info(f"找到 {len(inpaths)} 个文件")
    for file_idx, current_path in enumerate(inpaths):
        logger.info(f"[{file_idx + 1}/{len(inpaths)}] 处理文件: {current_path}")
        
        if not current_path.exists():
            logger.error(f"文件不存在: {current_path}")
            continue
            
        try:
            # 使用 with 确保文件正确关闭
            with xopen.xopen(current_path, "r") as fin:
                
                for line_no, line in enumerate(fin, 1):
                    
                    line = line.strip()
                    # 跳过空行
                    if not line:
                        continue
                    
                    try:
                        data = orjson.loads(line)
                        if filter_func(data):
                            yield current_path, data
                    except orjson.JSONDecodeError as e:
                            logger.warning(
                                f"跳过无效 JSON (文件: {current_path.name}, "
                                f"行: {line_no}): {str(e)[:100]}"
                            )
                            continue

                    except Exception as e:
                        logger.error(f"处理行 {line_no} 时出错: {e}")              
        except Exception as e:
            logger.error(f"读取文件失败 {current_path}: {e}")

    


def load_prompt(prompt_path:Path|str, schema_define_cls:BaseModel|None = None)->PromptTemplate:
    if isinstance(prompt_path, str):
        prompt_path = Path(prompt_path)
        
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    

    prompt_temp =  PromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))
    if "schema_definition" in prompt_temp.input_variables and schema_define_cls is not None:
        prompt_temp = prompt_temp.partial(schema_definition=MyJSONParser(schema_define_cls).get_format_instructions())
    
    return prompt_temp


def enhance_inpath(inpath:Path)->Path|List[Path]:
    inpaths = sorted(list(Path(inpath.parent).glob(inpath.name)))
    return inpaths

def enhance_outpath(outpath:Path)->Path:
    from datetime import datetime
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if outpath.suffix == "":
        enhanced_outpath = outpath / now_str
    else:
        enhanced_outpath = outpath.parent / f"{outpath.stem}_{now_str}{outpath.suffix}"
        
    return enhanced_outpath