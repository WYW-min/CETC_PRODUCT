from typing import Any, Dict
import json
import yaml
def safe_get(d: dict, keys: list, default=None):
    """Safely get a nested value from a dictionary."""
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d.get(key, default)
        else:
            return default
    return d

def pretty_dict(d:Dict[str,Any], mode = "json")->str:
    if mode == "json":
        return json.dumps(d, ensure_ascii=True, indent=2)
    elif mode == "yaml":
        return yaml.safe_dump(d, allow_unicode=True, sort_keys=False )
    