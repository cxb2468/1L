#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everything版本检测器
用于检测系统中安装的Everything版本，包括便携版
"""

import os
import winreg
import psutil
import logging
from typing import Dict, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('version_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_everything_install_path() -> Optional[str]:
    """
    获取Everything的安装路径
    :return: Everything安装路径，如果未安装返回None
    """
    try:
        # 检查64位注册表
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Everything", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            path = winreg.QueryValueEx(key, "InstallLocation")[0]
            winreg.CloseKey(key)
            return path
        except Exception:
            # 检查32位注册表
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Everything", 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
                path = winreg.QueryValueEx(key, "InstallLocation")[0]
                winreg.CloseKey(key)
                return path
            except Exception:
                return None
    except Exception:
        return None

def get_everything_version() -> Optional[Tuple[int, int]]:
    """
    获取Everything版本号
    :return: (主版本, 次版本)，如果未安装返回None
    """
    install_path = get_everything_install_path()
    if not install_path:
        return None
    
    exe_path = os.path.join(install_path, "Everything.exe")
    if not os.path.exists(exe_path):
        return None
    
    try:
        import win32api
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        major = (ms >> 16) & 0xffff
        minor = (ms & 0xffff)
        return major, minor
    except Exception:
        # 如果win32api不可用，尝试从文件名或其他方式判断
        try:
            # 检查是否存在1.5版本的特征文件
            if os.path.exists(os.path.join(install_path, "Everything64.dll")):
                return 1, 5
            return 1, 4
        except Exception:
            return None

def get_running_everything_process() -> Optional[psutil.Process]:
    """
    获取正在运行的Everything进程
    :return: Everything进程对象，如果没有运行返回None
    """
    try:
        logger.info("开始检查正在运行的进程...")
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name == 'Everything.exe':
                    logger.info(f"找到Everything进程: {proc_name}")
                    return proc
                # 也检查一下可能的其他名称
                if 'Everything' in proc_name:
                    logger.info(f"找到包含'Everything'的进程: {proc_name}")
            except Exception as e:
                logger.warning(f"获取进程信息失败: {str(e)}")
        logger.info("未找到Everything进程")
        return None
    except Exception as e:
        logger.error(f"获取Everything进程时出错: {str(e)}")
        return None

def get_window_title(process_id: int) -> Optional[str]:
    """
    获取进程的窗口标题
    :param process_id: 进程ID
    :return: 窗口标题，如果没有窗口返回None
    """
    try:
        import ctypes
        from ctypes.wintypes import DWORD, LPWSTR, BOOL
        
        # 定义回调函数类型
        EnumWindowsProc = ctypes.WINFUNCTYPE(BOOL, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        
        # 存储窗口标题
        window_title = None
        
        def enum_windows_callback(hwnd, lParam):
            nonlocal window_title
            # 获取窗口的进程ID
            pid = DWORD(0)
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # 如果进程ID匹配
            if pid.value == lParam:
                # 获取窗口标题
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
                    window_title = buffer.value
                return False  # 停止枚举
            return True  # 继续枚举
        
        # 枚举所有窗口
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), process_id)
        return window_title
    except Exception as e:
        logger.error(f"获取窗口标题时出错: {str(e)}")
        return None

def get_process_version(proc: psutil.Process) -> Optional[Tuple[int, int]]:
    """
    从进程获取Everything版本
    :param proc: Everything进程对象
    :return: (主版本, 次版本)，如果无法获取返回None
    """
    try:
        exe_path = proc.exe()
        if not exe_path:
            return None
        
        logger.info(f"正在检查进程: {exe_path}")
        
        # 首先检查进程所在目录是否有1.5版本的DLL文件
        exe_dir = os.path.dirname(exe_path)
        logger.info(f"进程所在目录: {exe_dir}")
        
        # 检查1.5版本的DLL文件（最可靠的检测方式）
        dll_path_1_5 = os.path.join(exe_dir, "Everything3_x64.dll")
        if os.path.exists(dll_path_1_5):
            logger.info(f"检测到1.5版本DLL: {dll_path_1_5}")
            return 1, 5
        
        # 检查1.4版本的DLL文件
        dll_path_1_4 = os.path.join(exe_dir, "Everything64.dll")
        if os.path.exists(dll_path_1_4):
            logger.info(f"检测到1.4版本DLL: {dll_path_1_4}")
            return 1, 4
        
        # 尝试从窗口标题检测版本
        window_title = get_window_title(proc.pid)
        if window_title:
            logger.info(f"获取到Everything窗口标题: {window_title}")
            if "1.5" in window_title:
                return 1, 5
            elif "Everything" in window_title:
                return 1, 4
        else:
            logger.warning("无法获取窗口标题")
        
        # 检查进程命令行参数
        try:
            cmdline = proc.cmdline()
            logger.info(f"进程命令行: {cmdline}")
            for arg in cmdline:
                if "1.5" in arg:
                    return 1, 5
        except Exception as e:
            logger.warning(f"获取进程命令行失败: {str(e)}")
        
        # 检查进程目录中是否有其他1.5版本的特征文件
        try:
            for file in os.listdir(exe_dir):
                if "1.5" in file or "Everything3" in file:
                    logger.info(f"在进程目录中发现1.5版本特征文件: {file}")
                    return 1, 5
        except Exception as e:
            logger.warning(f"检查进程目录文件失败: {str(e)}")
        
        # 最后尝试使用win32api获取文件版本
        # 注意：win32api获取的版本可能不准确（显示1.4但DLL是1.5）
        # 所以只在其他方法都失败时才使用
        try:
            import win32api
            info = win32api.GetFileVersionInfo(exe_path, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            major = (ms >> 16) & 0xffff
            minor = (ms & 0xffff)
            logger.info(f"从文件版本获取Everything版本: ({major}, {minor})")
            # 如果文件版本显示1.4，但目录中有1.5的DLL，优先信任DLL检测
            # （因为1.5便携版可能文件版本仍显示1.4）
            if major == 1 and minor == 4:
                # 再次确认没有1.5的DLL
                if os.path.exists(dll_path_1_5):
                    logger.info(f"文件版本显示1.4，但检测到1.5 DLL，优先使用1.5")
                    return 1, 5
            return major, minor
        except Exception as e:
            logger.warning(f"使用win32api获取版本失败: {str(e)}")
        
        logger.warning("无法确定Everything版本，默认返回1.4")
        return 1, 4
    except Exception as e:
        logger.error(f"获取进程版本时出错: {str(e)}")
        return None

def detect_everything_version() -> Dict[str, any]:
    """
    检测Everything版本信息
    :return: 包含版本信息的字典
    """
    # 首先尝试从安装路径获取版本
    version = get_everything_version()
    install_path = get_everything_install_path()
    logger.info(f"从安装路径获取的版本: {version}")
    logger.info(f"安装路径: {install_path}")
    
    # 检测正在运行的Everything进程
    running_process = get_running_everything_process()
    is_running = running_process is not None
    process_version = None
    
    if is_running:
        process_version = get_process_version(running_process)
        logger.info(f"检测到正在运行的Everything进程，版本: {process_version}")
        # 尝试直接检查进程的可执行文件路径（用于日志记录）
        try:
            exe_path = running_process.exe()
            logger.info(f"Everything进程可执行文件路径: {exe_path}")
            exe_dir = os.path.dirname(exe_path)
            logger.info(f"进程所在目录: {exe_dir}")
            dll_1_5_path = os.path.join(exe_dir, "Everything3_x64.dll")
            if os.path.exists(dll_1_5_path):
                logger.info(f"在进程目录中检测到1.5版本DLL: {dll_1_5_path}")
            else:
                logger.info(f"在进程目录中未找到1.5版本DLL: {dll_1_5_path}")
        except Exception as e:
            logger.error(f"检查进程目录时出错: {str(e)}")
    
    # 优先使用进程版本（如果正在运行）
    if process_version:
        version = process_version
        logger.info(f"优先使用进程版本: {version}")
    
    result = {
        "installed": version is not None,
        "install_path": install_path,
        "version": version,
        "major_version": version[0] if version else None,
        "minor_version": version[1] if version else None,
        "is_1_5": version == (1, 5) if version else False,
        "is_1_4": version == (1, 4) if version else False,
        "is_running": is_running,
        "process_version": process_version
    }
    
    logger.info(f"最终检测结果: {result}")
    return result
