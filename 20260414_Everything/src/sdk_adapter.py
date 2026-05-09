#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everything SDK适配器
用于适配不同版本的Everything SDK并管理其运行状态
支持同时尝试1.4和1.5版本通信
"""

import os
import subprocess
import ctypes
import logging
from typing import Dict, Optional, List, Any, Tuple
from resource_manager import ResourceManager
import psutil

# 初始化模块级别的日志器
logger = logging.getLogger(__name__)

class EverythingSDKAdapter:
    """Everything SDK适配器类 - 支持多版本并行检测"""
    
    def __init__(self, version_info: Dict[str, Any]):
        """
        初始化SDK适配器
        :param version_info: 版本信息字典
        """
        self.version_info = version_info
        self.install_path = version_info.get("install_path")
        self.resource_manager = ResourceManager()
        
        # 同时加载两个版本的SDK
        self.sdk_1_4 = None
        self.sdk_1_5 = None
        self.sdk_1_4_path = None
        self.sdk_1_5_path = None
        
        # 加载SDK
        self._load_both_sdks()
        
        # 缓存检测结果
        self._last_check_result = False
        self._last_check_time = 0
        
    def _load_both_sdks(self):
        """
        同时加载1.4和1.5版本的SDK
        """
        # 尝试加载1.4 SDK
        try:
            dll_path = self.resource_manager.get_dll_path('1.4')
            if not dll_path:
                # 尝试其他路径
                dll_path = self._find_dll_in_paths("Everything64.dll")
            
            if dll_path and os.path.exists(dll_path):
                self.sdk_1_4 = ctypes.CDLL(dll_path)
                self.sdk_1_4_path = dll_path
                logger.info(f"成功加载1.4版本SDK: {dll_path}")
        except Exception as e:
            logger.warning(f"加载1.4 SDK失败: {e}")
        
        # 尝试加载1.5 SDK
        try:
            dll_path = self.resource_manager.get_dll_path('1.5')
            if not dll_path:
                # 尝试其他路径
                dll_path = self._find_dll_in_paths("Everything3_x64.dll")
            
            if dll_path and os.path.exists(dll_path):
                self.sdk_1_5 = ctypes.CDLL(dll_path)
                self.sdk_1_5_path = dll_path
                logger.info(f"成功加载1.5版本SDK: {dll_path}")
        except Exception as e:
            logger.warning(f"加载1.5 SDK失败: {e}")
    
    def _find_dll_in_paths(self, dll_name: str) -> Optional[str]:
        """
        在多个路径中查找DLL
        """
        # 获取所有可能的Everything进程路径
        process_paths = self._get_everything_process_paths()
        
        search_paths = []
        
        # 添加进程所在目录
        for proc_path in process_paths:
            search_paths.append(os.path.join(os.path.dirname(proc_path), dll_name))
        
        # 添加安装目录
        if self.install_path:
            search_paths.append(os.path.join(self.install_path, dll_name))
        
        # 添加默认路径
        search_paths.extend([
            f"C:/Program Files/Everything/{dll_name}",
            f"C:/Program Files (x86)/Everything/{dll_name}",
        ])
        
        # 添加资源目录
        resource_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'dll', dll_name)
        search_paths.append(os.path.abspath(resource_path))
        
        for path in search_paths:
            if path and os.path.exists(path):
                return path
        return None
    
    def _get_everything_process_paths(self) -> List[str]:
        """
        获取所有Everything进程的可执行文件路径
        """
        paths = []
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    if proc.info['name'] == 'Everything.exe':
                        exe_path = proc.info.get('exe')
                        if exe_path:
                            paths.append(exe_path)
                except:
                    pass
        except Exception as e:
            logger.warning(f"获取Everything进程路径失败: {e}")
        return paths
    
    def find_everything_exe_from_registry(self) -> Optional[str]:
        """
        从注册表查找Everything安装路径
        :return: Everything.exe完整路径或None
        """
        import winreg
        
        # 尝试多个注册表位置
        registry_paths = [
            # App Paths (最可靠)
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Everything.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\Everything.exe"),
            # Everything自己的注册表项
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Everything"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Everything"),
            # 卸载信息
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Everything"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Everything"),
        ]
        
        for hkey, key_path in registry_paths:
            try:
                key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                try:
                    # 尝试获取默认值（App Paths）
                    exe_path, _ = winreg.QueryValueEx(key, "")
                    if exe_path and os.path.exists(exe_path):
                        winreg.CloseKey(key)
                        logger.info(f"从注册表找到Everything: {exe_path}")
                        return exe_path
                except:
                    pass
                
                try:
                    # 尝试获取InstallLocation
                    install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
                    if install_path:
                        exe_path = os.path.join(install_path, "Everything.exe")
                        if os.path.exists(exe_path):
                            winreg.CloseKey(key)
                            logger.info(f"从注册表找到Everything: {exe_path}")
                            return exe_path
                except:
                    pass
                
                try:
                    # 尝试获取DisplayIcon
                    icon_path, _ = winreg.QueryValueEx(key, "DisplayIcon")
                    if icon_path and "Everything.exe" in icon_path:
                        # DisplayIcon可能包含逗号和索引，需要处理
                        exe_path = icon_path.split(',')[0]
                        if os.path.exists(exe_path):
                            winreg.CloseKey(key)
                            logger.info(f"从注册表找到Everything: {exe_path}")
                            return exe_path
                except:
                    pass
                
                winreg.CloseKey(key)
            except:
                pass
        
        return None
    
    def find_everything_exe(self) -> Optional[str]:
        """
        查找Everything.exe的完整路径（多种方式）
        :return: Everything.exe完整路径或None
        """
        # 1. 首先尝试从注册表查找
        exe_path = self.find_everything_exe_from_registry()
        if exe_path:
            return exe_path
        
        # 2. 尝试从进程查找
        process_paths = self._get_everything_process_paths()
        for proc_path in process_paths:
            if os.path.exists(proc_path):
                return proc_path
        
        # 3. 尝试从安装路径查找
        if self.install_path:
            exe_path = os.path.join(self.install_path, "Everything.exe")
            if os.path.exists(exe_path):
                return exe_path
        
        # 4. 尝试默认安装路径
        default_paths = [
            r"C:\Program Files\Everything\Everything.exe",
            r"C:\Program Files (x86)\Everything\Everything.exe",
        ]
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_everything_running(self) -> bool:
        """
        检查Everything是否在运行并可通信
        尝试1.4和1.5两种通信方式，任一成功即返回True
        同时记录成功通信的版本
        :return: 是否可以成功通信
        """
        # 检查缓存（避免过于频繁的检测）
        import time
        current_time = time.time()
        if current_time - self._last_check_time < 1.0:  # 1秒内使用缓存
            return self._last_check_result
        
        self._last_check_time = current_time
        
        # 重置通信版本
        self._last_communication_version = None
        
        # 尝试1.5版本通信
        if self._try_1_5_communication():
            self._last_check_result = True
            self._last_communication_version = "1.5"
            logger.info("Everything 1.5 通信成功")
            return True
        
        # 尝试1.4版本通信
        if self._try_1_4_communication():
            self._last_check_result = True
            self._last_communication_version = "1.4"
            logger.info("Everything 1.4 通信成功")
            return True
        
        self._last_check_result = False
        self._last_communication_version = None
        logger.warning("所有通信方式均失败")
        return False
    
    def _try_1_5_communication(self) -> bool:
        """
        尝试使用1.5版本SDK通信
        """
        if not self.sdk_1_5:
            return False
        
        try:
            # 尝试连接
            self.sdk_1_5.Everything3_ConnectW.restype = ctypes.c_void_p
            
            # 尝试不同的实例名称
            instance_names = [None, "1.5a", "1.5"]
            client = None
            
            for instance_name in instance_names:
                client = self.sdk_1_5.Everything3_ConnectW(instance_name)
                if client and client != 0:
                    break
            
            if not client or client == 0:
                return False
            
            try:
                # 尝试创建搜索状态来验证通信
                self.sdk_1_5.Everything3_CreateSearchState.restype = ctypes.c_void_p
                search_state = self.sdk_1_5.Everything3_CreateSearchState()
                
                if search_state:
                    # 通信成功
                    try:
                        self.sdk_1_5.Everything3_DestroySearchState.argtypes = [ctypes.c_void_p]
                        self.sdk_1_5.Everything3_DestroySearchState(search_state)
                    except:
                        pass
                    
                    # 断开连接
                    try:
                        self.sdk_1_5.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
                        self.sdk_1_5.Everything3_DestroyClient(client)
                    except:
                        pass
                    
                    return True
                else:
                    # 创建搜索状态失败
                    try:
                        self.sdk_1_5.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
                        self.sdk_1_5.Everything3_DestroyClient(client)
                    except:
                        pass
                    return False
                    
            except Exception as e:
                logger.warning(f"1.5通信验证异常: {e}")
                try:
                    self.sdk_1_5.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
                    self.sdk_1_5.Everything3_DestroyClient(client)
                except:
                    pass
                return False
                
        except Exception as e:
            logger.warning(f"1.5通信尝试失败: {e}")
            return False
    
    def _try_1_4_communication(self) -> bool:
        """
        尝试使用1.4版本SDK通信
        """
        if not self.sdk_1_4:
            return False
        
        try:
            # 设置搜索查询
            self.sdk_1_4.Everything_SetSearchW("")
            self.sdk_1_4.Everything_SetRequestFlags(0x00000001)
            
            # 尝试执行查询
            query_result = self.sdk_1_4.Everything_QueryW(True)
            
            if query_result:
                return True
            else:
                # 查询失败，检查错误码
                error_code = self.sdk_1_4.Everything_GetLastError()
                if error_code == 0:
                    # 查询成功但无结果
                    return True
                else:
                    logger.warning(f"1.4查询失败，错误码: {error_code}")
                    return False
                    
        except Exception as e:
            logger.warning(f"1.4通信尝试失败: {e}")
            return False
    
    def get_communication_version(self) -> Optional[str]:
        """
        获取当前成功通信的版本
        优先使用最后一次检测时记录的版本
        :return: "1.4", "1.5" 或 None
        """
        # 优先使用已记录的版本（避免重复检测）
        if hasattr(self, '_last_communication_version') and self._last_communication_version:
            return self._last_communication_version
        
        # 如果没有记录，重新检测
        if self._try_1_5_communication():
            self._last_communication_version = "1.5"
            return "1.5"
        if self._try_1_4_communication():
            self._last_communication_version = "1.4"
            return "1.4"
        return None
    
    def search(self, query: str, sort_by: str = 'name', sort_ascending: bool = True) -> List[Dict[str, Any]]:
        """
        执行搜索 - 自动选择可用的SDK版本
        """
        results = []
        
        # 优先尝试1.5版本
        if self._try_1_5_communication():
            return self._search_1_5(query, sort_by, sort_ascending)
        
        # 然后尝试1.4版本
        if self._try_1_4_communication():
            return self._search_1_4(query, sort_by, sort_ascending)
        
        logger.error("没有可用的Everything通信方式")
        return results
    
    def _search_1_5(self, query: str, sort_by: str, sort_ascending: bool) -> List[Dict[str, Any]]:
        """
        使用1.5版本SDK搜索
        """
        results = []
        
        try:
            logger.info(f"使用1.5版SDK搜索: {query}")
            
            # 连接
            self.sdk_1_5.Everything3_ConnectW.restype = ctypes.c_void_p
            client = self.sdk_1_5.Everything3_ConnectW(None)
            if not client or client == 0:
                client = self.sdk_1_5.Everything3_ConnectW("1.5a")
            
            if not client or client == 0:
                logger.error("1.5连接失败")
                return results
            
            try:
                # 创建搜索状态
                self.sdk_1_5.Everything3_CreateSearchState.restype = ctypes.c_void_p
                search_state = self.sdk_1_5.Everything3_CreateSearchState()
                
                if not search_state:
                    logger.error("1.5创建搜索状态失败")
                    return results
                
                try:
                    # 设置搜索参数
                    self.sdk_1_5.Everything3_SetSearchTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
                    self.sdk_1_5.Everything3_SetSearchTextW(search_state, query)
                    
                    # 设置排序
                    sort_property_map = {'name': 0, 'path': 1, 'size': 2, 'date': 5}
                    property_id = sort_property_map.get(sort_by, 0)
                    self.sdk_1_5.Everything3_SetSearchSort.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_bool]
                    self.sdk_1_5.Everything3_SetSearchSort(search_state, property_id, sort_ascending)
                    
                    # 请求属性
                    self.sdk_1_5.Everything3_AddSearchPropertyRequest.argtypes = [ctypes.c_void_p, ctypes.c_uint]
                    for prop_id in [0, 1, 2, 5, 8]:  # name, path, size, date, attributes
                        self.sdk_1_5.Everything3_AddSearchPropertyRequest(search_state, prop_id)
                    
                    # 设置视口
                    self.sdk_1_5.Everything3_SetSearchViewportOffset.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
                    self.sdk_1_5.Everything3_SetSearchViewportOffset(search_state, 0)
                    self.sdk_1_5.Everything3_SetSearchViewportCount.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
                    self.sdk_1_5.Everything3_SetSearchViewportCount(search_state, 10000)
                    
                    # 执行搜索
                    self.sdk_1_5.Everything3_Search.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
                    self.sdk_1_5.Everything3_Search.restype = ctypes.c_void_p
                    result_list = self.sdk_1_5.Everything3_Search(client, search_state)
                    
                    if not result_list:
                        logger.error("1.5搜索失败")
                        return results
                    
                    try:
                        # 获取结果数量
                        self.sdk_1_5.Everything3_GetResultListViewportCount.argtypes = [ctypes.c_void_p]
                        self.sdk_1_5.Everything3_GetResultListViewportCount.restype = ctypes.c_size_t
                        viewport_count = self.sdk_1_5.Everything3_GetResultListViewportCount(result_list)
                        
                        logger.info(f"1.5搜索结果: {viewport_count}")
                        
                        # 获取结果
                        for i in range(viewport_count):
                            try:
                                # 获取路径
                                path_buf = ctypes.create_unicode_buffer(1024)
                                self.sdk_1_5.Everything3_GetResultPropertyTextW.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_size_t]
                                self.sdk_1_5.Everything3_GetResultPropertyTextW.restype = ctypes.c_size_t
                                
                                self.sdk_1_5.Everything3_GetResultPropertyTextW(result_list, i, 1, path_buf, 1024)
                                path_part = path_buf.value
                                
                                # 获取文件名
                                name_buf = ctypes.create_unicode_buffer(1024)
                                self.sdk_1_5.Everything3_GetResultPropertyTextW(result_list, i, 0, name_buf, 1024)
                                name_part = name_buf.value
                                
                                # 组合路径
                                if path_part and name_part:
                                    full_path = os.path.join(path_part, name_part)
                                elif name_part:
                                    full_path = name_part
                                else:
                                    continue
                                
                                # 获取大小
                                self.sdk_1_5.Everything3_GetResultPropertyUINT64.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint]
                                self.sdk_1_5.Everything3_GetResultPropertyUINT64.restype = ctypes.c_uint64
                                file_size = self.sdk_1_5.Everything3_GetResultPropertyUINT64(result_list, i, 2)
                                
                                # 获取日期
                                date_modified_val = self.sdk_1_5.Everything3_GetResultPropertyUINT64(result_list, i, 5)
                                
                                # 获取属性
                                self.sdk_1_5.Everything3_GetResultPropertyDWORD.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint]
                                self.sdk_1_5.Everything3_GetResultPropertyDWORD.restype = ctypes.c_uint32
                                attributes = self.sdk_1_5.Everything3_GetResultPropertyDWORD(result_list, i, 8)
                                is_folder = bool(attributes & 0x10)
                                
                                # 转换日期
                                date_modified = None
                                if date_modified_val:
                                    try:
                                        import datetime
                                        WINDOWS_TICKS = int(1 / 10 ** -7)
                                        WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                                        POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                                        EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()
                                        WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS
                                        microsecs = (date_modified_val - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
                                        date_modified = datetime.datetime.fromtimestamp(microsecs)
                                    except:
                                        pass
                                
                                results.append({
                                    'full_path_name': full_path,
                                    'file_name': os.path.basename(full_path),
                                    'dir_name': os.path.dirname(full_path),
                                    'file_size': file_size,
                                    'date_modified': date_modified,
                                    'is_folder': is_folder
                                })
                            except Exception as e:
                                logger.error(f"获取1.5结果[{i}]出错: {e}")
                                continue
                        
                    finally:
                        if result_list:
                            try:
                                self.sdk_1_5.Everything3_DestroyResultList.argtypes = [ctypes.c_void_p]
                                self.sdk_1_5.Everything3_DestroyResultList(result_list)
                            except:
                                pass
                finally:
                    if search_state:
                        try:
                            self.sdk_1_5.Everything3_DestroySearchState.argtypes = [ctypes.c_void_p]
                            self.sdk_1_5.Everything3_DestroySearchState(search_state)
                        except:
                            pass
            finally:
                if client:
                    try:
                        self.sdk_1_5.Everything3_DestroyClient.argtypes = [ctypes.c_void_p]
                        self.sdk_1_5.Everything3_DestroyClient(client)
                    except:
                        pass
        except Exception as e:
            logger.error(f"1.5搜索出错: {e}")
        
        return results
    
    def _search_1_4(self, query: str, sort_by: str, sort_ascending: bool) -> List[Dict[str, Any]]:
        """
        使用1.4版本SDK搜索
        """
        results = []
        
        try:
            logger.info(f"使用1.4版SDK搜索: {query}")
            
            # 设置请求标志
            EVERYTHING_REQUEST_FILE_NAME = 0x00000001
            EVERYTHING_REQUEST_PATH = 0x00000002
            EVERYTHING_REQUEST_SIZE = 0x00000010
            EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
            EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
            
            # 设置搜索
            self.sdk_1_4.Everything_SetSearchW(query)
            self.sdk_1_4.Everything_SetRequestFlags(
                EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH |
                EVERYTHING_REQUEST_SIZE | EVERYTHING_REQUEST_DATE_MODIFIED |
                EVERYTHING_REQUEST_ATTRIBUTES
            )
            
            # 设置排序
            sort_map = {'name': (1, 2), 'path': (3, 4), 'size': (5, 6), 'date': (11, 12)}
            sort_asc, sort_desc = sort_map.get(sort_by, (1, 2))
            sort_id = sort_asc if sort_ascending else sort_desc
            self.sdk_1_4.Everything_SetSort(sort_id)
            
            # 执行查询
            query_result = self.sdk_1_4.Everything_QueryW(True)
            if not query_result:
                error_code = self.sdk_1_4.Everything_GetLastError()
                logger.error(f"1.4查询失败，错误码: {error_code}")
                return results
            
            # 获取结果
            count = self.sdk_1_4.Everything_GetNumResults()
            logger.info(f"1.4搜索结果: {count}")
            
            self.sdk_1_4.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
            self.sdk_1_4.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
            
            for i in range(min(count, 10000)):
                try:
                    path = ctypes.create_unicode_buffer(1024)
                    date_modified_filetime = ctypes.c_ulonglong(0)
                    file_size = ctypes.c_ulonglong(0)
                    
                    self.sdk_1_4.Everything_GetResultFullPathNameW(i, path, 1024)
                    full_path = ctypes.wstring_at(path)
                    
                    self.sdk_1_4.Everything_GetResultDateModified(i, ctypes.byref(date_modified_filetime))
                    self.sdk_1_4.Everything_GetResultSize(i, ctypes.byref(file_size))
                    
                    # 判断是否为文件夹
                    is_folder = False
                    try:
                        is_folder = bool(self.sdk_1_4.Everything_IsFolderResult(i))
                    except:
                        try:
                            attrs = self.sdk_1_4.Everything_GetResultAttributes(i)
                            is_folder = bool(attrs & 0x10)
                        except:
                            pass
                    
                    # 转换日期
                    date_modified = None
                    if date_modified_filetime.value:
                        try:
                            import datetime
                            WINDOWS_TICKS = int(1 / 10 ** -7)
                            WINDOWS_EPOCH = datetime.datetime.strptime('1601-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                            POSIX_EPOCH = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
                            EPOCH_DIFF = (POSIX_EPOCH - WINDOWS_EPOCH).total_seconds()
                            WINDOWS_TICKS_TO_POSIX_EPOCH = EPOCH_DIFF * WINDOWS_TICKS
                            microsecs = (date_modified_filetime.value - WINDOWS_TICKS_TO_POSIX_EPOCH) / WINDOWS_TICKS
                            date_modified = datetime.datetime.fromtimestamp(microsecs)
                        except:
                            pass
                    
                    results.append({
                        'full_path_name': full_path,
                        'file_name': os.path.basename(full_path),
                        'dir_name': os.path.dirname(full_path),
                        'file_size': file_size.value,
                        'date_modified': date_modified,
                        'is_folder': is_folder
                    })
                except Exception as e:
                    logger.error(f"获取1.4结果[{i}]出错: {e}")
                    continue
        except Exception as e:
            logger.error(f"1.4搜索出错: {e}")
        
        return results
    
    def start_everything(self, exe_path: Optional[str] = None) -> bool:
        """
        启动Everything
        :param exe_path: 可选，指定Everything.exe路径，如果不指定则自动查找
        :return: 是否启动成功
        """
        # 如果没有指定路径，自动查找
        if not exe_path:
            exe_path = self.find_everything_exe()
        
        if not exe_path or not os.path.exists(exe_path):
            logger.error("未找到Everything.exe")
            return False
        
        try:
            # 获取工作目录（Everything.exe所在目录）
            work_dir = os.path.dirname(exe_path)
            
            # 使用shell=False，设置工作目录
            # 不使用DETACHED_PROCESS，避免权限问题
            subprocess.Popen(
                [exe_path],
                cwd=work_dir,  # 设置工作目录
                creationflags=subprocess.CREATE_NEW_CONSOLE,  # 只使用CREATE_NEW_CONSOLE
                close_fds=True,
                stdout=subprocess.DEVNULL,  # 重定向输出
                stderr=subprocess.DEVNULL
            )
            logger.info(f"启动Everything: {exe_path} (工作目录: {work_dir})")
            return True
        except PermissionError as e:
            logger.error(f"启动Everything权限不足: {e}")
            # 尝试使用shell=True
            try:
                subprocess.Popen(
                    f'"{exe_path}"',
                    cwd=os.path.dirname(exe_path),
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"使用shell模式启动Everything: {exe_path}")
                return True
            except Exception as e2:
                logger.error(f"使用shell模式启动也失败: {e2}")
                return False
        except Exception as e:
            logger.error(f"启动Everything失败: {e}")
            return False
    
    def can_start_everything(self) -> bool:
        """
        检查是否可以启动Everything（是否能找到可执行文件）
        :return: 是否能找到Everything.exe
        """
        return self.find_everything_exe() is not None
    
    def get_sdk_info(self) -> Dict[str, Any]:
        """
        获取SDK信息
        """
        return {
            "sdk_1_4_loaded": self.sdk_1_4 is not None,
            "sdk_1_5_loaded": self.sdk_1_5 is not None,
            "sdk_1_4_path": self.sdk_1_4_path,
            "sdk_1_5_path": self.sdk_1_5_path,
            "can_communicate": self.is_everything_running(),
            "communication_version": self.get_communication_version()
        }
