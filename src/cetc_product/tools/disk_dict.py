import sqlite3
import json
import atexit
import weakref
from pathlib import Path
from typing import Hashable, Tuple, Union, Any, Iterator
from collections.abc import MutableMapping

Key = Union[Hashable, Tuple[Hashable, ...]]


class DiskDict(MutableMapping):
    """基于 SQLite 的持久化字典，完整实现 dict 接口"""

    _instances: list = []  # 跟踪所有实例

    def __init__(self, db_path: Path, table: str = "kvdict"):
        self.db_path = Path(db_path)
        self.table = table
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                k TEXT PRIMARY KEY,
                v BLOB
            )
        """)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.commit()

        # 注册到全局列表，用于退出时清理
        DiskDict._instances.append(weakref.ref(self))

    # -------- 上下文管理器 --------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._safe_close()
        return False

    def _safe_close(self):
        """安全关闭，确保 WAL 合并"""
        if self._conn:
            try:
                self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                self._conn.commit()
            except Exception:
                pass
            finally:
                self._conn.close()
                self._conn = None

    def close(self):
        self._safe_close()

    # -------- key/value 编码 --------

    @staticmethod
    def _normalize_key(key: Key) -> Tuple[Hashable, ...]:
        return key if isinstance(key, tuple) else (key,)

    @staticmethod
    def _encode_key(key: Tuple[Hashable, ...]) -> str:
        return json.dumps(key, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _decode_key(s: str) -> Tuple[Hashable, ...]:
        return tuple(json.loads(s))

    @staticmethod
    def _encode_value(value: Any) -> bytes:
        return json.dumps(value, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def _decode_value(data: bytes) -> Any:
        return json.loads(data.decode("utf-8"))

    # -------- MutableMapping 必须实现的 5 个方法 --------

    def __getitem__(self, key: Key) -> Any:
        ks = self._encode_key(self._normalize_key(key))
        cur = self._conn.execute(
            f"SELECT v FROM {self.table} WHERE k = ? LIMIT 1", (ks,)
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError(key)
        return self._decode_value(row[0])

    def __setitem__(self, key: Key, value: Any):
        ks = self._encode_key(self._normalize_key(key))
        vs = self._encode_value(value)
        self._conn.execute(
            f"INSERT OR REPLACE INTO {self.table} (k, v) VALUES (?, ?)", (ks, vs)
        )
        self._conn.commit()

    def __delitem__(self, key: Key):
        ks = self._encode_key(self._normalize_key(key))
        cur = self._conn.execute(f"DELETE FROM {self.table} WHERE k = ?", (ks,))
        self._conn.commit()
        if cur.rowcount == 0:
            raise KeyError(key)

    def __iter__(self) -> Iterator[Tuple[Hashable, ...]]:
        cur = self._conn.execute(f"SELECT k FROM {self.table}")
        for (ks,) in cur:
            yield self._decode_key(ks)

    def __len__(self) -> int:
        cur = self._conn.execute(f"SELECT COUNT(*) FROM {self.table}")
        return cur.fetchone()[0]

    # -------- 可选：批量优化 --------

    def batch_update(self, items, batch_size: int = 10_000):
        """批量写入优化"""
        if isinstance(items, dict):
            items = items.items()
        buf = []
        for key, value in items:
            ks = self._encode_key(self._normalize_key(key))
            vs = self._encode_value(value)
            buf.append((ks, vs))
            if len(buf) >= batch_size:
                self._conn.executemany(
                    f"INSERT OR REPLACE INTO {self.table} (k, v) VALUES (?, ?)", buf
                )
                self._conn.commit()
                buf.clear()
        if buf:
            self._conn.executemany(
                f"INSERT OR REPLACE INTO {self.table} (k, v) VALUES (?, ?)", buf
            )
            self._conn.commit()

    def __del__(self):
        try:
            self._safe_close()
        except Exception:
            pass


@atexit.register
def _cleanup_all_diskdicts():
    """程序退出时关闭所有 DiskDict 实例"""
    for ref in DiskDict._instances:
        instance = ref()
        if instance is not None:
            try:
                instance._safe_close()
            except Exception:
                pass


# 示例用法
if __name__ == "__main__":
    db_path = Path("./wiki_info.db")
    with DiskDict(db_path) as dd:
        print(dd[("enwiki", "1625")])