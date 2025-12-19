from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class LanguageEnum(str, Enum):
    EN = "英文"
    ZH_HANS = "简体中文"
    ZH_HANT = "繁体中文"
    


class EnhanceDomainEnum(str, Enum):
    MILITARY = "军事"
    FINANCE = "金融"
    ELECTRIC_POWER = "电力"
    TELECOMMUNICATION = "电信"
    TRANSPORTATION = "交通"
    ENERGY = "能源"
    
    
class EntityType(str, Enum):
    PERSON = "人物"
    ORGANIZATION = "组织"
    EVENT = "事件"
    WORK = "作品"
    PLACE = "地点"
    CONCEPT = "概念"
    OBJECT = "物品"
    SPECIES = "生物物种"
    PHENOMENON = "现象"
    LANGUAGE = "语言"
    DISEASE = "疾病"
    CHEMICAL = "化学物质"
    FOOD = "食物"
    SPORT = "体育运动"
    AWARD = "奖项"
    LAW = "法律法规"
    THEORY = "理论学说"
    METHOD = "技术方法"
    OTHER = "其他"
    
class PersonSubtype(str, Enum):
    REAL = "现实人物"
    FICTIONAL = "虚构人物"
    
class OrganizationSubtype(str, Enum):
    GOVERNMENT_AGENCY = "政府机构"
    MILITARY = "军事组织"
    COMPANY = "公司企业"
    NGO = "非政府组织"
    UNIVERSITY = "大学院校"
    PARTY = "政党"
    MEDIA = "媒体机构"
    OTHER = "其他"


class DomainEnum(str, Enum):
    POLITICAL_AND_PUBLIC_AFFAIRS = "政治与公共事务"
    SCIENCE_AND_RESEARCH = "科学与研究"
    ENGINEERING_AND_TECHNOLOGY = "工程与技术"
    EDUCATION_AND_ACADEMICS = "教育与学术"
    BUSINESS_AND_ECONOMICS = "商业与经济"
    FINANCE_AND_INVESTMENT = "金融与投资"
    LAW_AND_JUDICIARY = "法律与司法"
    MEDICAL_AND_HEALTH = "医疗与健康"
    ART_AND_LITERATURE = "艺术与文学"
    PERFORMING_ARTS = "表演艺术"
    ENTERTAINMENT_AND_MEDIA = "娱乐与媒体"
    SPORTS_AND_COMPETITION = "体育与竞技"
    MILITARY_AND_SECURITY = "军事与安全"
    SOCIAL_WELFARE_AND_DEVELOPMENT = "社会公益与发展"
    RELIGION_AND_SPIRITUALITY = "宗教与精神"
    LIFESTYLE_AND_CULTURE = "生活方式与文化"
    OTHERS = "其他"
    
    @classmethod
    def get_target_domains(cls) -> List[str]:
        return [cls.POLITICAL_AND_PUBLIC_AFFAIRS, cls.SCIENCE_AND_RESEARCH, cls.ENGINEERING_AND_TECHNOLOGY, cls.FINANCE_AND_INVESTMENT, cls.LAW_AND_JUDICIARY, cls.MILITARY_AND_SECURITY]
    


class RegionEnum(str, Enum):
    US = "美国"
    CN = "中国大陆"
    TW = "中国台湾"
    EU = "欧洲"
    SEA = "东南亚"
    JP = "日本"
    KR = "韩国"
    OTHERS = "其他"
    
    @classmethod
    def get_target_regions(cls) -> List[str]:
        return [cls.TW, cls.US, cls.EU]
    
    





