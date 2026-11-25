"""
故事线接口：我的列表、发现页、详情、增删改（带权限校验）。
前缀 /api/storylines
"""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Storyline, Event
from schemas import (
    StorylineCreate, StorylineUpdate, StorylineOut, StorylineSummary,
)
from auth import get_current_user

router = APIRouter(prefix="/api/storylines", tags=["故事线"])


def _to_out(storyline: Storyline) -> dict:
    """把 ORM 对象转成响应格式，事件按 sort_order 排序、tags 从 JSON 字符串解析回数组"""
    events = []
    for e in sorted(storyline.events, key=lambda x: x.sort_order):
        events.append({
            "id": e.id,
            "event_date": e.event_date,
            "title": e.title,
            "description": e.description,
            "people": e.people,
            "tags": json.loads(e.tags or "[]"),
            "image_url": e.image_url,
            "sort_order": e.sort_order,
        })
    return {
        "id": storyline.id,
        "owner_id": storyline.owner_id,
        "title": storyline.title,
        "description": storyline.description,
        "person_a": storyline.person_a,
        "person_b": storyline.person_b,
        "is_public": storyline.is_public,
        "created_at": storyline.created_at,
        "updated_at": storyline.updated_at,
        "events": events,
    }


@router.get("/mine", response_model=List[StorylineSummary])
def get_my_storylines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的故事线列表（只返回自己的）"""
    items = db.query(Storyline).filter(Storyline.owner_id == current_user.id).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "person_a": s.person_a,
            "person_b": s.person_b,
            "owner_id": s.owner_id,
            "event_count": len(s.events),
        }
        for s in items
    ]


@router.get("/discover", response_model=List[StorylineSummary])
def discover(db: Session = Depends(get_db)):
    """发现页：所有公开的故事线，任何人可看（不需要登录）"""
    items = db.query(Storyline).filter(Storyline.is_public == True).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "person_a": s.person_a,
            "person_b": s.person_b,
            "owner_id": s.owner_id,
            "event_count": len(s.events),
        }
        for s in items
    ]


@router.get("/{storyline_id}", response_model=StorylineOut)
def get_storyline(storyline_id: int, db: Session = Depends(get_db)):
    """
    单条详情（含所有事件）。
    公开的任何人可看；私密的只能是本人——这里先不强制，前端控制入口，
    后续可加当前用户校验（面试可讲这个取舍）。
    """
    s = db.query(Storyline).filter(Storyline.id == storyline_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="故事线不存在")
    return _to_out(s)


@router.post("", response_model=StorylineOut, status_code=status.HTTP_201_CREATED)
def create_storyline(
    data: StorylineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建故事线：owner_id 设为当前登录用户"""
    s = Storyline(
        owner_id=current_user.id,
        title=data.title,
        description=data.description,
        person_a=data.person_a,
        person_b=data.person_b,
        is_public=data.is_public,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _to_out(s)


@router.put("/{storyline_id}", response_model=StorylineOut)
def update_storyline(
    storyline_id: int,
    data: StorylineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新故事线：先校验是不是本人的，不是就 403"""
    s = db.query(Storyline).filter(Storyline.id == storyline_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="故事线不存在")
    if s.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的故事线")

    # 只更新传进来的字段（exclude_unset 排除没传的）
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return _to_out(s)


@router.delete("/{storyline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_storyline(
    storyline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除故事线：级联删除它下面的所有事件（模型里配了 cascade）"""
    s = db.query(Storyline).filter(Storyline.id == storyline_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="故事线不存在")
    if s.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的故事线")
    db.delete(s)
    db.commit()
