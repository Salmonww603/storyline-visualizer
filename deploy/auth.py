"""
认证工具：密码哈希、JWT token 生成与校验、当前用户获取。
安全要点：
1. 密码绝不存明文，用 bcrypt 哈希（不可逆）
2. JWT 密钥从环境变量读，不写死在代码里
3. 每个需要登录的接口都通过 get_current_user 拿身份
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# bcrypt 哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置：密钥从环境变量读，没设置时用开发默认值（部署时必须换掉）
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # token 有效期 7 天

# OAuth2 密码模式：告诉 FastAPI 从 /api/auth/login 拿 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 可选认证：和上面那个的区别是 auto_error=False。
# 默认的 oauth2_scheme 遇到没带 token 的请求会直接抛 401，
# 但"公开故事线"这种接口匿名访客也要能看，所以不能强制。
# 这里让 FastAPI 没 token 时不报错、把 token 位置传 None 进来，
# 由下面的 get_optional_user 自己决定怎么处理。
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login", auto_error=False
)


def hash_password(password: str) -> str:
    """把明文密码转成 bcrypt 哈希（每次结果都不同，因为加盐）"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """登录时比对：明文密码 vs 存的哈希值"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT token：把用户 id 塞进 payload，签名后返回"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    从请求头的 Bearer token 解析出当前用户。
    FastAPI 会自动把返回值注入到接口函数里。
    任何需要登录的接口加一个参数 user: User = Depends(get_current_user) 即可。
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_error
    return user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    可选认证：用于"公开内容任何人可看、私密内容仅本人可看"的接口。
    - 没带 token → 返回 None（代表匿名访客），不抛 401
    - 带了有效 token → 返回对应用户
    - 带了无效/过期 token → 也返回 None（当作匿名，后面权限判断会拦住私密的）
    这样接口函数里只要判断 user 是不是 owner 即可。
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == user_id).first()
