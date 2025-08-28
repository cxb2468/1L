# -*- coding: utf-8 -*-
"""
文件扫描器模块
负责扫描指定目录中的Office文档和其他文件
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class FileScanner:
    """文件扫描器类"""
    
    def __init__(self):
        # 支持的文件类型映射
        self.file_type_map = {
            '.doc': 'Word文档',
            '.docx': 'Word文档',
            '.xls': 'Excel表格',
            '.xlsx': 'Excel表格',
            '.ppt': 'PowerPoint演示文稿',
            '.pptx': 'PowerPoint演示文稿',
            '.pdf': 'PDF文档',
            '.txt': '文本文档',
            '.rtf': 'RTF文档'
        }
        
    def scan_files(self, directory: str, file_extensions: List[str] = None) -> List[Dict]:
        """扫描指定目录中的文件
        
        Args:
            directory: 要扫描的目录路径
            file_extensions: 要扫描的文件扩展名列表，如果为None则扫描所有支持的类型
            
        Returns:
            包含文件信息的字典列表
        """
        if file_extensions is None:
            file_extensions = list(self.file_type_map.keys())
            
        files = []
        
        try:
            # 确保目录存在
            if not os.path.exists(directory):
                raise FileNotFoundError(f"目录不存在: {directory}")
                
            # 扫描文件
            for ext in file_extensions:
                pattern = os.path.join(directory, f"*{ext}")
                for file_path in glob.glob(pattern, recursive=False):
                    if os.path.isfile(file_path):
                        file_info = self.get_file_info(file_path)
                        if file_info:
                            files.append(file_info)
                            
            # 按修改时间排序（最新的在前）
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            
        except Exception as e:
            raise Exception(f"扫描文件时出错: {str(e)}")
            
        return files
        
    def get_file_info(self, file_path: str) -> Dict:
        """获取文件详细信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            包含文件信息的字典
        """
        try:
            stat = os.stat(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'extension': file_ext,
                'type': self.file_type_map.get(file_ext, '未知类型'),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'accessed_time': datetime.fromtimestamp(stat.st_atime)
            }
            
        except Exception as e:
            print(f"获取文件信息失败 {file_path}: {str(e)}")
            return None
            
    def filter_files_by_date(self, files: List[Dict], days_old: int = 7) -> List[Dict]:
        """根据文件修改日期过滤文件
        
        Args:
            files: 文件列表
            days_old: 文件修改时间超过多少天的文件会被包含
            
        Returns:
            过滤后的文件列表
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        return [f for f in files if f['modified_time'] < cutoff_date]
        
    def filter_files_by_size(self, files: List[Dict], min_size_mb: float = 0, 
                           max_size_mb: float = float('inf')) -> List[Dict]:
        """根据文件大小过滤文件
        
        Args:
            files: 文件列表
            min_size_mb: 最小文件大小（MB）
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            过滤后的文件列表
        """
        return [f for f in files if min_size_mb <= f['size_mb'] <= max_size_mb]
        
    def group_files_by_type(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """按文件类型分组
        
        Args:
            files: 文件列表
            
        Returns:
            按类型分组的文件字典
        """
        groups = {}
        for file_info in files:
            file_type = file_info['type']
            if file_type not in groups:
                groups[file_type] = []
            groups[file_type].append(file_info)
            
        return groups
        
    def group_files_by_date(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """按修改日期分组（按年月）
        
        Args:
            files: 文件列表
            
        Returns:
            按日期分组的文件字典
        """
        groups = {}
        for file_info in files:
            date_key = file_info['modified_time'].strftime('%Y-%m')
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(file_info)
            
        return groups
        
    def get_file_statistics(self, files: List[Dict]) -> Dict:
        """获取文件统计信息
        
        Args:
            files: 文件列表
            
        Returns:
            统计信息字典
        """
        if not files:
            return {
                'total_count': 0,
                'total_size_mb': 0,
                'by_type': {},
                'oldest_file': None,
                'newest_file': None,
                'largest_file': None
            }
            
        total_size = sum(f['size'] for f in files)
        by_type = self.group_files_by_type(files)
        type_stats = {}
        
        for file_type, type_files in by_type.items():
            type_stats[file_type] = {
                'count': len(type_files),
                'size_mb': round(sum(f['size'] for f in type_files) / (1024 * 1024), 2)
            }
            
        # 找出最老、最新和最大的文件
        oldest_file = min(files, key=lambda x: x['modified_time'])
        newest_file = max(files, key=lambda x: x['modified_time'])
        largest_file = max(files, key=lambda x: x['size'])
        
        return {
            'total_count': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_type': type_stats,
            'oldest_file': oldest_file,
            'newest_file': newest_file,
            'largest_file': largest_file
        }
        
    def is_file_in_use(self, file_path: str) -> bool:
        """检查文件是否正在被使用
        
        Args:
            file_path: 文件路径
            
        Returns:
            如果文件正在被使用返回True，否则返回False
        """
        try:
            # 尝试以独占模式打开文件
            with open(file_path, 'r+b') as f:
                pass
            return False
        except (IOError, OSError):
            return True
            
    def get_safe_files_to_archive(self, files: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """获取可以安全归档的文件列表
        
        Args:
            files: 文件列表
            
        Returns:
            (可归档文件列表, 正在使用的文件列表)
        """
        safe_files = []
        in_use_files = []
        
        for file_info in files:
            if self.is_file_in_use(file_info['path']):
                in_use_files.append(file_info)
            else:
                safe_files.append(file_info)
                
        return safe_files, in_use_files
        
    def validate_file_path(self, file_path: str) -> bool:
        """验证文件路径是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            如果路径有效返回True，否则返回False
        """
        try:
            return os.path.exists(file_path) and os.path.isfile(file_path)
        except:
            return False