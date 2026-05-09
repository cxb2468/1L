# 校务管理系统 - Python FastAPI版本

## 📖 项目简介

这是一个基于 **Python + FastAPI + SQLite** 开发的学校综合管理平台，由原PHP版本重构而来。系统支持学生学籍管理、教员信息管理、成绩录入与统计、工资管理、班级科目配置及多级权限控制。

## ✨ 主要特性

- 🔐 **安全可靠**：JWT认证 + bcrypt密码加密 + 参数化查询
- 🚀 **高性能**：FastAPI异步框架 + SQLAlchemy ORM
- 📊 **完整功能**：学生/教师/成绩/工资/班级管理全覆盖
- 🎯 **RESTful API**：标准化接口设计，支持第三方集成
- 📱 **现代界面**：响应式设计，支持PC和移动端
- 📝 **自动文档**：Swagger UI自动生成API文档
- 💾 **简化部署**：SQLite单文件数据库，无需额外安装

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.104+ |
| 数据库 | SQLite 3.x |
| ORM | SQLAlchemy 2.0+ |
| 数据验证 | Pydantic 2.5+ |
| 认证 | JWT (python-jose) |
| 密码加密 | bcrypt (passlib) |
| 前端 | HTML5 + CSS3 + JavaScript |

## 📦 快速开始

### 方式一：一键启动（推荐）

```bash
# Windows用户双击运行
start.bat

# Linux/Mac用户
chmod +x start.sh
./start.sh
```

### 方式二：手动启动

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 初始化数据库

```bash
python init_db.py
```

#### 3. 启动服务器

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问系统

- 🌐 Web界面：http://localhost:8000
- 📚 API文档：http://localhost:8000/docs
- 👤 默认账号：`admin` / `123456`

**⚠️ 请在首次登录后立即修改密码！**

## 📋 功能模块

### 1. 学生管理
- ✅ 在校学生列表、添加/编辑/删除
- ✅ 详细档案（含照片、家长信息、评语）
- ✅ 转学/退学办理
- ✅ 毕业升级（自动识别毕业班级）
- ✅ 离校人员管理（查看、恢复、删除）

### 2. 教员管理
- ✅ 在职/退休/调离教员管理
- ✅ 详细档案（含照片、简历、职称）
- ✅ 退休/调离办理
- ✅ 恢复在职

### 3. 成绩管理
- ✅ 期中/期末成绩录入
- ✅ 按班级查看成绩列表
- ✅ 点击表头排序（学号、姓名、各科成绩）
- ✅ 班级平均分统计
- ✅ 最高分/最低分统计

### 4. 工资管理
- ✅ 支持5张独立工资表
- ✅ 自定义工资项目名称
- ✅ 自动计算合计（前5项之和减去第6项）
- ✅ 行列汇总统计
- ✅ 标题和项目设置

### 5. 班级管理
- ✅ 通用班级（年级+序号）添加模式
- ✅ 自设班级（自定义名称）模式
- ✅ 班级分类管理
- ✅ 设置班级科目（最多10科）
- ✅ 班主任分配

### 6. 管理员管理
- ✅ 管理员增删改查
- ✅ 权限分配（4位权限码）
- ✅ 防唯一超级管理员误操作保护
- ✅ 密码修改

### 7. 系统首页
- ✅ 数据统计卡片（学生/教员/离校/班级数）
- ✅ 快捷入口菜单
- ✅ 实时数据更新

## 🔑 权限说明

权限字符串为4位（如 `1111`），从左到右依次代表：

| 位置 | 权限类型 | 说明 |
|------|---------|------|
| 第1位 | 学生管理 | 学生档案、成绩管理等 |
| 第2位 | 教员管理 | 教师档案、退休调离等 |
| 第3位 | 工资管理 | 工资表操作 |
| 第4位 | 系统管理 | 班级管理、管理员设置等 |

示例：
- `1111` - 全部权限（超级管理员）
- `1000` - 仅学生管理
- `1100` - 学生管理 + 教员管理

## 🗂️ 目录结构

```
EduManager/
├── main.py                 # FastAPI主应用入口
├── config.py               # 配置文件
├── database.py             # 数据库连接
├── models.py               # SQLAlchemy数据模型
├── schemas.py              # Pydantic验证模型
├── auth.py                 # 认证和权限模块
├── init_db.py              # 数据库初始化脚本
├── test_api.py             # API测试脚本
├── requirements.txt        # Python依赖
├── start.bat               # Windows启动脚本
├── README.md               # 本文档
├── README_PYTHON.md        # 详细技术文档
├── 快速开始.md             # 快速入门指南
├── 重构总结.md             # PHP到Python重构对比
│
├── routers/                # API路由目录
│   ├── student.py          # 学生管理API
│   ├── teacher.py          # 教员管理API
│   ├── score.py            # 成绩管理API
│   ├── wage.py             # 工资管理API
│   ├── class_manage.py     # 班级管理API
│   └── admin_user.py       # 管理员管理API
│
├── static/                 # 静态文件目录
│   ├── login.html          # 登录页面
│   ├── index.html          # 主页（仪表盘）
│   └── student.html        # 学生管理页面
│
└── uploads/                # 上传文件存储（自动创建）
```

## 🧪 测试验证

运行测试脚本验证所有API功能：

```bash
python test_api.py
```

测试包括：
- ✅ 用户登录
- ✅ 仪表盘统计
- ✅ 班级管理
- ✅ 学生CRUD操作
- ✅ 工资配置查询

## 📊 API使用示例

### Python示例

```python
import requests

# 1. 登录获取token
response = requests.post("http://localhost:8000/login", data={
    "username": "admin",
    "password": "123456"
})
token = response.json()["access_token"]

# 2. 获取学生列表
headers = {"Authorization": f"Bearer {token}"}
students = requests.get("http://localhost:8000/students/", headers=headers).json()

# 3. 添加学生
requests.post("http://localhost:8000/students/", json={
    "学号": 2026001,
    "姓名": "张三",
    "性别": "男",
    "所在班级": "一年级1班",
    "联系电话": "13800138000"
}, headers=headers)

# 4. 获取仪表盘统计
stats = requests.get("http://localhost:8000/dashboard/stats", headers=headers).json()
print(stats)
```

### JavaScript示例

```javascript
// 1. 登录
const loginResponse = await fetch('/login', {
    method: 'POST',
    body: new FormData({
        username: 'admin',
        password: '123456'
    })
});
const { access_token } = await loginResponse.json();

// 2. 获取学生列表
const students = await fetch('/students/', {
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
}).then(r => r.json());
```

## ⚙️ 配置说明

编辑 `config.py` 文件可修改以下配置：

```python
# 数据库路径
DATABASE_URL = "sqlite:///./school_mis.db"

# JWT密钥（生产环境请修改）
SECRET_KEY = "your-secret-key-change-in-production"

# Token过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 最大文件大小
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
```

## ❓ 常见问题

### Q: 提示端口被占用？
A: 修改启动端口或关闭占用端口的程序
```bash
python main.py --port 8080
```

### Q: 如何重置数据库？
A: 删除 `school_mis.db` 文件后重新运行 `python init_db.py`

### Q: 忘记密码怎么办？
A: 删除 `school_mis.db` 文件后重新运行 `python init_db.py`，会重新创建默认管理员账号（admin/123456）

### Q: 如何备份数据？
A: 直接复制 `school_mis.db` 文件即可备份整个数据库

### Q: 支持并发访问吗？
A: 是的，FastAPI原生支持异步并发，可处理多用户同时访问

### Q: 可以部署到Linux服务器吗？
A: 完全可以！只需安装Python 3.8+，然后运行 `python main.py`

## 🔒 安全建议

1. **修改默认密码**：首次登录后立即修改admin密码
2. **更改SECRET_KEY**：生产环境务必修改 `config.py` 中的 `SECRET_KEY`
3. **启用HTTPS**：公网部署建议使用SSL证书
4. **定期备份**：定期备份 `school_mis.db` 文件
5. **限制访问**：内网使用或通过防火墙限制访问IP

## 📝 与原PHP版本的差异

| 特性 | PHP版本 | Python版本 |
|------|---------|------------|
| 数据库 | MySQL | SQLite |
| 会话管理 | Session | JWT Token |
| 密码存储 | 明文 | bcrypt加密 |
| SQL注入防护 | 部分未防护 | 全面参数化查询 |
| 图片处理 | 直接存储 | Base64编码 |
| 前端兼容性 | IE8+ | 现代浏览器 |
| API接口 | 无 | RESTful API |
| 自动文档 | 无 | Swagger UI |

## 🚀 后续扩展建议

1. **功能增强**
   - 多学期支持
   - 考试类型自定义
   - 选课系统
   - 考勤管理
   - 课程表管理

2. **性能优化**
   - 分页查询
   - 缓存机制（Redis）
   - 全文搜索（Elasticsearch）

3. **移动端**
   - 开发移动APP
   - 微信小程序
   - 响应式优化

4. **安全加固**
   - 双因素认证
   - 操作日志审计
   - 数据备份自动化

## 📄 许可证

本项目仅供学习和内部使用。

## 🤝 技术支持

如有问题请查看：
- 📖 [快速开始.md](快速开始.md) - 快速入门指南
- 📚 [README_PYTHON.md](README_PYTHON.md) - 详细技术文档
- 🔧 [重构总结.md](重构总结.md) - PHP到Python重构对比
- 🌐 http://localhost:8000/docs - API在线文档

---

**版本**: v2.0.0 (Python重构版)  
**最后更新**: 2026-04-28  
**开发语言**: Python 3.8+  
**框架**: FastAPI  

🎉 祝您使用愉快！
