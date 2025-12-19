from pathlib import Path
from typing import Any, Dict, List
import json
import yaml


import re
from typing import Literal

from opencc import OpenCC

from cetc_product.data_model.entity import LanguageEnum

_cc_s2t = OpenCC("s2t")
_cc_t2s = OpenCC("t2s")
_re_cjk = re.compile(r"[\u4e00-\u9fff]")
_re_alpha = re.compile(r"[A-Za-z]")



def detect_lang_simple(text: str, trad_ratio_threshold: float = 0.6) -> LanguageEnum | None:
    """
    判定文本主要语言：
    - LanguageEnum.EN      : 英文（只含字母，无中文）
    - LanguageEnum.ZH_HANS : 简体中文为主
    - LanguageEnum.ZH_HANT : 繁体中文为主
    - None                 : 无法判断（纯符号/数字/空）

    规则说明：
    - 有中文时，通过 OpenCC 将每个汉字映射为“简体特征字/繁体特征字”计数，
      计算 trad_ratio = trad_count / (simp_count + trad_count)
    - 若 trad_ratio >= trad_ratio_threshold -> ZH_HANT，否则 -> ZH_HANS
    - 若没有任何可区分的特征字（total == 0），按业务约定默认归为 ZH_HANS
    """
    text = text.strip()
    if not text:
        return None

    # 无中文：区分英文与其他
    if not _re_cjk.search(text):
        return LanguageEnum.EN if _re_alpha.search(text) else None

    # 有中文：统计简体/繁体“特征字”数量
    to_trad = _cc_s2t.convert(text)
    to_simp = _cc_t2s.convert(text)

    simp_count = 0
    trad_count = 0

    for o, t, s in zip(text, to_trad, to_simp):
        # 只考虑基本汉字区间
        if not ("\u4e00" <= o <= "\u9fff"):
            continue

        if o == s and o != t:
            simp_count += 1
        elif o == t and o != s:
            trad_count += 1
        # 两边都一样（简繁同形字）不计入统计

    total = simp_count + trad_count
    if total == 0:
        # 没有可区分的简繁特征字，按约定默认简体
        return LanguageEnum.ZH_HANS

    trad_ratio = trad_count / total
    if trad_ratio >= trad_ratio_threshold:
        return LanguageEnum.ZH_HANT
    return LanguageEnum.ZH_HANS



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
        return json.dumps(d, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
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
