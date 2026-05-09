from database import engine, Base, SessionLocal
from models import AdminUser, SystemSettings, WageConfig, Class
from auth import get_password_hash
import sys

def init_database():
    """初始化数据库，创建所有表和默认数据"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin_count = db.query(AdminUser).count()
        if admin_count == 0:
            print("创建默认管理员账号...")
            admin = AdminUser(
                用户名="admin",
                密码=get_password_hash("123456"),
                权限="1111"
            )
            db.add(admin)
        
        # 检查系统设置
        settings_count = db.query(SystemSettings).count()
        if settings_count == 0:
            print("创建默认系统设置...")
            settings = SystemSettings(
                id=1,
                学校名称="校务管理系统"
            )
            db.add(settings)
        
        # 检查工资配置
        wage_config_count = db.query(WageConfig).count()
        if wage_config_count == 0:
            print("创建默认工资配置...")
            for i in range(1, 6):
                config = WageConfig(
                    table_id=i,
                    标题=f"教员工资表(表{i})",
                    项目1名称="基本工资",
                    项目2名称="岗位津贴",
                    项目3名称="绩效工资",
                    项目4名称="工龄工资",
                    项目5名称="其他补贴",
                    项目6名称="养老保险",
                    项目7名称="实发合计"
                )
                db.add(config)
        
        # 添加示例班级
        class_count = db.query(Class).count()
        if class_count == 0:
            print("创建示例班级...")
            sample_class = Class(
                所在班级="一年级1班",
                班主任="admin",
                科目1="Mathematics",
                科目2="Chinese",
                科目3="English",
                科目4="Politics",
                科目5="History",
                科目6="Geography",
                科目7="Physics",
                科目8="Chemistry",
                科目9="Biology",
                科目10="Sports",
                班级分类="通用"
            )
            db.add(sample_class)
        
        db.commit()
        print("数据库初始化完成！")
        print("\n默认管理员账号:")
        print("用户名: admin")
        print("密码: 123456")
        print("\n请在首次登录后立即修改密码！")
        
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
