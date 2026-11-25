"""
事件接口：添加、更新、删除。
前缀 /api/events
权限逻辑：事件本身没有 owner，通过它所属的故事线找到 owner 来校验。
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Storyline, Event
from schemas import EventCreate, EventUpdate, EventOut
from auth import get_current_user

router = APIRouter(prefix="/api/events", tags=["事件"])


def _event_to_out(e: Event) -> dict:
    """把事件 ORM 对象转成响应格式：tags 从 JSON 字符串解析回数组"""
    return {
        "id": e.id,
        "event_date": e.event_date,
        "title": e.title,
        "description": e.description,
        "people": e.people,
        "tags": json.loads(e.tags or "[]"),
        "image_url": e.image_url,
        "sort_order": e.sort_order,
    }


def _check_owner(db: Session, storyline_id: int, user_id: int) -> Storyline:
    """内部工具：检查故事线存在且属于当前用户，否则报错"""
    s = db.query(Storyline).filter(Storyline.id == storyline_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="故事线不存在")
    if s.owner_id != user_id:
        raise HTTPException(status_code=403, detail="只能操作自己故事线里的事件")
    return s


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    storyline_id: int,
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加事件：storyline_id 作为查询参数传（如 /api/events?storyline_id=1）"""
    s = _check_owner(db, storyline_id, current_user.id)

    # 新事件排在最后：sort_order = 当前最大 + 1
    max_order = db.query(Event).filter(Event.storyline_id == storyline_id).count()
    e = Event(
        storyline_id=storyline_id,
        event_date=data.event_date,
        title=data.title,
        description=data.description,
        people=data.people,
        tags=json.dumps(data.tags, ensure_ascii=False),
        image_url=data.image_url,
        sort_order=max_order,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return _event_to_out(e)


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新事件"""
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="事件不存在")
    _check_owner(db, e.storyline_id, current_user.id)

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "tags" and value is not None:
            value = json.dumps(value, ensure_ascii=False)
        setattr(e, field, value)
    db.commit()
    db.refresh(e)
    return _event_to_out(e)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除事件"""
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="事件不存在")
    _check_owner(db, e.storyline_id, current_user.id)
    db.delete(e)
    db.commit()
