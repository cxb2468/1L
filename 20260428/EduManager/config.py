import os
from pathlib import Path

# 数据库配置
DATABASE_URL = "sqlite:///./school_mis.db"

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 文件上传配置
UPLOAD_DIR = Path(__file__).parent / "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
