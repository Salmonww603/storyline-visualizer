"""
Pydantic 模型：定义 API 的请求/响应数据格式。
FastAPI 会自动校验请求体，不符合格式就返回 422 错误。
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ===== 认证相关 =====
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型直接转换


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ===== 事件相关 =====
class EventBase(BaseModel):
    event_date: str = ""
    title: str
    description: str = ""
    people: str = "A"
    tags: List[str] = []
    image_url: str = ""


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    """更新事件：所有字段可选，只更新传进来的"""
    event_date: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    people: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None


class EventOut(EventBase):
    id: int
    sort_order: int = 0

    class Config:
        from_attributes = True


# ===== 故事线相关 =====
class StorylineBase(BaseModel):
    title: str
    description: str = ""
    person_a: str = ""
    person_b: str = ""
    is_public: bool = False


class StorylineCreate(StorylineBase):
    pass


class StorylineUpdate(BaseModel):
    """更新故事线：所有字段可选"""
    title: Optional[str] = None
    description: Optional[str] = None
    person_a: Optional[str] = None
    person_b: Optional[str] = None
    is_public: Optional[bool] = None


class StorylineOut(StorylineBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    events: List[EventOut] = []

    class Config:
        from_attributes = True


class StorylineSummary(BaseModel):
    """发现页用的精简版（不含事件列表，列表页更轻量）"""
    id: int
    title: str
    description: str = ""
    person_a: str = ""
    person_b: str = ""
    owner_id: int
    event_count: int = 0

    class Config:
        from_attributes = True
