# -*- coding: utf-8 -*-
"""
归档管理器模块
负责将文件归档到指定目录，并按规则组织文件结构
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import json

class ArchiveManager:
    """归档管理器类"""
    
    def __init__(self):
        self.archive_log = []
        
    def archive_files(self, files: List[Dict], archive_base_path: str, 
                     organize_by: str = 'type_and_date') -> int:
        """归档文件列表
        
        Args:
            files: 要归档的文件列表
            archive_base_path: 归档基础路径
            organize_by: 组织方式 ('type', 'date', 'type_and_date')
            
        Returns:
            成功归档的文件数量
        """
        if not files:
            return 0
            
        # 确保归档目录存在
        os.makedirs(archive_base_path, exist_ok=True)
        
        archived_count = 0
        
        for file_info in files:
            try:
                # 确定目标路径
                target_path = self.get_target_path(file_info, archive_base_path, organize_by)
                
                # 创建目标目录
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # 处理文件名冲突
                target_path = self.resolve_name_conflict(target_path)
                
                # 移动文件
                shutil.move(file_info['path'], target_path)
                
                # 记录归档操作
                self.log_archive_operation(file_info, target_path, 'success')
                archived_count += 1
                
            except Exception as e:
                # 记录失败操作
                self.log_archive_operation(file_info, '', 'failed', str(e))
                print(f"归档文件失败 {file_info['name']}: {str(e)}")
                
        # 保存归档日志
        self.save_archive_log(archive_base_path)
        
        return archived_count
        
    def get_target_path(self, file_info: Dict, base_path: str, organize_by: str) -> str:
        """获取文件的目标归档路径
        
        Args:
            file_info: 文件信息
            base_path: 归档基础路径
            organize_by: 组织方式
            
        Returns:
            目标文件路径
        """
        file_name = file_info['name']
        file_type = file_info['type']
        modified_date = file_info['modified_time']
        
        if organize_by == 'type':
            # 按文件类型组织
            return os.path.join(base_path, file_type, file_name)
            
        elif organize_by == 'date':
            # 按日期组织
            year_month = modified_date.strftime('%Y-%m')
            return os.path.join(base_path, year_month, file_name)
            
        elif organize_by == 'type_and_date':
            # 按类型和日期组织
            year_month = modified_date.strftime('%Y-%m')
            return os.path.join(base_path, file_type, year_month, file_name)
            
        else:
            # 默认直接放在基础目录
            return os.path.join(base_path, file_name)
            
    def resolve_name_conflict(self, target_path: str) -> str:
        """解决文件名冲突
        
        Args:
            target_path: 目标文件路径
            
        Returns:
            解决冲突后的文件路径
        """
        if not os.path.exists(target_path):
            return target_path
            
        # 分离文件名和扩展名
        path_obj = Path(target_path)
        base_name = path_obj.stem
        extension = path_obj.suffix
        directory = path_obj.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = directory / new_name
            
            if not os.path.exists(new_path):
                return str(new_path)
                
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{base_name}_{timestamp}{extension}"
                return str(directory / new_name)
                
    def copy_files(self, files: List[Dict], archive_base_path: str, 
                  organize_by: str = 'type_and_date') -> int:
        """复制文件到归档目录（而不是移动）
        
        Args:
            files: 要复制的文件列表
            archive_base_path: 归档基础路径
            organize_by: 组织方式
            
        Returns:
            成功复制的文件数量
        """
        if not files:
            return 0
            
        # 确保归档目录存在
        os.makedirs(archive_base_path, exist_ok=True)
        
        copied_count = 0
        
        for file_info in files:
            try:
                # 确定目标路径
                target_path = self.get_target_path(file_info, archive_base_path, organize_by)
                
                # 创建目标目录
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # 处理文件名冲突
                target_path = self.resolve_name_conflict(target_path)
                
                # 复制文件
                shutil.copy2(file_info['path'], target_path)
                
                # 记录操作
                self.log_archive_operation(file_info, target_path, 'copied')
                copied_count += 1
                
            except Exception as e:
                # 记录失败操作
                self.log_archive_operation(file_info, '', 'copy_failed', str(e))
                print(f"复制文件失败 {file_info['name']}: {str(e)}")
                
        # 保存归档日志
        self.save_archive_log(archive_base_path)
        
        return copied_count
        
    def log_archive_operation(self, file_info: Dict, target_path: str, 
                            status: str, error_msg: str = ''):
        """记录归档操作
        
        Args:
            file_info: 文件信息
            target_path: 目标路径
            status: 操作状态
            error_msg: 错误消息
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_path': file_info['path'],
            'source_name': file_info['name'],
            'file_type': file_info['type'],
            'file_size_mb': file_info['size_mb'],
            'target_path': target_path,
            'status': status,
            'error_message': error_msg
        }
        
        self.archive_log.append(log_entry)
        
    def save_archive_log(self, archive_base_path: str):
        """保存归档日志到文件
        
        Args:
            archive_base_path: 归档基础路径
        """
        if not self.archive_log:
            return
            
        try:
            log_file_path = os.path.join(archive_base_path, 'archive_log.json')
            
            # 如果日志文件已存在，加载现有日志
            existing_log = []
            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        existing_log = json.load(f)
                except:
                    existing_log = []
                    
            # 合并日志
            existing_log.extend(self.archive_log)
            
            # 保持最近1000条记录
            if len(existing_log) > 1000:
                existing_log = existing_log[-1000:]
                
            # 保存日志
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_log, f, ensure_ascii=False, indent=2)
                
            # 清空当前日志
            self.archive_log = []
            
        except Exception as e:
            print(f"保存归档日志失败: {str(e)}")
            
    def get_archive_statistics(self, archive_base_path: str) -> Dict:
        """获取归档统计信息
        
        Args:
            archive_base_path: 归档基础路径
            
        Returns:
            统计信息字典
        """
        try:
            log_file_path = os.path.join(archive_base_path, 'archive_log.json')
            
            if not os.path.exists(log_file_path):
                return {
                    'total_archived': 0,
                    'total_size_mb': 0,
                    'by_type': {},
                    'by_date': {},
                    'success_rate': 0,
                    'last_archive_time': None
                }
                
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                
            # 统计成功归档的文件
            successful_archives = [entry for entry in log_data 
                                 if entry['status'] in ['success', 'copied']]
            
            total_archived = len(successful_archives)
            total_size = sum(entry.get('file_size_mb', 0) for entry in successful_archives)
            
            # 按类型统计
            by_type = {}
            for entry in successful_archives:
                file_type = entry.get('file_type', '未知')
                if file_type not in by_type:
                    by_type[file_type] = {'count': 0, 'size_mb': 0}
                by_type[file_type]['count'] += 1
                by_type[file_type]['size_mb'] += entry.get('file_size_mb', 0)
                
            # 按日期统计（按天）
            by_date = {}
            for entry in successful_archives:
                date_key = entry['timestamp'][:10]  # YYYY-MM-DD
                if date_key not in by_date:
                    by_date[date_key] = {'count': 0, 'size_mb': 0}
                by_date[date_key]['count'] += 1
                by_date[date_key]['size_mb'] += entry.get('file_size_mb', 0)
                
            # 计算成功率
            total_operations = len(log_data)
            success_rate = (total_archived / total_operations * 100) if total_operations > 0 else 0
            
            # 最后归档时间
            last_archive_time = None
            if successful_archives:
                last_archive_time = max(entry['timestamp'] for entry in successful_archives)
                
            return {
                'total_archived': total_archived,
                'total_size_mb': round(total_size, 2),
                'by_type': by_type,
                'by_date': by_date,
                'success_rate': round(success_rate, 1),
                'last_archive_time': last_archive_time
            }
            
        except Exception as e:
            print(f"获取归档统计失败: {str(e)}")
            return {}
            
    def cleanup_empty_directories(self, archive_base_path: str):
        """清理空目录
        
        Args:
            archive_base_path: 归档基础路径
        """
        try:
            for root, dirs, files in os.walk(archive_base_path, topdown=False):
                for directory in dirs:
                    dir_path = os.path.join(root, directory)
                    try:
                        # 尝试删除空目录
                        os.rmdir(dir_path)
                    except OSError:
                        # 目录不为空，跳过
                        pass
        except Exception as e:
            print(f"清理空目录失败: {str(e)}")
            
    def restore_file(self, archive_path: str, original_path: str) -> bool:
        """从归档中恢复文件
        
        Args:
            archive_path: 归档中的文件路径
            original_path: 原始位置路径
            
        Returns:
            恢复是否成功
        """
        try:
            if not os.path.exists(archive_path):
                return False
                
            # 确保目标目录存在
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            
            # 处理文件名冲突
            original_path = self.resolve_name_conflict(original_path)
            
            # 移动文件回原位置
            shutil.move(archive_path, original_path)
            
            return True
            
        except Exception as e:
            print(f"恢复文件失败: {str(e)}")
            return False
            
    def get_archive_structure(self, archive_base_path: str) -> Dict:
        """获取归档目录结构
        
        Args:
            archive_base_path: 归档基础路径
            
        Returns:
            目录结构字典
        """
        structure = {}
        
        try:
            for root, dirs, files in os.walk(archive_base_path):
                # 计算相对路径
                rel_path = os.path.relpath(root, archive_base_path)
                if rel_path == '.':
                    rel_path = ''
                    
                # 统计文件信息
                file_count = len([f for f in files if not f.startswith('.')])
                total_size = 0
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                        except:
                            pass
                            
                if file_count > 0:
                    structure[rel_path or 'root'] = {
                        'file_count': file_count,
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'subdirs': dirs.copy()
                    }
                    
        except Exception as e:
            print(f"获取目录结构失败: {str(e)}")
            
        return structure