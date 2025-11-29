from pathlib import Path
from typing import Any, Dict, List
import json
import yaml


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        # 可以添加更多类型的转换
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def safe_get(d: dict, keys: list, default=None):
    """Safely get a nested value from a dictionary."""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d.get(key, default)
        else:
            return default
    return d


def pretty_dict(d: Dict[str, Any], mode="json") -> str:
    if mode == "json":
        return json.dumps(d, ensure_ascii=True, indent=2, cls=CustomJSONEncoder)
    elif mode == "yaml":
        return yaml.safe_dump(d, allow_unicode=True, sort_keys=False)


def check_path(path: Path) -> bool:
    try:
        return path.exists()
    except:
        return False


from wcmatch import glob


def get_globpath(path: Path, enhance=True) -> List[Path]:

    if not enhance:
        return [p for p in path.parent.glob(path.name)]
    else:
        return [Path(p) for p in glob.iglob(str(path), flags=glob.BRACE)]
