# -*- coding: utf-8 -*-
"""
日志管理器模块
负责应用程序的日志记录和管理
"""

import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

class AppLogger:
    """应用程序日志管理器"""
    
    def __init__(self, log_dir: str = None, log_level: str = 'INFO'):
        if log_dir is None:
            # 默认日志目录
            self.log_dir = os.path.join(
                os.path.expanduser('~'), 
                '.desktop_archive_logs'
            )
        else:
            self.log_dir = log_dir
            
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置日志级别
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 初始化日志器
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志器
        
        Returns:
            配置好的日志器
        """
        # 创建日志器
        logger = logging.getLogger('DesktopArchive')
        logger.setLevel(self.log_level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
            
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件处理器（轮转日志）
        log_file = os.path.join(self.log_dir, 'desktop_archive.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器（仅在调试时使用）
        if self.log_level <= logging.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        return logger
        
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
        
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
        
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
        
    def exception(self, message: str):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message)
        
    def log_archive_operation(self, operation: str, file_count: int, 
                            success: bool, details: str = ''):
        """记录归档操作
        
        Args:
            operation: 操作类型
            file_count: 文件数量
            success: 是否成功
            details: 详细信息
        """
        status = "成功" if success else "失败"
        message = f"归档操作 - {operation}: {status}, 文件数量: {file_count}"
        
        if details:
            message += f", 详情: {details}"
            
        if success:
            self.info(message)
        else:
            self.error(message)
            
    def log_scheduler_event(self, event: str, details: str = ''):
        """记录调度器事件
        
        Args:
            event: 事件类型
            details: 详细信息
        """
        message = f"调度器事件 - {event}"
        if details:
            message += f": {details}"
            
        self.info(message)
        
    def log_config_change(self, setting: str, old_value: str, new_value: str):
        """记录配置变更
        
        Args:
            setting: 设置项名称
            old_value: 旧值
            new_value: 新值
        """
        message = f"配置变更 - {setting}: {old_value} -> {new_value}"
        self.info(message)
        
    def log_file_operation(self, operation: str, file_path: str, 
                          success: bool, error_msg: str = ''):
        """记录文件操作
        
        Args:
            operation: 操作类型（移动、复制、删除等）
            file_path: 文件路径
            success: 是否成功
            error_msg: 错误消息
        """
        status = "成功" if success else "失败"
        message = f"文件操作 - {operation}: {status}, 文件: {file_path}"
        
        if not success and error_msg:
            message += f", 错误: {error_msg}"
            
        if success:
            self.debug(message)
        else:
            self.error(message)
            
    def get_log_files(self) -> list:
        """获取所有日志文件列表
        
        Returns:
            日志文件路径列表
        """
        log_files = []
        
        try:
            for file in os.listdir(self.log_dir):
                if file.endswith('.log'):
                    file_path = os.path.join(self.log_dir, file)
                    log_files.append(file_path)
                    
            # 按修改时间排序
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
        except Exception as e:
            self.error(f"获取日志文件列表失败: {str(e)}")
            
        return log_files
        
    def get_recent_logs(self, lines: int = 100) -> list:
        """获取最近的日志条目
        
        Args:
            lines: 要获取的行数
            
        Returns:
            日志条目列表
        """
        log_entries = []
        
        try:
            log_file = os.path.join(self.log_dir, 'desktop_archive.log')
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    # 获取最后N行
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    log_entries = [line.strip() for line in recent_lines if line.strip()]
                    
        except Exception as e:
            self.error(f"读取最近日志失败: {str(e)}")
            
        return log_entries
        
    def search_logs(self, keyword: str, days: int = 7) -> list:
        """搜索日志中的关键词
        
        Args:
            keyword: 搜索关键词
            days: 搜索最近几天的日志
            
        Returns:
            匹配的日志条目列表
        """
        matching_entries = []
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for log_file in self.get_log_files():
                # 检查文件修改时间
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_mtime < cutoff_date:
                    continue
                    
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if keyword.lower() in line.lower():
                            matching_entries.append({
                                'file': os.path.basename(log_file),
                                'line_number': line_num,
                                'content': line.strip()
                            })
                            
        except Exception as e:
            self.error(f"搜索日志失败: {str(e)}")
            
        return matching_entries
        
    def cleanup_old_logs(self, retention_days: int = 30):
        """清理旧日志文件
        
        Args:
            retention_days: 保留天数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for log_file in self.get_log_files():
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                
                if file_mtime < cutoff_date:
                    os.remove(log_file)
                    self.info(f"已删除旧日志文件: {os.path.basename(log_file)}")
                    
        except Exception as e:
            self.error(f"清理旧日志失败: {str(e)}")
            
    def get_log_statistics(self) -> dict:
        """获取日志统计信息
        
        Returns:
            日志统计信息字典
        """
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'oldest_log': None,
            'newest_log': None,
            'log_levels': {
                'DEBUG': 0,
                'INFO': 0,
                'WARNING': 0,
                'ERROR': 0,
                'CRITICAL': 0
            }
        }
        
        try:
            log_files = self.get_log_files()
            stats['total_files'] = len(log_files)
            
            if log_files:
                # 计算总大小
                total_size = sum(os.path.getsize(f) for f in log_files)
                stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
                
                # 最新和最旧的日志
                stats['newest_log'] = os.path.basename(log_files[0])
                stats['oldest_log'] = os.path.basename(log_files[-1])
                
                # 统计日志级别（仅统计主日志文件）
                main_log = os.path.join(self.log_dir, 'desktop_archive.log')
                if os.path.exists(main_log):
                    with open(main_log, 'r', encoding='utf-8') as f:
                        for line in f:
                            for level in stats['log_levels'].keys():
                                if f' - {level} - ' in line:
                                    stats['log_levels'][level] += 1
                                    break
                                    
        except Exception as e:
            self.error(f"获取日志统计失败: {str(e)}")
            
        return stats
        
    def export_logs(self, export_path: str, days: int = 7) -> bool:
        """导出日志到指定路径
        
        Args:
            export_path: 导出文件路径
            days: 导出最近几天的日志
            
        Returns:
            导出是否成功
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with open(export_path, 'w', encoding='utf-8') as export_file:
                export_file.write(f"桌面文件归档工具日志导出\n")
                export_file.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                export_file.write(f"日志范围: 最近{days}天\n")
                export_file.write("=" * 50 + "\n\n")
                
                for log_file in self.get_log_files():
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if file_mtime < cutoff_date:
                        continue
                        
                    export_file.write(f"\n--- {os.path.basename(log_file)} ---\n")
                    
                    with open(log_file, 'r', encoding='utf-8') as f:
                        export_file.write(f.read())
                        
            self.info(f"日志已导出到: {export_path}")
            return True
            
        except Exception as e:
            self.error(f"导出日志失败: {str(e)}")
            return False
            
    def set_log_level(self, level: str):
        """设置日志级别
        
        Args:
            level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        try:
            new_level = getattr(logging, level.upper())
            self.logger.setLevel(new_level)
            self.log_level = new_level
            
            # 更新所有处理器的级别
            for handler in self.logger.handlers:
                handler.setLevel(new_level)
                
            self.info(f"日志级别已设置为: {level.upper()}")
            
        except AttributeError:
            self.error(f"无效的日志级别: {level}")