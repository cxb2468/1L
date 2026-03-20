# coding: utf-8
"""
清理缓存文件
清理过期的JSON数据文件，避免文件过大
"""

import os
import sys
import json
from datetime import datetime, timedelta

# 确保项目根目录在 sys.path 中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 延迟导入logger，避免循环导入
# from logger.logger_config import get_logger

# logger = get_logger(__name__)
logger = None

def _get_logger():
    """延迟获取logger实例"""
    global logger
    if logger is None:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
    return logger

def clean_old_json_files(max_days=7):
    """
    清理超过指定天数的JSON文件
    :param max_days: 保留的最大天数
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    if not os.path.exists(data_dir):
        _get_logger().info("数据目录不存在，无需清理")
        return
    
    # 获取当前日期
    current_date = datetime.now().date()
    
    # 遍历数据目录中的所有文件
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                # 从文件名提取日期（格式：YYYYMMDD.json）
                date_str = filename.split('.')[0]  # 移除扩展名
                file_date = datetime.strptime(date_str, '%Y%m%d').date()
                
                # 计算日期差异
                date_diff = (current_date - file_date).days
                
                # 如果文件超过最大保留天数，则删除
                if date_diff > max_days:
                    file_path = os.path.join(data_dir, filename)
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    _get_logger().info(f"已删除过期JSON文件: {filename} (大小: {file_size} bytes, 超过保留期限 {date_diff} 天)")
                    
            except ValueError:
                # 文件名不符合日期格式，跳过
                _get_logger().debug(f"跳过非日期格式的JSON文件: {filename}")
            except Exception as e:
                _get_logger().error(f"删除JSON文件 {filename} 时出错: {e}")

def truncate_large_json_files(max_size_mb=10):
    """
    截断过大的JSON文件，保留最新的数据
    :param max_size_mb: 最大大小（MB）
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    if not os.path.exists(data_dir):
        return
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(data_dir, filename)
                file_size = os.path.getsize(file_path)
                
                if file_size > max_size_bytes:
                    _get_logger().info(f"文件 {filename} 过大 ({file_size / (1024*1024):.2f} MB)，开始截断...")
                    
                    # 读取并解析JSON数据
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            _get_logger().error(f"JSON文件 {filename} 格式错误，跳过处理")
                            continue
                    
                    if isinstance(data, list) and len(data) > 100:  # 如果是列表且元素较多
                        # 保留后一半的数据
                        kept_data = data[len(data)//2:]
                        
                        # 写回文件
                        temp_file_path = file_path + '.tmp'
                        with open(temp_file_path, 'w', encoding='utf-8') as f:
                            json.dump(kept_data, f, ensure_ascii=False, indent=2)
                        
                        # 原子性替换
                        import shutil
                        shutil.move(temp_file_path, file_path)
                        
                        new_size = os.path.getsize(file_path)
                        _get_logger().info(f"文件 {filename} 已截断，原大小: {file_size / (1024*1024):.2f} MB, 新大小: {new_size / (1024*1024):.2f} MB")
                    
            except Exception as e:
                _get_logger().error(f"处理大JSON文件 {filename} 时出错: {e}")

if __name__ == "__main__":
    _get_logger().info("开始清理缓存文件...")
    clean_old_json_files()
    truncate_large_json_files()
    _get_logger().info("缓存清理完成")