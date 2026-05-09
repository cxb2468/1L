from database import Base
from sqlalchemy import Column, Integer, String, Text, Date, Float, LargeBinary, ForeignKey

# 学籍表
class Student(Base):
    __tablename__ = "学籍表"
    
    学号 = Column(Integer, primary_key=True)
    姓名 = Column(String(50))
    性别 = Column(String(2))
    所在班级 = Column(String(50))
    照片 = Column(LargeBinary)
    本学期评语 = Column(Text)
    综合评语 = Column(Text)
    期中1 = Column(Integer)
    期中2 = Column(Integer)
    期中3 = Column(Integer)
    期中4 = Column(Integer)
    期中5 = Column(Integer)
    期中6 = Column(Integer)
    期中7 = Column(Integer)
    期中8 = Column(Integer)
    期中9 = Column(Integer)
    期中10 = Column(Integer)
    期末1 = Column(Integer)
    期末2 = Column(Integer)
    期末3 = Column(Integer)
    期末4 = Column(Integer)
    期末5 = Column(Integer)
    期末6 = Column(Integer)
    期末7 = Column(Integer)
    期末8 = Column(Integer)
    期末9 = Column(Integer)
    期末10 = Column(Integer)
    联系电话 = Column(String(20))
    家庭住址 = Column(String(200))
    户籍 = Column(String(100))
    籍贯 = Column(String(100))
    家长A = Column(String(20))
    家长A姓名 = Column(String(50))
    家长A单位 = Column(String(100))
    家长A电话 = Column(String(20))
    家长B = Column(String(20))
    家长B姓名 = Column(String(50))
    家长B单位 = Column(String(100))
    家长B电话 = Column(String(20))
    班内职务 = Column(String(50))
    民族 = Column(String(20))
    出生日期 = Column(Date)
    入学日期 = Column(Date)
    身份证号 = Column(String(18))

# 离校人员名单
class LeftStudent(Base):
    __tablename__ = "离校人员名单"
    
    学号 = Column(Integer, primary_key=True)
    姓名 = Column(String(50))
    性别 = Column(String(2))
    民族 = Column(String(20))
    出生日期 = Column(Date)
    入学日期 = Column(Date)
    所在班级 = Column(String(50))
    班内职务 = Column(String(50))
    家庭住址 = Column(String(200))
    联系电话 = Column(String(20))
    户籍 = Column(String(100))
    籍贯 = Column(String(100))
    家长A = Column(String(20))
    家长A姓名 = Column(String(50))
    家长A单位 = Column(String(100))
    家长A电话 = Column(String(20))
    家长B = Column(String(20))
    家长B姓名 = Column(String(50))
    家长B单位 = Column(String(100))
    家长B电话 = Column(String(20))
    照片 = Column(LargeBinary)
    本学期评语 = Column(Text)
    综合评语 = Column(Text)
    期中1 = Column(Integer)
    期中2 = Column(Integer)
    期中3 = Column(Integer)
    期中4 = Column(Integer)
    期中5 = Column(Integer)
    期中6 = Column(Integer)
    期中7 = Column(Integer)
    期中8 = Column(Integer)
    期中9 = Column(Integer)
    期中10 = Column(Integer)
    期末1 = Column(Integer)
    期末2 = Column(Integer)
    期末3 = Column(Integer)
    期末4 = Column(Integer)
    期末5 = Column(Integer)
    期末6 = Column(Integer)
    期末7 = Column(Integer)
    期末8 = Column(Integer)
    期末9 = Column(Integer)
    期末10 = Column(Integer)
    离校时间 = Column(Date)
    离校原因 = Column(String(100))

# 教员表
class Teacher(Base):
    __tablename__ = "教员表"
    
    编号 = Column(Integer, primary_key=True)
    姓名 = Column(String(50))
    性别 = Column(String(2))
    照片 = Column(LargeBinary)
    个人简历 = Column(Text)
    民族 = Column(String(20))
    出生日期 = Column(Date)
    学历 = Column(String(20))
    政治面貌 = Column(String(20))
    参加工作时间 = Column(Date)
    调入本校时间 = Column(Date)
    职称 = Column(String(30))
    职务或岗位 = Column(String(50))
    身份证号 = Column(String(18))
    手机号码 = Column(String(20))
    家庭住址 = Column(String(200))
    住宅电话 = Column(String(20))
    籍贯 = Column(String(100))
    户籍所在地 = Column(String(100))
    其他资料 = Column(Text)

# 离校教员表
class LeftTeacher(Base):
    __tablename__ = "离校教员表"
    
    编号 = Column(Integer, primary_key=True)
    姓名 = Column(String(50))
    性别 = Column(String(2))
    照片 = Column(LargeBinary)
    个人简历 = Column(Text)
    民族 = Column(String(20))
    出生日期 = Column(Date)
    学历 = Column(String(20))
    政治面貌 = Column(String(20))
    参加工作时间 = Column(Date)
    调入本校时间 = Column(Date)
    职称 = Column(String(30))
    职务或岗位 = Column(String(50))
    身份证号 = Column(String(18))
    手机号码 = Column(String(20))
    家庭住址 = Column(String(200))
    住宅电话 = Column(String(20))
    籍贯 = Column(String(100))
    户籍所在地 = Column(String(100))
    其他资料 = Column(Text)
    离校时间 = Column(Date)
    离校原因 = Column(String(100))

# 班级表
class Class(Base):
    __tablename__ = "班级表"
    
    所在班级 = Column(String(50), primary_key=True)
    班主任 = Column(String(50))
    科目1 = Column(String(50))
    科目2 = Column(String(50))
    科目3 = Column(String(50))
    科目4 = Column(String(50))
    科目5 = Column(String(50))
    科目6 = Column(String(50))
    科目7 = Column(String(50))
    科目8 = Column(String(50))
    科目9 = Column(String(50))
    科目10 = Column(String(50))
    班级分类 = Column(String(20))

# 管理员表
class AdminUser(Base):
    __tablename__ = "管理员表"
    
    用户名 = Column(String(50), primary_key=True)
    密码 = Column(String(100))  # 存储bcrypt哈希
    权限 = Column(String(4), default="0000")

# 系统设置表
class SystemSettings(Base):
    __tablename__ = "系统设置表"
    
    id = Column(Integer, primary_key=True, default=1)
    学校名称 = Column(String(100), default="校务管理系统")

# 工资配置表
class WageConfig(Base):
    __tablename__ = "wage_config"
    
    table_id = Column(Integer, primary_key=True)
    标题 = Column(String(100))
    项目1名称 = Column(String(50))
    项目2名称 = Column(String(50))
    项目3名称 = Column(String(50))
    项目4名称 = Column(String(50))
    项目5名称 = Column(String(50))
    项目6名称 = Column(String(50))
    项目7名称 = Column(String(50))

# 工资记录表
class WageRecord(Base):
    __tablename__ = "wage_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer)
    姓名 = Column(String(50))
    项目1 = Column(Float)
    项目2 = Column(Float)
    项目3 = Column(Float)
    项目4 = Column(Float)
    项目5 = Column(Float)
    项目6 = Column(Float)
    项目7 = Column(Float)
    合计 = Column(Float)
