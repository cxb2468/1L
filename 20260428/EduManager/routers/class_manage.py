from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Class, Student, LeftStudent
from schemas import ClassCreate, ClassUpdate, ClassResponse
from auth import get_current_user, require_system_perm, AdminUser
from typing import Optional, List

router = APIRouter(prefix="/classes", tags=["班级管理"])

@router.get("/", response_model=List[ClassResponse])
def list_classes(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_system_perm)
):
    """获取班级列表"""
    classes = db.query(Class).order_by(Class.所在班级).all()
    return classes

@router.get("/{class_name}", response_model=ClassResponse)
def get_class(class_name: str, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_system_perm)):
    """获取单个班级详情"""
    cls = db.query(Class).filter(Class.所在班级 == class_name).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    return cls

@router.post("/")
def create_class(cls: ClassCreate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_system_perm)):
    """添加班级"""
    existing = db.query(Class).filter(Class.所在班级 == cls.所在班级).first()
    if existing:
        raise HTTPException(status_code=400, detail="班级已存在")
    
    db_class = Class(**cls.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return {"message": "添加成功", "所在班级": db_class.所在班级}

@router.put("/{class_name}")
def update_class(class_name: str, cls: ClassUpdate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_system_perm)):
    """更新班级信息"""
    db_class = db.query(Class).filter(Class.所在班级 == class_name).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    update_data = cls.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_class, key, value)
    
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{class_name}")
def delete_class(class_name: str, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_system_perm)):
    """删除班级（同时将该班学生移至离校名单）"""
    db_class = db.query(Class).filter(Class.所在班级 == class_name).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    # 将该班所有学生移至离校名单
    students = db.query(Student).filter(Student.所在班级 == class_name).all()
    for student in students:
        left_student = LeftStudent(
            学号=student.学号,
            姓名=student.姓名,
            性别=student.性别,
            民族=student.民族,
            出生日期=student.出生日期,
            入学日期=student.入学日期,
            所在班级=student.所在班级,
            班内职务=student.班内职务,
            家庭住址=student.家庭住址,
            联系电话=student.联系电话,
            户籍=student.户籍,
            籍贯=student.籍贯,
            家长A=student.家长A,
            家长A姓名=student.家长A姓名,
            家长A单位=student.家长A单位,
            家长A电话=student.家长A电话,
            家长B=student.家长B,
            家长B姓名=student.家长B姓名,
            家长B单位=student.家长B单位,
            家长B电话=student.家长B电话,
            照片=student.照片,
            本学期评语=student.本学期评语,
            综合评语=student.综合评语,
            期中1=student.期中1, 期中2=student.期中2, 期中3=student.期中3,
            期中4=student.期中4, 期中5=student.期中5, 期中6=student.期中6,
            期中7=student.期中7, 期中8=student.期中8, 期中9=student.期中9,
            期中10=student.期中10,
            期末1=student.期末1, 期末2=student.期末2, 期末3=student.期末3,
            期末4=student.期末4, 期末5=student.期末5, 期末6=student.期末6,
            期末7=student.期末7, 期末8=student.期末8, 期末9=student.期末9,
            期末10=student.期末10,
            离校时间=None,
            离校原因="班级删除"
        )
        db.add(left_student)
        db.delete(student)
    
    db.delete(db_class)
    db.commit()
    return {"message": "删除成功"}
