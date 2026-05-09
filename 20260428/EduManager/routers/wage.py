from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WageConfig, WageRecord
from schemas import WageConfigResponse, WageConfigUpdate, WageRecordCreate, WageRecordUpdate, WageRecordResponse
from auth import get_current_user, require_wage_perm, AdminUser
from typing import List
from typing import List

router = APIRouter(prefix="/wages", tags=["工资管理"])

@router.get("/config/{table_id}", response_model=WageConfigResponse)
def get_wage_config(table_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_wage_perm)):
    """获取工资表配置"""
    if table_id < 1 or table_id > 5:
        raise HTTPException(status_code=400, detail="工资表编号无效")
    
    config = db.query(WageConfig).filter(WageConfig.table_id == table_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config

@router.put("/config/{table_id}")
def update_wage_config(
    table_id: int, 
    config_update: WageConfigUpdate, 
    db: Session = Depends(get_db), 
    current_user: AdminUser = Depends(require_wage_perm)
):
    """更新工资表配置"""
    config = db.query(WageConfig).filter(WageConfig.table_id == table_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    update_data = config_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.commit()
    return {"message": "配置更新成功"}

@router.get("/records/{table_id}", response_model=List[WageRecordResponse])
def list_wage_records(table_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_wage_perm)):
    """获取工资记录列表"""
    if table_id < 1 or table_id > 5:
        raise HTTPException(status_code=400, detail="工资表编号无效")
    
    records = db.query(WageRecord).filter(WageRecord.table_id == table_id).order_by(WageRecord.id).all()
    return records

@router.post("/records/{table_id}")
def create_wage_record(
    table_id: int,
    record: WageRecordCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_wage_perm)
):
    """添加工资记录"""
    if table_id < 1 or table_id > 5:
        raise HTTPException(status_code=400, detail="工资表编号无效")
    
    # 自动计算合计：项目1+项目2+项目3+项目4+项目5-项目6
    total = record.项目1 + record.项目2 + record.项目3 + record.项目4 + record.项目5 - record.项目6
    
    db_record = WageRecord(
        table_id=table_id,
        姓名=record.姓名,
        项目1=record.项目1,
        项目2=record.项目2,
        项目3=record.项目3,
        项目4=record.项目4,
        项目5=record.项目5,
        项目6=record.项目6,
        项目7=record.项目7,
        合计=total
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return {"message": "添加成功", "id": db_record.id}

@router.put("/records/{record_id}")
def update_wage_record(
    record_id: int,
    record_update: WageRecordUpdate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(require_wage_perm)
):
    """更新工资记录"""
    db_record = db.query(WageRecord).filter(WageRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    update_data = record_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # 重新计算合计
    db_record.合计 = db_record.项目1 + db_record.项目2 + db_record.项目3 + db_record.项目4 + db_record.项目5 - db_record.项目6
    
    db.commit()
    return {"message": "更新成功"}

@router.delete("/records/{record_id}")
def delete_wage_record(record_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_wage_perm)):
    """删除工资记录"""
    db_record = db.query(WageRecord).filter(WageRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}

@router.get("/records/{table_id}/summary")
def wage_summary(table_id: int, db: Session = Depends(get_db), current_user: AdminUser = Depends(require_wage_perm)):
    """获取工资统计（各列合计）"""
    if table_id < 1 or table_id > 5:
        raise HTTPException(status_code=400, detail="工资表编号无效")
    
    records = db.query(WageRecord).filter(WageRecord.table_id == table_id).all()
    
    summary = {
        "项目1合计": sum(r.项目1 or 0 for r in records),
        "项目2合计": sum(r.项目2 or 0 for r in records),
        "项目3合计": sum(r.项目3 or 0 for r in records),
        "项目4合计": sum(r.项目4 or 0 for r in records),
        "项目5合计": sum(r.项目5 or 0 for r in records),
        "项目6合计": sum(r.项目6 or 0 for r in records),
        "总合计": sum(r.合计 or 0 for r in records),
        "记录数": len(records)
    }
    
    return summary
