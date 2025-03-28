import sqlite3
import os
from datetime import datetime
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DBManager:
    def __init__(self, db_path='recordings.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库，创建必要的表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recordings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT NOT NULL,
                        text_content TEXT,
                        created_time DATETIME NOT NULL
                    )
                """)
                conn.commit()
                logging.info('数据库初始化成功')
        except sqlite3.Error as e:
            logging.error(f'数据库初始化失败: {e}')
            raise
    
    def add_recording(self, file_path, text_content=''):
        """添加新的录音记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO recordings (file_path, text_content, created_time) VALUES (?, ?, ?)",
                (file_path, text_content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_all_recordings(self):
        """获取所有录音记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recordings ORDER BY created_time DESC")
            return cursor.fetchall()
    
    def update_text_content(self, recording_id, text_content):
        """保留方法以维持数据库兼容性"""
        pass
    
    def delete_recording(self, recording_id):
        """删除录音记录"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # 首先获取文件路径
            try:
                conn.execute("BEGIN TRANSACTION")
                # 先删除数据库记录
                cursor.execute("DELETE FROM recordings WHERE id = ? RETURNING file_path", (recording_id,))
                result = cursor.fetchone()
                if not result:
                    print(f"未找到ID为{recording_id}的记录")
                    conn.rollback()
                    return False
                
                file_path = result[0]
                conn.commit()
                
                # 事务提交成功后删除文件
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        print(f"文件删除失败但数据库记录已移除: {e}")
                return True
            except Exception as e:
                conn.rollback()
                print(f"数据库操作失败: {e}")
                return False

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"数据库操作失败: {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"删除操作失败: {e}")
            return False
        finally:
            if conn:
                conn.close()