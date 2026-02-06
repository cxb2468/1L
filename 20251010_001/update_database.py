import pandas as pd
import sqlite3
import os

# 数据库和Excel文件名
DB_NAME = 'japan.db'
EXCEL_FILE = 'japan.xlsx'

def update_database():
    """清空数据库数据并重新导入Excel数据"""
    print("开始更新数据库...")
    
    # 检查文件是否存在
    if not os.path.exists(EXCEL_FILE):
        print(f"错误：找不到Excel文件 {EXCEL_FILE}")
        return False
    
    # 读取Excel文件
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"成功读取Excel文件，共 {len(df)} 行数据")
        print("列名:", df.columns.tolist())
        print("前5行数据:")
        print(df.head())
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return False
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 删除现有数据但保持表结构
        cursor.execute("DELETE FROM japan_data")
        print("已清空 japan_data 表中的所有数据")
        
        # 重置自动增长计数器
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='japan_data'")
        print("已重置自动增长计数器")
        
        # 重新导入数据，不使用DataFrame的索引，让SQLite自动处理index列
        df.to_sql('japan_data', conn, if_exists='append', index=False)
        print("数据已成功导入到数据库")
        
        # 创建索引以提高查询性能
        print("正在创建索引...")
        for column in df.columns:
            if df[column].dtype == 'object':  # 文本列
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{column} ON japan_data ('{column}')")
                except Exception as e:
                    print(f"创建索引 {column} 时出错: {e}")
        
        # 提交更改
        conn.commit()
        
        # 验证数据导入
        cursor.execute("SELECT COUNT(*) FROM japan_data")
        count = cursor.fetchone()[0]
        print(f"数据库中现在共有 {count} 条记录")
        
        conn.close()
        print("数据库更新完成!")
        return True
        
    except Exception as e:
        print(f"操作数据库时出错: {e}")
        return False

def ensure_autoincrement_table():
    """确保表结构正确设置了自动递增主键"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(japan_data)")
        columns = cursor.fetchall()
        
        print("当前表结构:")
        for col in columns:
            print(f"  列名: {col[1]}, 类型: {col[2]}, 非空: {col[3]}, 默认值: {col[4]}, 主键: {col[5]}")
        
        # 检查是否有自动递增主键
        has_autoincrement_pk = False
        for col in columns:
            if col[1] == 'index' and col[5] == 1:  # index列是主键
                # 检查是否是自动递增的
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='japan_data'")
                table_sql = cursor.fetchone()[0]
                if 'AUTOINCREMENT' in table_sql:
                    has_autoincrement_pk = True
                    break
        
        if not has_autoincrement_pk:
            print("警告: 表结构可能没有正确设置自动递增主键")
            print("建议重建表以确保正确的自动递增行为")
        else:
            print("表已正确设置自动递增主键")
        
        conn.close()
        return True
    except Exception as e:
        print(f"检查表结构时出错: {e}")
        return False

if __name__ == "__main__":
    success = update_database()
    if success:
        print("数据库更新成功!")
        ensure_autoincrement_table()
    else:
        print("数据库更新失败!")