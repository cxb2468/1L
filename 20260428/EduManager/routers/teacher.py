from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Teacher, LeftTeacher
from schemas import TeacherCreate, TeacherUpdate, TeacherResponse
from auth import get_current_user, require_teacher_perm, AdminUser
from typing import Optional, List
import base64
from datetime import date

router = APIRouter(prefix="/teachers", tags=["教员管理"])

def encode_photo(photo_bytes):
    """将照片转换为base64编码"""
    if photo_bytes:
        return base64.b64encode(photo_bytes).decode('utf-8')
    return None

@router.get("/", response_model=List[TeacherResponse])
def list_teachers(
    keyword: Optional[str] = Query(None),
    status: str = Query("active"),  # active, retired, transferred
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_teacher_perm)
):
    """获取教员列表"""
    if status == "active":
        query = db.query(Teacher)
    else:
        query = db.query(LeftTeacher)
    
    if keyword:
        query = query.filter(
            or_(
                Teacher.姓名.like(f"%{keyword}%") if status == "active" else LeftTeacher.姓名.like(f"%{keyword}%"),
                Teacher.编号.like(f"%{keyword}%") if status == "active" else LeftTeacher.编号.like(f"%{keyword}%")
            )
        )
    
    teachers = query.order_by(Teacher.姓名 if status == "active" else LeftTeacher.姓名).all()
    for t in teachers:
        t.照片 = encode_photo(t.照片)
    return teachers

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, status: str = "active", db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """获取单个教员详情"""
    if status == "active":
        teacher = db.query(Teacher).filter(Teacher.编号 == teacher_id).first()
    else:
        teacher = db.query(LeftTeacher).filter(LeftTeacher.编号 == teacher_id).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="教员不存在")
    teacher.照片 = encode_photo(teacher.照片)
    return teacher

@router.post("/")
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """添加教员"""
    existing = db.query(Teacher).filter(Teacher.编号 == teacher.编号).first()
    if existing:
        raise HTTPException(status_code=400, detail="编号已存在")
    
    photo_bytes = None
    if teacher.照片:
        photo_bytes = base64.b64decode(teacher.照片)
    
    db_teacher = Teacher(
        **teacher.dict(exclude={'照片'}),
        照片=photo_bytes
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return {"message": "添加成功", "编号": db_teacher.编号}

@router.put("/{teacher_id}")
def update_teacher(teacher_id: int, teacher: TeacherUpdate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """更新教员信息"""
    db_teacher = db.query(Teacher).filter(Teacher.编号 == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教员不存在")
    
    update_data = teacher.dict(exclude_unset=True, exclude={'照片'})
    if teacher.照片:
        update_data['照片'] = base64.b64decode(teacher.照片)
    
    for key, value in update_data.items():
        setattr(db_teacher, key, value)
    
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """删除教员（永久删除）"""
    db_teacher = db.query(Teacher).filter(Teacher.编号 == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教员不存在")
    
    db.delete(db_teacher)
    db.commit()
    return {"message": "删除成功"}

@router.post("/{teacher_id}/retire")
def retire_teacher(
    teacher_id: int,
    离校原因: str = "退休",
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_teacher_perm)
):
    """办理退休"""
    db_teacher = db.query(Teacher).filter(Teacher.编号 == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教员不存在")
    
    left_teacher = LeftTeacher(
        **db_teacher.__dict__,
        离校时间=date.today(),
        离校原因=离校原因
    )
    
    db.add(left_teacher)
    db.delete(db_teacher)
    db.commit()
    return {"message": "退休办理成功"}

@router.post("/{teacher_id}/transfer")
def transfer_teacher(
    teacher_id: int,
    离校原因: str = "调离",
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_teacher_perm)
):
    """办理调离"""
    db_teacher = db.query(Teacher).filter(Teacher.编号 == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="教员不存在")
    
    left_teacher = LeftTeacher(
        **db_teacher.__dict__,
        离校时间=date.today(),
        离校原因=离校原因
    )
    
    db.add(left_teacher)
    db.delete(db_teacher)
    db.commit()
    return {"message": "调离办理成功"}

@router.post("/left/{teacher_id}/restore")
def restore_teacher(teacher_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """恢复离校教员到在职状态"""
    left_teacher = db.query(LeftTeacher).filter(LeftTeacher.编号 == teacher_id).first()
    if not left_teacher:
        raise HTTPException(status_code=404, detail="离校教员不存在")
    
    teacher = Teacher(
        编号=left_teacher.编号,
        姓名=left_teacher.姓名,
        性别=left_teacher.性别,
        照片=left_teacher.照片,
        个人简历=left_teacher.个人简历,
        民族=left_teacher.民族,
        出生日期=left_teacher.出生日期,
        学历=left_teacher.学历,
        政治面貌=left_teacher.政治面貌,
        参加工作时间=left_teacher.参加工作时间,
        调入本校时间=left_teacher.调入本校时间,
        职称=left_teacher.职称,
        职务或岗位=left_teacher.职务或岗位,
        身份证号=left_teacher.身份证号,
        手机号码=left_teacher.手机号码,
        家庭住址=left_teacher.家庭住址,
        住宅电话=left_teacher.住宅电话,
        籍贯=left_teacher.籍贯,
        户籍所在地=left_teacher.户籍所在地,
        其他资料=left_teacher.其他资料
    )
    
    db.add(teacher)
    db.delete(left_teacher)
    db.commit()
    return {"message": "恢复成功"}

@router.delete("/left/{teacher_id}")
def delete_left_teacher(teacher_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_teacher_perm)):
    """永久删除离校教员记录"""
    left_teacher = db.query(LeftTeacher).filter(LeftTeacher.编号 == teacher_id).first()
    if not left_teacher:
        raise HTTPException(status_code=404, detail="离校教员不存在")
    
    db.delete(left_teacher)
    db.commit()
    return {"message": "删除成功"}
