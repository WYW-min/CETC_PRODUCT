from typing import Dict


class RunStats:
    """运行统计信息"""
    
    def __init__(self):
        self.processed = 0
        self.failed = 0
        self.skipped = 0
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "processed": self.processed,
            "failed": self.failed,
            "skipped": self.skipped,
        }