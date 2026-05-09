from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import AdminUser
from schemas import LoginRequest, TokenResponse
from auth import authenticate_user, create_access_token, timedelta, get_current_user
from datetime import datetime
import uvicorn
import os

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="校务管理系统",
    description="基于Python + FastAPI + SQLite的学校综合管理平台",
    version="2.0.0"
)

# 导入路由（在挂载静态文件之前导入）
from routers import student, teacher, class_manage, score, wage, admin_user

# 注册路由
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(class_manage.router)
app.include_router(score.router)
app.include_router(wage.router)
app.include_router(admin_user.router)

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    """根路径，重定向到登录页面"""
    return FileResponse('static/login.html')

@app.get("/index")
def index():
    """主页"""
    return FileResponse('static/index.html')

@app.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=1440)  # 24小时
    access_token = create_access_token(
        data={"sub": user.用户名}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.用户名,
        "permission": user.权限
    }

@app.get("/me")
def get_current_user_info(current_user: AdminUser = Depends(get_current_user)):
    """获取当前用户信息（需要通过token验证）"""
    return {
        "用户名": current_user.用户名,
        "权限": current_user.权限
    }

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    from models import Student, Teacher, LeftStudent, Class
    
    stats = {
        "在校学生数": db.query(Student).count(),
        "在职教员数": db.query(Teacher).count(),
        "离校人员数": db.query(LeftStudent).count(),
        "班级数": db.query(Class).count()
    }
    
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
