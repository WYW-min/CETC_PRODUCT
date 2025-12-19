
from typing import List
from pydantic import BaseModel, Field

from cetc_product.data_model.entity import EnhanceDomainEnum


class EnhancedDomain(BaseModel):
    """定义所有需要增强的领域信息的数据基础模型"""
    domains: List[EnhanceDomainEnum] | None = Field(None, description="涉及的领域名称")
    why: str | None = Field(None, description="简要说明领域归类理由，如“- 描述信息中明确说明... \n- 根据已有知识表明...\n...”")

