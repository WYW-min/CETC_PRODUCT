from typing import List
from pydantic import BaseModel, Field

from cetc_product.data_model.entity import EnhanceDomainEnum


class Location(BaseModel):
    """结构化的地理位置信息"""

    country: str | None = Field(None, description="国家")
    region: str | None = Field(None, description="地区、省份或州")
    city: str | None = Field(None, description="城市")
    street_address: str | None = Field(None, description="街道、详细地址")


class Person(BaseModel):
    """结构化的人物信息"""

    name: str = Field(..., description="人物姓名")
    role: str | None = Field(None, description="在组织中的角色或职务")


class BaseEntities(BaseModel):
    """定义所有需要抽取的实体类型的基础模型"""

    name: str = Field(..., description="机构名称")
    domains: List[EnhanceDomainEnum] | None = Field(None, description="所属领域或行业")
    alias: List[str] | None = Field(None, description="机构别名")
    persons: List[Person] | None = Field(None, description="与该组织相关的人员信息")
    locations: List[Location] | None = Field(None, description="地理位置")
    abbreviations: List[str] | None = Field(None, description="缩略语")
    parent_org: List[str] | None = Field(None, description="上级机构")
    emails: List[str] | None = Field(None, description="电子邮箱")
    ip_addresses: List[str] | None = Field(None, description="IP地址")
    vulnerability_ids: List[str] | None = Field(None, description="漏洞编号 (CVE)")
    phone_numbers: List[str] | None = Field(None, description="电话号码")
    usernames: List[str] | None = Field(None, description="用户名")
    urls: List[str] | None = Field(None, description="URL链接")


class OrganizationInfos(BaseModel):
    """
    从维基百科页面中抽取的、高度结构化的机构信息实体。
    包含最终的合并视图及抽取理由。
    """

    consolidated_view: List[BaseEntities] | None = Field(
        None,
        description="所有来源抽取结果的合并与去重视图。 为 False，此字段应为 null。",
    )
    why: str | None = Field(
        ...,
        description="简要说明为何该条目被判断为具体的组织实体，或为何不被认为是具体的组织实体。",
    )
