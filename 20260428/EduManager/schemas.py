from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import base64

# ==================== 学生相关 ====================
class StudentBase(BaseModel):
    学号: int
    姓名: str
    性别: Optional[str] = None
    所在班级: Optional[str] = None
    联系电话: Optional[str] = None
    家庭住址: Optional[str] = None
    户籍: Optional[str] = None
    籍贯: Optional[str] = None
    家长A: Optional[str] = None
    家长A姓名: Optional[str] = None
    家长A单位: Optional[str] = None
    家长A电话: Optional[str] = None
    家长B: Optional[str] = None
    家长B姓名: Optional[str] = None
    家长B单位: Optional[str] = None
    家长B电话: Optional[str] = None
    班内职务: Optional[str] = None
    民族: Optional[str] = None
    出生日期: Optional[date] = None
    入学日期: Optional[date] = None
    身份证号: Optional[str] = None
    本学期评语: Optional[str] = None
    综合评语: Optional[str] = None

class StudentCreate(StudentBase):
    照片: Optional[str] = None  # base64编码的图片

class StudentUpdate(StudentBase):
    照片: Optional[str] = None

class StudentResponse(StudentBase):
    照片: Optional[str] = None  # base64编码的图片
    
    class Config:
        from_attributes = True

# ==================== 离校学生相关 ====================
class LeftStudentResponse(StudentBase):
    照片: Optional[str] = None
    离校时间: Optional[date] = None
    离校原因: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== 教员相关 ====================
class TeacherBase(BaseModel):
    编号: int
    姓名: str
    性别: Optional[str] = None
    民族: Optional[str] = None
    出生日期: Optional[date] = None
    学历: Optional[str] = None
    政治面貌: Optional[str] = None
    参加工作时间: Optional[date] = None
    调入本校时间: Optional[date] = None
    职称: Optional[str] = None
    职务或岗位: Optional[str] = None
    身份证号: Optional[str] = None
    手机号码: Optional[str] = None
    家庭住址: Optional[str] = None
    住宅电话: Optional[str] = None
    籍贯: Optional[str] = None
    户籍所在地: Optional[str] = None
    个人简历: Optional[str] = None
    其他资料: Optional[str] = None

class TeacherCreate(TeacherBase):
    照片: Optional[str] = None

class TeacherUpdate(TeacherBase):
    照片: Optional[str] = None

class TeacherResponse(TeacherBase):
    照片: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== 班级相关 ====================
class ClassBase(BaseModel):
    所在班级: str
    班主任: Optional[str] = None
    科目1: Optional[str] = None
    科目2: Optional[str] = None
    科目3: Optional[str] = None
    科目4: Optional[str] = None
    科目5: Optional[str] = None
    科目6: Optional[str] = None
    科目7: Optional[str] = None
    科目8: Optional[str] = None
    科目9: Optional[str] = None
    科目10: Optional[str] = None
    班级分类: Optional[str] = "通用"

class ClassCreate(ClassBase):
    pass

class ClassUpdate(ClassBase):
    pass

class ClassResponse(ClassBase):
    class Config:
        from_attributes = True

# ==================== 管理员相关 ====================
class AdminUserBase(BaseModel):
    用户名: str
    权限: str = "0000"

class AdminUserCreate(AdminUserBase):
    密码: str

class AdminUserUpdate(BaseModel):
    密码: Optional[str] = None
    权限: Optional[str] = None

class AdminUserResponse(AdminUserBase):
    class Config:
        from_attributes = True

# ==================== 工资配置相关 ====================
class WageConfigBase(BaseModel):
    table_id: int
    标题: str
    项目1名称: Optional[str] = "基本工资"
    项目2名称: Optional[str] = "岗位津贴"
    项目3名称: Optional[str] = "绩效工资"
    项目4名称: Optional[str] = "工龄工资"
    项目5名称: Optional[str] = "其他补贴"
    项目6名称: Optional[str] = "养老保险"
    项目7名称: Optional[str] = "实发合计"

class WageConfigCreate(WageConfigBase):
    pass

class WageConfigUpdate(BaseModel):
    标题: Optional[str] = None
    项目1名称: Optional[str] = None
    项目2名称: Optional[str] = None
    项目3名称: Optional[str] = None
    项目4名称: Optional[str] = None
    项目5名称: Optional[str] = None
    项目6名称: Optional[str] = None
    项目7名称: Optional[str] = None

class WageConfigResponse(WageConfigBase):
    class Config:
        from_attributes = True

# ==================== 工资记录相关 ====================
class WageRecordBase(BaseModel):
    table_id: int
    姓名: str
    项目1: float = 0
    项目2: float = 0
    项目3: float = 0
    项目4: float = 0
    项目5: float = 0
    项目6: float = 0
    项目7: float = 0

class WageRecordCreate(WageRecordBase):
    pass

class WageRecordUpdate(BaseModel):
    姓名: Optional[str] = None
    项目1: Optional[float] = None
    项目2: Optional[float] = None
    项目3: Optional[float] = None
    项目4: Optional[float] = None
    项目5: Optional[float] = None
    项目6: Optional[float] = None
    项目7: Optional[float] = None

class WageRecordResponse(WageRecordBase):
    id: int
    合计: float
    
    class Config:
        from_attributes = True

# ==================== 登录相关 ====================
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    permission: str

# ==================== 通用响应 ====================
class Response(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
