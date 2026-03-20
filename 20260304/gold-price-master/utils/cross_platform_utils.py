# coding: utf-8
"""
跨平台兼容性工具模块
提供统一的跨平台处理函数，确保代码在Windows和Linux环境下都能正常运行
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Any, Callable, Optional

# 获取日志记录器
logger = logging.getLogger(__name__)

class CrossPlatformUtils:
    """跨平台工具类"""
    
    @staticmethod
    def get_system_info() -> dict:
        """获取系统信息"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    @staticmethod
    def is_windows() -> bool:
        """判断是否为Windows系统"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_linux() -> bool:
        """判断是否为Linux系统"""
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def is_macos() -> bool:
        """判断是否为macOS系统"""
        return platform.system().lower() == 'darwin'
    
    @staticmethod
    def get_project_root() -> Path:
        """获取项目根目录（跨平台兼容）"""
        # 从当前文件位置向上查找项目根目录
        current_path = Path(__file__).parent
        while current_path.parent != current_path:  # 不是根目录
            if (current_path / 'main.py').exists():
                return current_path
            current_path = current_path.parent
        # 如果没找到，返回当前目录
        return Path.cwd()
    
    @staticmethod
    def safe_mkdir(directory: str | Path, exist_ok: bool = True) -> bool:
        """
        安全创建目录
        :param directory: 目录路径
        :param exist_ok: 是否允许目录已存在
        :return: 是否创建成功
        """
        try:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=exist_ok)
            return True
        except PermissionError:
            logger.error(f"权限不足，无法创建目录: {directory}")
            return False
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def safe_file_operation(filepath: str | Path, operation_func: Callable, *args, **kwargs) -> Any:
        """
        安全的文件操作包装器
        :param filepath: 文件路径
        :param operation_func: 操作函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 操作结果
        """
        try:
            # 确保父目录存在
            parent_dir = Path(filepath).parent
            CrossPlatformUtils.safe_mkdir(parent_dir)
            return operation_func(filepath, *args, **kwargs)
        except PermissionError:
            logger.error(f"权限不足，无法访问文件: {filepath}")
            raise
        except FileNotFoundError:
            logger.error(f"文件或目录不存在: {filepath}")
            raise
        except Exception as e:
            logger.error(f"文件操作失败 {filepath}: {e}")
            raise
    
    @staticmethod
    def sync_filesystem() -> None:
        """跨平台的文件系统同步"""
        system = platform.system().lower()
        
        if system == 'linux':
            try:
                os.sync()
                logger.debug("Linux文件系统同步完成")
            except (AttributeError, OSError) as e:
                logger.warning(f"Linux文件系统同步失败: {e}")
        elif system == 'darwin':  # macOS
            try:
                subprocess.run(['sync'], check=True, timeout=10, capture_output=True)
                logger.debug("macOS文件系统同步完成")
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.warning(f"macOS文件系统同步失败: {e}")
        elif system == 'windows':
            # Windows系统通常不需要手动同步
            logger.debug("Windows系统，跳过文件系统同步")
        else:
            logger.warning(f"未知操作系统: {system}，跳过文件系统同步")
    
    @staticmethod
    def safe_subprocess_run(command: list, timeout: int = 300, **kwargs) -> subprocess.CompletedProcess:
        """
        安全的subprocess运行函数
        :param command: 命令列表
        :param timeout: 超时时间（秒）
        :param kwargs: 其他参数
        :return: subprocess.CompletedProcess对象
        """
        if not command or not command[0]:
            raise ValueError("命令不能为空")
        
        # 设置默认参数
        kwargs.setdefault('capture_output', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('timeout', timeout)
        kwargs.setdefault('check', True)
        
        try:
            logger.debug(f"执行命令: {' '.join(str(arg) for arg in command)}")
            result = subprocess.run(command, **kwargs)
            logger.debug(f"命令执行成功，返回码: {result.returncode}")
            return result
        except subprocess.TimeoutExpired:
            logger.warning(f"命令执行超时: {' '.join(str(arg) for arg in command)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e}")
            logger.error(f"标准输出: {e.stdout}")
            logger.error(f"错误输出: {e.stderr}")
            raise
        except FileNotFoundError:
            logger.error(f"命令未找到: {command[0]}")
            raise
        except Exception as e:
            logger.error(f"执行命令时发生未知错误: {e}")
            raise
    
    @staticmethod
    def get_temp_directory() -> Path:
        """获取跨平台的临时目录"""
        system = platform.system().lower()
        
        if system == 'windows':
            # Windows使用TEMP环境变量
            temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or 'C:\\temp'
        else:
            # Linux/macOS使用/tmp
            temp_dir = '/tmp'
        
        return Path(temp_dir)
    
    @staticmethod
    def normalize_path(path: str | Path) -> Path:
        """
        标准化路径（跨平台）
        :param path: 输入路径
        :return: 标准化后的Path对象
        """
        return Path(path).resolve()
    
    @staticmethod
    def get_python_executable() -> str:
        """获取Python可执行文件路径（跨平台）"""
        return sys.executable
    
    @staticmethod
    def is_admin() -> bool:
        """判断当前是否具有管理员权限（跨平台）"""
        try:
            if CrossPlatformUtils.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except (AttributeError, OSError, PermissionError):
            return False

# 创建全局实例
cross_platform = CrossPlatformUtils()

# 便捷函数
def get_system_info():
    return cross_platform.get_system_info()

def is_windows():
    return cross_platform.is_windows()

def is_linux():
    return cross_platform.is_linux()

def is_macos():
    return cross_platform.is_macos()

def get_project_root():
    return cross_platform.get_project_root()

def safe_mkdir(directory, exist_ok=True):
    return cross_platform.safe_mkdir(directory, exist_ok)

def safe_file_operation(filepath, operation_func, *args, **kwargs):
    return cross_platform.safe_file_operation(filepath, operation_func, *args, **kwargs)

def sync_filesystem():
    cross_platform.sync_filesystem()

def safe_subprocess_run(command, timeout=300, **kwargs):
    return cross_platform.safe_subprocess_run(command, timeout, **kwargs)

def get_temp_directory():
    return cross_platform.get_temp_directory()

def normalize_path(path):
    return cross_platform.normalize_path(path)

def get_python_executable():
    return cross_platform.get_python_executable()

def is_admin():
    return cross_platform.is_admin()