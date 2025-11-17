from typing import List
from pydantic import BaseModel, Field

class Location(BaseModel):
    """结构化的地理位置信息"""
    country: str | None = Field(None, description="国家")
    region: str | None = Field(None, description="地区、省份或州")
    city: str | None = Field(None, description="城市")
    postal_code: str | None = Field(None, description="邮政编码")
    full_address: str | None = Field(None, description="完整的原始地址文本")
    timezone: str | None = Field(None, description="时区")

class Measurement(BaseModel):
    """用于表示带有单位的测量值"""
    value: float | None = Field(None, description="数值")
    unit: str | None = Field(None, description="单位 (例如: 'cm', 'kg')")

class EducationRecord(BaseModel):
    """单条教育经历记录"""
    institution: str | None = Field(None, description="毕业院校或教育机构名称")
    degree: str | None = Field(None, description="获得的学位")
    major: str | None = Field(None, description="主修专业")

class SocialMediaAccount(BaseModel):
    """社交媒体账号信息"""
    platform: str | None = Field(None, description="平台名称")
    username_or_id: str | None = Field(None, description="用户名或ID")
    url: str | None = Field(None, description="个人主页URL")

class EmergencyContact(BaseModel):
    """紧急联系人信息"""
    name: str | None = Field(None, description="联系人姓名")
    relationship: str | None = Field(None, description="与本人的关系")
    phone_number: str | None = Field(None, description="联系人电话")

# --- 2. 按逻辑分组的属性模型 ---

class CoreIdentity(BaseModel):
    """核心身份信息"""
    full_name: str | None = Field(None, description="姓名")
    gender: str | None = Field(None, description="性别")
    age: int | None = Field(None, description="年龄")
    birth_date: str | None = Field(None, description="出生日期")
    nationality: str | None = Field(None, description="国籍")
    ethnicity: str | None = Field(None, description="民族")
    race: str | None = Field(None, description="人种/种族")
    id_card_number: str | None = Field(None, description="身份证号")

class PhysicalAttributes(BaseModel):
    """物理特征"""
    height: Measurement | None = Field(None, description="身高")
    weight: Measurement | None = Field(None, description="体重")
    blood_type: str | None = Field(None, description="血型")
    skin_color: str | None = Field(None, description="肤色")
    hair_color: str | None = Field(None, description="发色")
    eye_color: str | None = Field(None, description="瞳色")
    handedness: str | None = Field(None, description="惯用手")

class FamilyAndRelationships(BaseModel):
    """家庭与社会关系"""
    marital_status: str | None = Field(None, description="婚姻状况")
    spouse_name: str | None = Field(None, description="配偶姓名")
    number_of_children: int | None = Field(None, description="子女数量")
    family_population: int | None = Field(None, description="家庭人口")

class EducationAndCareer(BaseModel):
    """教育与职业"""
    education_history: List[EducationRecord] = Field(default_factory=list, description="学历、毕业院校、专业、学位")
    occupation: str | None = Field(None, description="职业")
    employer: str | None = Field(None, description="工作单位/公司")
    position: str | None = Field(None, description="职位/职称")
    work_years: Measurement | None = Field(None, description="工作年限")
    industry: str | None = Field(None, description="行业")
    language_skills: List[str] = Field(default_factory=list, description="语言能力")

class HealthAndLifestyle(BaseModel):
    """健康与生活方式 (高度敏感)"""
    health_status: str | None = Field(None, description="健康状况")
    allergy_history: List[str] = Field(default_factory=list, description="过敏史")
    medical_history: List[str] = Field(default_factory=list, description="病史")
    disability_status: str | None = Field(None, description="残疾状况")
    smoking_status: str | None = Field(None, description="吸烟状况")
    drinking_habits: str | None = Field(None, description="饮酒习惯")
    dietary_preferences: List[str] = Field(default_factory=list, description="饮食偏好")
    exercise_frequency: str | None = Field(None, description="锻炼频率")
    sleep_duration: Measurement | None = Field(None, description="睡眠时长 (单位: 小时)")
    medical_insurance_type: str | None = Field(None, description="医疗保险类型")

class FinancialProfile(BaseModel):
    """财务状况 (高度敏感)"""
    annual_income: Measurement | None = Field(None, description="年收入")
    primary_income_source: str | None = Field(None, description="主要收入来源")
    housing_situation: str | None = Field(None, description="住房情况")
    property_count: int | None = Field(None, description="房产数量")
    vehicle_ownership: List[str] = Field(default_factory=list, description="车辆拥有情况")
    bank_deposits: Measurement | None = Field(None, description="银行存款")
    liabilities: Measurement | None = Field(None, description="负债情况")
    credit_score: int | None = Field(None, description="信用评分")
    investment_preferences: List[str] = Field(default_factory=list, description="投资偏好")
    consumption_level: str | None = Field(None, description="消费水平")

class PersonalInterests(BaseModel):
    """个人兴趣与偏好"""
    hobbies: List[str] = Field(default_factory=list, description="兴趣爱好")
    political_inclination: str | None = Field(None, description="政治倾向")
    shopping_preferences: List[str] = Field(default_factory=list, description="购物偏好")
    media_consumption_habits: List[str] = Field(default_factory=list, description="媒体消费习惯")
    travel_preferences: List[str] = Field(default_factory=list, description="旅游偏好")
    pet_ownership: List[str] = Field(default_factory=list, description="宠物拥有情况")
    transportation_preferences: List[str] = Field(default_factory=list, description="交通方式偏好")
    reading_preferences: List[str] = Field(default_factory=list, description="阅读偏好")
    religious_belief: str | None = Field(None, description="宗教信仰")

class DigitalFootprint(BaseModel):
    """数字足迹 (高度敏感)"""
    email_address: str | None = Field(None, description="电子邮箱地址")
    phone_number: str | None = Field(None, description="手机号码")
    social_media_accounts: List[SocialMediaAccount] = Field(default_factory=list, description="社交媒体账号")
    ip_address: str | None = Field(None, description="IP地址")
    device_id: str | None = Field(None, description="设备ID")
    browsing_history: List[str] = Field(default_factory=list, description="网络浏览历史")
    search_history: List[str] = Field(default_factory=list, description="搜索记录")
    location_data: List[str] = Field(default_factory=list, description="位置数据")
    online_purchase_history: List[str] = Field(default_factory=list, description="在线购买记录")
    virtual_avatar: str | None = Field(None, description="虚拟形象/头像")

class GeographicInformation(BaseModel):
    """地理位置信息"""
    residential_address: Location | None = Field(None, description="居住地址")
    birth_place: Location | None = Field(None, description="出生地")
    household_registration_location: Location | None = Field(None, description="户籍所在地")
    work_address: Location | None = Field(None, description="工作地址")
    residence_country: str | None = Field(None, description="居住国")
    residence_city_type: str | None = Field(None, description="居住城市类型")
    commute_distance: Measurement | None = Field(None, description="通勤距离")
    emergency_contact: EmergencyContact | None = Field(None, description="紧急联系人信息")

class PersonAttributes(BaseModel):
    """包含所有个人属性的聚合模型"""
    identity: CoreIdentity | None = None
    physical: PhysicalAttributes | None = None
    family: FamilyAndRelationships | None = None
    career: EducationAndCareer | None = None
    health: HealthAndLifestyle | None = None
    financial: FinancialProfile | None = None
    interests: PersonalInterests | None = None
    digital: DigitalFootprint | None = None
    geographic: GeographicInformation | None = None

# --- 3. 最终的顶层输出模型 ---
class PersonInfo(BaseModel):
    """从维基百科页面中尽力抽取的、详尽的个人信息范式模型。"""
    consolidated_view: PersonAttributes | None = Field(None, description="所有来源抽取结果的合并与去重视图，若无有效信息或并非一个真实的人物则为null。")
    why: str | None = Field(None, description="简要说明抽取信息，如“输入并非一个真实的人物”。")