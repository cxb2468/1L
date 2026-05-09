from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import AdminUser
from schemas import AdminUserCreate, AdminUserUpdate, AdminUserResponse
from auth import get_current_user, require_system_perm, get_password_hash, verify_password
from typing import List

router = APIRouter(prefix="/admin-users", tags=["管理员管理"])

@router.get("/", response_model=List[AdminUserResponse])
def list_admin_users(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_system_perm)
):
    """获取管理员列表"""
    users = db.query(AdminUser).all()
    return users

@router.post("/")
def create_admin_user(
    user: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_system_perm)
):
    """添加管理员"""
    existing = db.query(AdminUser).filter(AdminUser.用户名 == user.用户名).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if len(user.权限) != 4:
        raise HTTPException(status_code=400, detail="权限字符串必须为4位")
    
    db_user = AdminUser(
        用户名=user.用户名,
        密码=get_password_hash(user.密码),
        权限=user.权限
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "添加成功", "用户名": db_user.用户名}

@router.put("/{username}")
def update_admin_user(
    username: str,
    user_update: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_system_perm)
):
    """更新管理员信息"""
    db_user = db.query(AdminUser).filter(AdminUser.用户名 == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否为唯一超级管理员
    if username == current_user.用户名:
        super_admins = db.query(AdminUser).filter(AdminUser.权限 == "1111").count()
        if super_admins == 1 and user_update.权限 and user_update.权限 != "1111":
            raise HTTPException(status_code=400, detail="不能降低唯一超级管理员的权限")
    
    if user_update.密码:
        db_user.密码 = get_password_hash(user_update.密码)
    
    if user_update.权限:
        if len(user_update.权限) != 4:
            raise HTTPException(status_code=400, detail="权限字符串必须为4位")
        
        # 如果要修改权限，检查是否会影响唯一超级管理员
        if db_user.权限 == "1111" and user_update.权限 != "1111":
            super_admins = db.query(AdminUser).filter(AdminUser.权限 == "1111").count()
            if super_admins == 1:
                raise HTTPException(status_code=400, detail="系统中至少需要保留一个超级管理员")
        
        db_user.权限 = user_update.权限
    
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{username}")
def delete_admin_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_system_perm)
):
    """删除管理员"""
    if username == current_user.用户名:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    db_user = db.query(AdminUser).filter(AdminUser.用户名 == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否为唯一超级管理员
    if db_user.权限 == "1111":
        super_admins = db.query(AdminUser).filter(AdminUser.权限 == "1111").count()
        if super_admins == 1:
            raise HTTPException(status_code=400, detail="不能删除唯一的超级管理员")
    
    db.delete(db_user)
    db.commit()
    return {"message": "删除成功"}
