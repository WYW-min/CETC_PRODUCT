from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ======================
# 一、元信息（meta）
# ======================


class Language(str, Enum):
    zh_cn = "zh-CN"
    zh_tw = "zh-TW"
    en = "en"
    other = "other"


class Meta(BaseModel):
    source_platform: str = Field(
        ...,
        description=(
            "数据来源平台名称，如 Facebook、Twitter、LinkedIn、Strava、"
            "Instagram、Quora、Reddit、VK、Indeed、Airbnb、Yelp、Myspace、Discord、Nextdoor、Spotify 等。"
            "用于后续统计是否覆盖不少于 8 种平台以及必选平台（Facebook、Twitter、LinkedIn、Strava）。"
        ),
    )
    language: Language = Field(
        ...,
        description=(
            "文本语种，用于满足“语种覆盖中文简体、英文、中文繁体”的场景要求。"
            "常用取值：zh-CN（简体中文）、zh-TW（繁体中文）、en（英文）。"
        ),
    )
    download_time: Optional[str] = Field(
        None,
        description=("下载时间"),
    )
    source_url: Optional[str] = Field(
        None,
        description="原始帖文或页面的 URL，用于追溯数据来源（可选）。",
    )


# ======================
# 二、人员信息（persons）
# ======================


class PersonType(str, Enum):
    soldier = "军人"
    politician = "政治人物"
    opinion_leader = "意见领袖"
    government_official = "政府官员"
    security_staff = "安全/情报相关人员"
    entrepreneur = "企业家/高管"
    academic = "学者/研究人员"
    journalist = "记者/媒体人"
    influencer = "网络红人/KOL"
    ordinary_user = "普通用户"
    other = "其他"


class SocialAccount(BaseModel):
    """
    统一表示一个社交账号，可用于“本人名下账号”
    也可用于“关注/被关注的其他账号（信息不全时可以只填部分字段）”。
    """

    platform: Optional[str] = Field(
        None,
        description=(
            "账号所属平台，如 Facebook、Twitter、LinkedIn、Strava、Instagram 等。"
        ),
    )
    handle: Optional[str] = Field(
        None,
        description=("账号标识，如 @handle、用户名或用户 ID。"),
    )
    profile_url: Optional[str] = Field(
        None,
        description="账号主页链接（如能从文本中解析到）。",
    )
    note: Optional[str] = Field(
        None,
        description=(
            "关于该账号的补充描述，如“上文提到的某部队官微”或“疑似军队单位账号”等。"
        ),
    )


class PersonAttributes(BaseModel):
    """
    人员属性信息，覆盖要求中的“人员属性不少于 13 种”。
    """

    name: Optional[str] = Field(None, description="姓名，如文本中未出现则为 null。")
    nickname: Optional[str] = Field(None, description="昵称或网名，如社交平台显示名。")
    gender: Optional[str] = Field(
        None,
        description="性别，如 male/female/unknown，或原文中出现的性别描述。",
    )
    birthday: Optional[str] = Field(
        None,
        description="生日字符串，建议使用 'YYYY-MM-DD' 格式，原文有提及即可记录。",
    )
    id_document: Optional[str] = Field(
        None,
        description="证件信息，如护照号、军官证号、身份证号等敏感标识（若文本中明确出现）。",
    )
    social_accounts: List[SocialAccount] = Field(
        default_factory=list,
        description="该人物本人名下的社交账号列表（用于“社交账号”属性）。",
    )
    emails: List[str] = Field(
        default_factory=list,
        description="电子邮箱列表。",
    )
    phones: List[str] = Field(
        default_factory=list,
        description="联系电话列表。",
    )
    addresses: List[str] = Field(
        default_factory=list,
        description="住址或联系地址列表。",
    )
    employers: List[str] = Field(
        default_factory=list,
        description="工作单位名称列表，对应“工作单位”属性。",
    )
    job_titles: List[str] = Field(
        default_factory=list,
        description="岗位职务列表，如“情报分析员”“营长”等。",
    )
    work_time: Optional[str] = Field(
        None,
        description="工作时间或任职时间，如“2019-2023 在某防务公司任职”。",
    )
    events: List[str] = Field(
        default_factory=list,
        description="与该人物相关的重要事件描述，如“参加某军演”“在推特上发表某政治言论”。",
    )
    locations: List[str] = Field(
        default_factory=list,
        description="与人物相关的地理位置信息，如居住城市、出行地点，满足“地理位置信息”类别。",
    )
    devices: List[str] = Field(
        default_factory=list,
        description="与人物相关的设备信息，如“iPhone 15 Pro”“Garmin 跑表”等。",
    )  # 设备信息
    network_assets: List[str] = Field(
        default_factory=list,
        description="与人物关联的网络资产，如个人网站、博客、服务器域名等。",
    )


class Person(BaseModel):
    """
    人员实体：每个 person 需要包含：
    - person_type：人员类型（军人、政治人物、意见领袖等），用于满足“人员类型不少于 10 类”的统计要求；
    - is_target：是否为目标人物；
    - following_accounts：该人物关注的账号；
    - followed_by_accounts：关注该人物（或其账号）的账号；
    以及人员基础属性（姓名、昵称、性别、生日、工作单位等）。
    """

    person_id: str = Field(
        ...,
        description="人物在本条样本中的唯一 ID，如 P1、P2 等，用于关系引用。",
    )
    person_type: PersonType = Field(
        ...,
        description=(
            "人员类型标签，用于区分军人、政治人物、意见领袖等。"
            "有助于满足场景要求中“社交媒体关注的人员类型不少于 10 类”的指标。"
        ),
    )
    attributes: PersonAttributes = Field(
        default_factory=PersonAttributes,
        description="该人物的基础属性信息集合，覆盖姓名、昵称、性别、生日、社交账号等 13 类以上属性。",
    )

    owned_accounts: List[SocialAccount] = Field(
        default_factory=list,
        description=(
            "该人物名下的账号（冗余于 attributes.social_accounts，但更强调“归属关系”）。"
            "用于后续建立账号层面的关注关系。"
        ),
    )  # 网络账户信息
    following_accounts: List[SocialAccount] = Field(
        default_factory=list,
        description=(
            "该人物“关注的账号”列表，即他/她 follow 的对象账户，可以是个人账号或机构账号。"
            "用于满足新增字段“关注的账号”要求。"
        ),
    )
    followed_by_accounts: List[SocialAccount] = Field(
        default_factory=list,
        description=(
            "“关注该人物（或其账号）的账号”列表，即粉丝/关注者。"
            "用于满足新增字段“被关注的账号”要求。"
        ),
    )


# ======================
# 三、组织信息（organizations）
# ======================


class OrganizationAttributes(BaseModel):
    """
    组织/机构属性，覆盖“机构信息不少于 7 种”要求。
    """

    name: Optional[str] = Field(
        None,
        description="机构名称，如部队番号、政府机构名称、公司名称等。",
    )
    industry: Optional[str] = Field(
        None,
        description="行业类别，如 military、government、it、education 等。",
    )
    website: Optional[str] = Field(
        None,
        description="机构官方网址 URL。",
    )
    social_accounts: List[SocialAccount] = Field(
        default_factory=list,
        description="机构官方社交账号列表，如官微、官方推特账号等。",
    )
    phones: List[str] = Field(
        default_factory=list,
        description="机构联系电话列表。",
    )
    contacts: List[str] = Field(
        default_factory=list,
        description="机构相关联系人姓名，可与 persons.person_id 逻辑对应。",
    )
    locations: List[str] = Field(
        default_factory=list,
        description="机构所在的地理位置，如国家、城市、详细地址等。",
    )
    network_assets: List[str] = Field(
        default_factory=list,
        description="机构关联的网络资产，如官网域名、服务器、IP 地址等。",
    )


class Organization(BaseModel):
    """
    组织实体：包含机构属性以及可选的组织类型、与目标人物的关系等。
    """

    org_id: str = Field(
        ...,
        description="机构在本条样本中的唯一 ID，如 O1、O2，用于与人员建立关系。",
    )
    org_type: Optional[str] = Field(
        None,
        description="机构类型，如军队单位、政府部门、防务企业、社交平台公司等（可选）。",
    )
    attributes: OrganizationAttributes = Field(
        default_factory=OrganizationAttributes,
        description="机构的详细属性信息，涵盖名称、行业类别、官网、社交账号、联系电话、联系人员、地理位置等。",
    )


# ======================
# 四、顶层样本结构：只暴露 meta / persons / organizations
# ======================


class ExtractionSample(BaseModel):
    """
    单条社交媒体文本的标注结果，用于训练网络安全领域行为体信息抽取模型。
    顶层仅包含三个字段：
    - meta：元信息
    - persons：人员信息（含目标人物标记、人员类型、关注/被关注账号等）
    - organizations：组织/机构信息
    """

    # meta: Meta = Field(
    #     ...,
    #     description=(
    #         "样本元信息，包括来源平台、语言、时间等，用于满足平台覆盖、语种覆盖、近 6 个月等数据级要求。"
    #     ),
    # )

    persons: List[Person] | None = Field(
        None,
        description=(
            "文本中出现的所有人物实体列表。"
            "每个 person 必须包含人员类型（person_type）、目标人物标记（is_target）、"
            "以及关注与被关注账号（following_accounts、followed_by_accounts）。"
        ),
    )
    organizations: List[Organization] | None = Field(
        None,
        description=(
            "文本中出现的所有组织/机构实体列表，包含机构名称、行业类别、官网、社交账号、联系电话、"
            "联系人员、地理位置等信息。"
        ),
    )
