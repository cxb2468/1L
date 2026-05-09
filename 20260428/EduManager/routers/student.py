from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Student, LeftStudent, Class
from schemas import StudentCreate, StudentUpdate, StudentResponse, LeftStudentResponse
from auth import get_current_user, require_student_perm, AdminUser
from typing import Optional, List
import base64
from datetime import date

router = APIRouter(prefix="/students", tags=["学生管理"])

def encode_photo(photo_bytes):
    """将照片转换为base64编码"""
    if photo_bytes:
        return base64.b64encode(photo_bytes).decode('utf-8')
    return None

@router.get("/", response_model=List[StudentResponse])
def list_students(
    class_name: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_student_perm)
):
    """获取学生列表"""
    query = db.query(Student)
    
    if class_name:
        query = query.filter(Student.所在班级 == class_name)
    if keyword:
        query = query.filter(
            or_(
                Student.姓名.like(f"%{keyword}%"),
                Student.学号.like(f"%{keyword}%")
            )
        )
    
    students = query.order_by(Student.所在班级, Student.姓名).all()
    for s in students:
        s.照片 = encode_photo(s.照片)
    return students

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """获取单个学生详情"""
    student = db.query(Student).filter(Student.学号 == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    student.照片 = encode_photo(student.照片)
    return student

@router.post("/")
def create_student(student: StudentCreate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """添加学生"""
    # 检查学号是否已存在
    existing = db.query(Student).filter(Student.学号 == student.学号).first()
    if existing:
        raise HTTPException(status_code=400, detail="学号已存在")
    
    # 处理照片
    photo_bytes = None
    if student.照片:
        photo_bytes = base64.b64decode(student.照片)
    
    db_student = Student(
        **student.dict(exclude={'照片'}),
        照片=photo_bytes
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return {"message": "添加成功", "学号": db_student.学号}

@router.put("/{student_id}")
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """更新学生信息"""
    db_student = db.query(Student).filter(Student.学号 == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    update_data = student.dict(exclude_unset=True, exclude={'照片'})
    if student.照片:
        update_data['照片'] = base64.b64decode(student.照片)
    
    for key, value in update_data.items():
        setattr(db_student, key, value)
    
    db.commit()
    return {"message": "更新成功"}

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """删除学生（永久删除）"""
    db_student = db.query(Student).filter(Student.学号 == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    db.delete(db_student)
    db.commit()
    return {"message": "删除成功"}

@router.post("/{student_id}/transfer")
def transfer_student(
    student_id: int, 
    离校时间: date, 
    离校原因: str,
    db: Session = Depends(get_db), 
    current_user: AdminUser = Depends(require_student_perm)
):
    """转学/退学（移至离校人员名单）"""
    db_student = db.query(Student).filter(Student.学号 == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 创建离校记录
    left_student = LeftStudent(
        学号=db_student.学号,
        姓名=db_student.姓名,
        性别=db_student.性别,
        民族=db_student.民族,
        出生日期=db_student.出生日期,
        入学日期=db_student.入学日期,
        所在班级=db_student.所在班级,
        班内职务=db_student.班内职务,
        家庭住址=db_student.家庭住址,
        联系电话=db_student.联系电话,
        户籍=db_student.户籍,
        籍贯=db_student.籍贯,
        家长A=db_student.家长A,
        家长A姓名=db_student.家长A姓名,
        家长A单位=db_student.家长A单位,
        家长A电话=db_student.家长A电话,
        家长B=db_student.家长B,
        家长B姓名=db_student.家长B姓名,
        家长B单位=db_student.家长B单位,
        家长B电话=db_student.家长B电话,
        照片=db_student.照片,
        本学期评语=db_student.本学期评语,
        综合评语=db_student.综合评语,
        期中1=db_student.期中1, 期中2=db_student.期中2, 期中3=db_student.期中3,
        期中4=db_student.期中4, 期中5=db_student.期中5, 期中6=db_student.期中6,
        期中7=db_student.期中7, 期中8=db_student.期中8, 期中9=db_student.期中9,
        期中10=db_student.期中10,
        期末1=db_student.期末1, 期末2=db_student.期末2, 期末3=db_student.期末3,
        期末4=db_student.期末4, 期末5=db_student.期末5, 期末6=db_student.期末6,
        期末7=db_student.期末7, 期末8=db_student.期末8, 期末9=db_student.期末9,
        期末10=db_student.期末10,
        离校时间=离校时间,
        离校原因=离校原因
    )
    
    db.add(left_student)
    db.delete(db_student)
    db.commit()
    return {"message": "转学/退学办理成功"}

@router.get("/left/list", response_model=List[LeftStudentResponse])
def list_left_students(
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_student_perm)
):
    """获取离校学生名单"""
    query = db.query(LeftStudent)
    
    if keyword:
        query = query.filter(
            or_(
                LeftStudent.姓名.like(f"%{keyword}%"),
                LeftStudent.学号.like(f"%{keyword}%")
            )
        )
    
    students = query.order_by(LeftStudent.离校时间.desc()).all()
    for s in students:
        s.照片 = encode_photo(s.照片)
    return students

@router.post("/left/{student_id}/restore")
def restore_student(student_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """恢复离校学生到学籍表"""
    left_student = db.query(LeftStudent).filter(LeftStudent.学号 == student_id).first()
    if not left_student:
        raise HTTPException(status_code=404, detail="离校学生不存在")
    
    # 创建学籍记录
    student = Student(
        学号=left_student.学号,
        姓名=left_student.姓名,
        性别=left_student.性别,
        民族=left_student.民族,
        出生日期=left_student.出生日期,
        入学日期=left_student.入学日期,
        所在班级=left_student.所在班级,
        班内职务=left_student.班内职务,
        家庭住址=left_student.家庭住址,
        联系电话=left_student.联系电话,
        户籍=left_student.户籍,
        籍贯=left_student.籍贯,
        家长A=left_student.家长A,
        家长A姓名=left_student.家长A姓名,
        家长A单位=left_student.家长A单位,
        家长A电话=left_student.家长A电话,
        家长B=left_student.家长B,
        家长B姓名=left_student.家长B姓名,
        家长B单位=left_student.家长B单位,
        家长B电话=left_student.家长B电话,
        照片=left_student.照片,
        本学期评语=left_student.本学期评语,
        综合评语=left_student.综合评语,
        期中1=left_student.期中1, 期中2=left_student.期中2, 期中3=left_student.期中3,
        期中4=left_student.期中4, 期中5=left_student.期中5, 期中6=left_student.期中6,
        期中7=left_student.期中7, 期中8=left_student.期中8, 期中9=left_student.期中9,
        期中10=left_student.期中10,
        期末1=left_student.期末1, 期末2=left_student.期末2, 期末3=left_student.期末3,
        期末4=left_student.期末4, 期末5=left_student.期末5, 期末6=left_student.期末6,
        期末7=left_student.期末7, 期末8=left_student.期末8, 期末9=left_student.期末9,
        期末10=left_student.期末10
    )
    
    db.add(student)
    db.delete(left_student)
    db.commit()
    return {"message": "恢复成功"}

@router.delete("/left/{student_id}")
def delete_left_student(student_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_student_perm)):
    """永久删除离校学生记录"""
    left_student = db.query(LeftStudent).filter(LeftStudent.学号 == student_id).first()
    if not left_student:
        raise HTTPException(status_code=404, detail="离校学生不存在")
    
    db.delete(left_student)
    db.commit()
    return {"message": "删除成功"}
