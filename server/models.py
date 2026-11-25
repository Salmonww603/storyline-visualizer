"""
数据模型：用 Python 类表示数据库表（ORM）。
一个类 = 一张表，一个类的实例 = 表里的一行，类属性 = 字段。
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 关系：一个用户有多条故事线（反向引用，方便 user.storylines 这样访问）
    storylines = relationship("Storyline", back_populates="owner", cascade="all, delete-orphan")


class Storyline(Base):
    """故事线表"""
    __tablename__ = "storylines"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    person_a = Column(String(100), default="")
    person_b = Column(String(100), default="")
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系：故事线属于一个用户，且有多个事件
    owner = relationship("User", back_populates="storylines")
    events = relationship("Event", back_populates="storyline", cascade="all, delete-orphan")


class Event(Base):
    """事件表"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    storyline_id = Column(Integer, ForeignKey("storylines.id"), nullable=False)
    event_date = Column(String(50), default="")   # 用字符串，兼容"2021年春"这种非标准日期
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    people = Column(String(50), default="A")      # 'A' / 'B' / 'AB'
    tags = Column(Text, default="[]")             # JSON 字符串，如 ["开端","名场面"]
    image_url = Column(String(500), default="")
    sort_order = Column(Integer, default=0)

    # 关系：事件属于一条故事线
    storyline = relationship("Storyline", back_populates="events")
