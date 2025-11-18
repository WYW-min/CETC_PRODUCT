from cetc_product.tools.tiny_tool import safe_get

class Funcs:
    @staticmethod
    def simple_dict_getid(r: dict) -> str:
        """从处理结果中提取 ID（兼容 tuple 和 list）
        
        Examples:
            {"id": [43198295, "Akhouri Sinha"]} -> "43198295_Akhouri Sinha"
            {"id": (43198295, "Akhouri Sinha")} -> "43198295_Akhouri Sinha"  ✅ 兼容
        """
        id_value = safe_get(r, ["id"])
        if isinstance(id_value, (list, tuple)):
            return "_".join(map(str, id_value))  # ✅ tuple 和 list 都转换为字符串
        return str(id_value)
    
    @staticmethod
    def wiki_dict_getid(r: dict) -> str:
        """从原始 wiki 数据中提取 ID（返回字符串）
        
        Examples:
            {"page_id": 123, "title": "Python"} -> "123_Python"
        """
        page_id = r.get("page_id")
        title = r.get("title", "")
        return f"{page_id}_{title}"
    
    @staticmethod
    def simple_dict_good(r: dict) -> bool:
        """判断处理结果是否成功"""
        return not safe_get(r, ["out", "error"])