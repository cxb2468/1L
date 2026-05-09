#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源文件管理模块
用于管理和复制资源文件，确保程序能正确使用所需的资源
"""

import os
import shutil
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resource_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResourceManager:
    """
    资源文件管理类
    负责从ref_materials复制资源到项目内的适当目录
    """
    
    def __init__(self):
        """
        初始化资源管理器
        """
        # 定义目录路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ref_materials_dir = os.path.join(self.base_dir, 'ref_materials')
        self.resources_dir = os.path.join(self.base_dir, 'resources')
        self.dll_dir = os.path.join(self.resources_dir, 'dll')
        
        # 确保资源目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        确保资源目录存在
        """
        for directory in [self.resources_dir, self.dll_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
    
    def copy_dll_files(self):
        """
        复制DLL文件从ref_materials到resources/dll目录
        :return: 复制是否成功
        """
        try:
            # 定义需要复制的DLL文件
            dll_files = [
                'Everything64.dll',      # 1.4版本
                'Everything3_x64.dll'    # 1.5版本
            ]
            
            success = True
            for dll_file in dll_files:
                source_path = os.path.join(self.ref_materials_dir, dll_file)
                target_path = os.path.join(self.dll_dir, dll_file)
                
                # 检查源文件是否存在
                if not os.path.exists(source_path):
                    logger.warning(f"源DLL文件不存在: {source_path}")
                    success = False
                    continue
                
                # 检查目标文件是否存在，以及是否需要更新
                need_copy = True
                if os.path.exists(target_path):
                    # 比较文件修改时间
                    source_mtime = os.path.getmtime(source_path)
                    target_mtime = os.path.getmtime(target_path)
                    if source_mtime <= target_mtime:
                        logger.info(f"DLL文件已最新: {dll_file}")
                        need_copy = False
                
                if need_copy:
                    # 复制文件
                    shutil.copy2(source_path, target_path)
                    logger.info(f"已复制DLL文件: {dll_file} 到 {target_path}")
            
            return success
        except Exception as e:
            logger.error(f"复制DLL文件时出错: {str(e)}")
            return False
    
    def get_dll_path(self, version):
        """
        获取指定版本的DLL文件路径
        :param version: Everything版本，'1.4' 或 '1.5'
        :return: DLL文件路径，如果不存在返回None
        """
        if version == '1.4':
            dll_file = 'Everything64.dll'
        elif version == '1.5':
            dll_file = 'Everything3_x64.dll'
        else:
            logger.error(f"不支持的版本: {version}")
            return None
        
        dll_path = os.path.join(self.dll_dir, dll_file)
        if os.path.exists(dll_path):
            return dll_path
        else:
            logger.warning(f"DLL文件不存在: {dll_path}")
            # 尝试复制DLL文件
            if self.copy_dll_files():
                if os.path.exists(dll_path):
                    return dll_path
            return None
    
    def get_resource_path(self, resource_name):
        """
        获取资源文件路径
        :param resource_name: 资源文件名
        :return: 资源文件路径，如果不存在返回None
        """
        resource_path = os.path.join(self.resources_dir, resource_name)
        if os.path.exists(resource_path):
            return resource_path
        else:
            # 尝试从ref_materials复制
            source_path = os.path.join(self.ref_materials_dir, resource_name)
            if os.path.exists(source_path):
                try:
                    shutil.copy2(source_path, resource_path)
                    logger.info(f"已复制资源文件: {resource_name} 到 {resource_path}")
                    return resource_path
                except Exception as e:
                    logger.error(f"复制资源文件时出错: {str(e)}")
                    return None
            else:
                logger.warning(f"资源文件不存在: {resource_name}")
                return None
    
    def clean_resources(self):
        """
        清理资源文件（可选）
        :return: 清理是否成功
        """
        try:
            if os.path.exists(self.resources_dir):
                shutil.rmtree(self.resources_dir)
                logger.info(f"已清理资源目录: {self.resources_dir}")
            return True
        except Exception as e:
            logger.error(f"清理资源时出错: {str(e)}")
            return False

# 测试函数
def test_resource_manager():
    """
    测试资源管理器功能
    """
    manager = ResourceManager()
    
    # 测试复制DLL文件
    print("测试复制DLL文件...")
    manager.copy_dll_files()
    
    # 测试获取DLL路径
    print("测试获取DLL路径...")
    dll_1_4 = manager.get_dll_path('1.4')
    print(f"1.4版本DLL路径: {dll_1_4}")
    
    dll_1_5 = manager.get_dll_path('1.5')
    print(f"1.5版本DLL路径: {dll_1_5}")
    
    # 测试清理资源
    # print("测试清理资源...")
    # manager.clean_resources()

if __name__ == "__main__":
    test_resource_manager()
