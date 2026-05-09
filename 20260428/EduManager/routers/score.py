from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from database import get_db
from models import Student, Class
from auth import get_current_user, require_student_perm, AdminUser
from typing import Optional, Dict, Any
import json

router = APIRouter(prefix="/scores", tags=["成绩管理"])

@router.get("/list")
def list_scores(
    class_name: str = Query(...),
    exam_type: str = Query(...),  # 期中 or 期末
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_student_perm)
):
    """获取班级成绩列表"""
    # 获取班级科目
    cls = db.query(Class).filter(Class.所在班级 == class_name).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    subjects = []
    for i in range(1, 11):
        subject = getattr(cls, f'科目{i}')
        if subject:
            subjects.append((i, subject))
    
    # 获取学生成绩
    students = db.query(Student).filter(Student.所在班级 == class_name).order_by(Student.学号).all()
    
    result = []
    for student in students:
        scores = {}
        for idx, subject_name in subjects:
            score_field = f"{exam_type}{idx}"
            score = getattr(student, score_field, None)
            scores[subject_name] = score
        
        result.append({
            "学号": student.学号,
            "姓名": student.姓名,
            "性别": student.性别,
            "成绩": scores
        })
    
    return {
        "班级": class_name,
        "考试类型": exam_type,
        "科目": [name for _, name in subjects],
        "学生成绩": result
    }

@router.post("/entry")
def entry_score(
    学号: int,
    exam_type: str,
    subject_index: int,
    score: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_student_perm)
):
    """录入单科成绩"""
    if subject_index < 1 or subject_index > 10:
        raise HTTPException(status_code=400, detail="科目索引无效")
    
    score_field = f"{exam_type}{subject_index}"
    student = db.query(Student).filter(Student.学号 == 学号).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    setattr(student, score_field, score)
    db.commit()
    return {"message": "成绩录入成功"}

@router.get("/statistics")
def score_statistics(
    class_name: str = Query(...),
    exam_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_student_perm)
):
    """获取班级成绩统计"""
    # 获取班级科目
    cls = db.query(Class).filter(Class.所在班级 == class_name).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    subjects = []
    for i in range(1, 11):
        subject = getattr(cls, f'科目{i}')
        if subject:
            subjects.append((i, subject))
    
    # 计算各科平均分
    stats = {}
    for idx, subject_name in subjects:
        score_field = f"{exam_type}{idx}"
        avg_result = db.query(func.avg(getattr(Student, score_field))).filter(
            Student.所在班级 == class_name
        ).scalar()
        
        stats[subject_name] = {
            "平均分": round(avg_result, 2) if avg_result else 0,
            "最高分": db.query(func.max(getattr(Student, score_field))).filter(
                Student.所在班级 == class_name
            ).scalar() or 0,
            "最低分": db.query(func.min(getattr(Student, score_field))).filter(
                Student.所在班级 == class_name
            ).scalar() or 0
        }
    
    return {
        "班级": class_name,
        "考试类型": exam_type,
        "统计": stats
    }
