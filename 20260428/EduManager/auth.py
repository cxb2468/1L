from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import AdminUser
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码哈希值"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    """验证用户"""
    user = db.query(AdminUser).filter(AdminUser.用户名 == username).first()
    if not user:
        return False
    if not verify_password(password, user.密码):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(AdminUser).filter(AdminUser.用户名 == username).first()
    if user is None:
        raise credentials_exception
    return user

def check_permission(permission_str: str, required_bit: int):
    """检查权限位 (0-3)"""
    if len(permission_str) != 4:
        return False
    return permission_str[required_bit] == '1'

def require_student_perm(current_user: AdminUser = Depends(get_current_user)):
    """需要学生管理权限"""
    if not check_permission(current_user.权限, 0):
        raise HTTPException(status_code=403, detail="没有学生管理权限")
    return current_user

def require_teacher_perm(current_user: AdminUser = Depends(get_current_user)):
    """需要教员管理权限"""
    if not check_permission(current_user.权限, 1):
        raise HTTPException(status_code=403, detail="没有教员管理权限")
    return current_user

def require_wage_perm(current_user: AdminUser = Depends(get_current_user)):
    """需要工资管理权限"""
    if not check_permission(current_user.权限, 2):
        raise HTTPException(status_code=403, detail="没有工资管理权限")
    return current_user

def require_system_perm(current_user: AdminUser = Depends(get_current_user)):
    """需要系统管理权限"""
    if not check_permission(current_user.权限, 3):
        raise HTTPException(status_code=403, detail="没有系统管理权限")
    return current_user
