from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Hashable, Set, Iterable, Callable, TypeVar, Generic, List, Tuple
from pydantic import BaseModel, Field
import os
from loguru import logger
from cetc_product.tools.tiny_tool import pretty_dict

TRecord = TypeVar("TRecord")
TId = TypeVar("TId")


class CheckpointState(BaseModel):
    """
    - key: path（字符串）
    - value: 该 path 对应的已处理成功的 id 集合（字符串）
    """
    paths: Dict[str, Set[str]] = Field(default_factory=dict)  # ✅ 只存储 str

    @property
    def all_ids(self) -> Set[str]:
        """所有路径上的 id 全集"""
        all_ids: Set[str] = set()
        for v in self.paths.values():
            all_ids.update(v)
        return all_ids

    @property
    def simple_count(self) -> Dict[str, int]:
        """每个路径上的 id 数量"""
        count_dict = {k: len(v) for k, v in self.paths.items()}
        return {"total": len(self.all_ids)} | count_dict


class FileCheckpoint(Generic[TRecord, TId]):
    """
    基于单个 JSON 文件的 checkpoint 管理器
    
    核心设计：
    - 支持读写阶段不同的数据结构和 ID 提取逻辑
    - 读取阶段：filter() 过滤已处理数据
    - 写入阶段：update() 标记成功数据
    """

    def __init__(
        self,
        file_path: str | Path,
        writed_data_paths: Iterable[str | Path] | None = None,
        read_writed_data_func: Callable[[str | Path], Iterable[TRecord]] | None = None,
        backfill_get_id: Callable[[TRecord], TId] | None = None,
        backfill_is_good: Callable[[TRecord], bool] = lambda r: True,
    ):
        """
        Args:
            file_path: checkpoint 文件路径
            writed_data_paths: 已写入的历史数据路径列表（用于回填）
            read_writed_data_func: 读取历史数据的函数
            backfill_get_id: 从历史数据中提取 ID 的函数
            backfill_is_good: 判断历史数据是否有效的函数
        """
        self.file_path = Path(file_path)

        # 1) 加载已有状态
        self.state = self._load_or_empty()

        # 2) 初始化已处理 id 集合
        self.all_ids: Set[str] = self.state.all_ids.copy()

        # 3) 从历史数据回填（如果提供）
        if writed_data_paths and read_writed_data_func and backfill_get_id:
            self._load_from_history(
                writed_data_paths,
                read_writed_data_func,
                backfill_get_id,
                backfill_is_good
            )

        logger.info(
            f"Checkpoint 初始化完成: {pretty_dict(self.state.simple_count)}"
        )

    # ==================== 核心 API ====================

    def filter(
        self,
        records: Iterable[TRecord],
        get_id: Callable[[TRecord], TId],
    ) -> Tuple[List[TRecord], int]:
        """
        【读取阶段】过滤已处理的数据
        
        Args:
            records: 原始数据
            get_id: 从记录中提取 ID 的函数
        
        Returns:
            (未处理的记录列表, 跳过的数量)
        """
        filtered = []
        skipped_count = 0
        
        for r in records:
            rid = get_id(r)
            if rid not in self.all_ids:
                filtered.append(r)
            else:
                skipped_count += 1
        
        if skipped_count > 0:
            logger.debug(f"跳过已处理数据: {skipped_count} 条")
        
        return filtered, skipped_count

    def update(
        self,
        to_write_path: str | Path,
        records: Iterable[TRecord],
        is_good: Callable[[TRecord], bool],
        get_id: Callable[[TRecord], TId],
    ) -> Tuple[int, int]:
        """
        【写入阶段】标记成功处理的数据
        
        Args:
            to_write_path: 数据写入的目标路径
            records: 已处理的记录
            is_good: 判断记录是否成功的函数
            get_id: 从记录中提取 ID 的函数
        
        Returns:
            (成功标记的数量, 失败的数量)
        """
        path_str = str(to_write_path)
        marked_count = 0
        failed_count = 0
        duplicate_count = 0
        
        for r in records:
            if not is_good(r):
                failed_count += 1
                continue
            
            rid = get_id(r)

            if rid in self.all_ids:
                duplicate_count += 1
                continue
            
            self._mark(path_str, rid)
            marked_count += 1
        
        if marked_count > 0 or failed_count > 0:
            logger.debug(
                f"标记结果: 成功 {marked_count} 条, "
                f"失败 {failed_count} 条, "
                f"重复 {duplicate_count} 条"
            )
        
        return marked_count, failed_count

    def save(self, new_path: str | Path | None = None) -> None:
        """
        保存 checkpoint 状态到磁盘
        
        Args:
            new_path: 新的保存路径（None 则保存到原路径）
        """
        path_to_save = Path(new_path) if new_path is not None else self.file_path

        if new_path is not None:
            self.file_path = path_to_save

        path_to_save.parent.mkdir(parents=True, exist_ok=True)
        data = self.state.model_dump_json(indent=2, exclude_none=True)
        path_to_save.write_text(data, encoding="utf-8")
        logger.debug(f"Checkpoint 已保存: {path_to_save}")

    # ==================== 内部方法 ====================

    def _load_or_empty(self) -> CheckpointState:
        """从文件加载状态，不存在则返回空状态"""
        if not self.file_path.exists():
            return CheckpointState()
        
        try:
            raw = self.file_path.read_text(encoding="utf-8")
            return CheckpointState.model_validate_json(raw)
        except Exception as e:
            logger.warning(f"加载 checkpoint 失败，使用空状态: {e}")
            return CheckpointState()

    def _mark(self, path: str, id_value: Any) -> None:
        """内部方法：标记某个 path 下的 id"""
        if path not in self.state.paths:
            self.state.paths[path] = set()
        
        # ✅ 统一转换为字符串
        id_str = str(id_value) if not isinstance(id_value, (list, tuple)) else "_".join(map(str, id_value))
        
        self.state.paths[path].add(id_str)
        self.all_ids.add(id_str)

    def _load_from_history(
        self,
        paths: Iterable[str | Path],
        read_func: Callable[[str | Path], Iterable[TRecord]],
        get_id: Callable[[TRecord], TId],
        is_good: Callable[[TRecord], bool]
    ) -> None:
        """从历史数据文件中补齐 checkpoint"""
        history_log: Dict[str, int] = defaultdict(int)
        failed_paths: List[str] = []
        
        for p in paths:
            path_str = str(p)
            try:
                if not Path(p).exists():
                    logger.warning(f"历史数据文件不存在: {p}")
                    failed_paths.append(path_str)
                    continue
                
                records = read_func(p)
                marked, failed = self.update(
                    to_write_path=path_str,
                    records=records,
                    is_good=is_good,
                    get_id=get_id
                )
                history_log[path_str] = marked
                
            except Exception as e:
                logger.warning(f"加载历史数据失败: {p} - {e}")
                failed_paths.append(path_str)
        
        if history_log:
            logger.info(f"从历史数据加载: {pretty_dict(dict(history_log))}")
        if failed_paths:
            logger.warning(f"加载失败的路径: {len(failed_paths)} 个")


# ==================== 使用示例 ====================
if __name__ == "__main__":
    import json
    
    # 模拟读写阶段不同的数据结构
    ckpt_path = Path("checkpoint_demo.json")
    if ckpt_path.exists():
        ckpt_path.unlink()

    print("=== Run #1 ===")
    checkpoint = FileCheckpoint[dict, str](file_path=ckpt_path)

    # 1. 读取阶段：原始数据
    read_records = [
        {"page_id": 1, "title": "Python"},
        {"page_id": 2, "title": "Java"},
        {"page_id": 3, "title": "C++"},
    ]
    
    def get_read_id(r: dict) -> str:
        return f"{r['page_id']}_{r['title']}"
    
    to_process, skipped = checkpoint.filter(read_records, get_read_id)
    print(f"待处理: {len(to_process)} 条, 跳过: {skipped} 条")
    
    # 2. 写入阶段：处理后的数据
    write_records = [
        {"id": (1, "Python"), "out": {"result": "ok"}, "error": None},
        {"id": (2, "Java"), "out": None, "error": "timeout"},  # 失败
        {"id": (3, "C++"), "out": {"result": "ok"}, "error": None},
    ]
    
    def get_write_id(r: dict) -> str:
        return f"{r['id'][0]}_{r['id'][1]}"
    
    def is_good(r: dict) -> bool:
        return r.get("error") is None
    
    marked, failed = checkpoint.update("path_A", write_records, is_good, get_write_id)
    print(f"成功: {marked} 条, 失败: {failed} 条")
    
    checkpoint.save()
    print(f"All IDs: {checkpoint.state.all_ids}\n")

    # 3. 重新加载并测试
    print("=== Run #2 (reload) ===")
    checkpoint2 = FileCheckpoint[dict, str](file_path=ckpt_path)

    read_records2 = [
        {"page_id": 1, "title": "Python"},  # 已处理
        {"page_id": 2, "title": "Java"},    # 之前失败
        {"page_id": 4, "title": "Go"},      # 新数据
    ]
    
    to_process, skipped = checkpoint2.filter(read_records2, get_read_id)
    print(f"待处理: {[get_read_id(r) for r in to_process]}")
    print(f"跳过: {skipped} 条")
