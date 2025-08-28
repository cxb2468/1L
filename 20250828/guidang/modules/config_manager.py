# -*- coding: utf-8 -*-
"""
配置管理器模块
负责应用程序配置的保存、加载和管理
"""

import os
import json
from typing import Dict, Any
from pathlib import Path

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # 默认配置文件路径
            self.config_file = os.path.join(
                os.path.expanduser('~'), 
                '.desktop_archive_config.json'
            )
        else:
            self.config_file = config_file
            
        # 默认配置
        self.default_config = {
            'desktop_path': os.path.join(os.path.expanduser('~'), 'Desktop'),
            'archive_path': os.path.join(os.path.expanduser('~'), 'Documents', 'DesktopArchive'),
            'frequency': '每天',
            'hour': '18',
            'minute': '00',
            'include_word': True,
            'include_excel': True,
            'include_ppt': True,
            'include_pdf': True,
            'include_txt': False,
            'organize_by': 'type_and_date',  # 'type', 'date', 'type_and_date'
            'auto_start': False,
            'minimize_to_tray': True,
            'show_notifications': True,
            'backup_before_archive': False,
            'days_before_archive': 7,
            'max_file_size_mb': 100,
            'exclude_patterns': [],  # 排除的文件名模式
            'language': 'zh_CN',
            'theme': 'default',
            'log_level': 'INFO',
            'max_log_files': 10,
            'archive_log_retention_days': 30
        }
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 合并默认配置（确保新增的配置项有默认值）
                merged_config = self.default_config.copy()
                merged_config.update(config)
                
                # 验证配置
                validated_config = self.validate_config(merged_config)
                
                return validated_config
            else:
                # 配置文件不存在，返回默认配置
                return self.default_config.copy()
                
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return self.default_config.copy()
            
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件
        
        Args:
            config: 要保存的配置字典
            
        Returns:
            保存是否成功
        """
        try:
            # 验证配置
            validated_config = self.validate_config(config)
            
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
            
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证和修正配置
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            验证后的配置字典
        """
        validated = config.copy()
        
        # 验证路径
        if 'desktop_path' in validated:
            if not os.path.exists(validated['desktop_path']):
                validated['desktop_path'] = self.default_config['desktop_path']
                
        # 验证归档路径（如果不存在会自动创建）
        if 'archive_path' in validated:
            try:
                os.makedirs(validated['archive_path'], exist_ok=True)
            except:
                validated['archive_path'] = self.default_config['archive_path']
                
        # 验证频率
        valid_frequencies = ['每小时', '每天', '每周', '每月']
        if validated.get('frequency') not in valid_frequencies:
            validated['frequency'] = self.default_config['frequency']
            
        # 验证时间
        try:
            hour = int(validated.get('hour', 18))
            if not (0 <= hour <= 23):
                validated['hour'] = self.default_config['hour']
            else:
                validated['hour'] = str(hour)
        except:
            validated['hour'] = self.default_config['hour']
            
        try:
            minute = int(validated.get('minute', 0))
            if not (0 <= minute <= 59):
                validated['minute'] = self.default_config['minute']
            else:
                validated['minute'] = str(minute).zfill(2)
        except:
            validated['minute'] = self.default_config['minute']
            
        # 验证布尔值
        bool_keys = ['include_word', 'include_excel', 'include_ppt', 'include_pdf', 
                    'include_txt', 'auto_start', 'minimize_to_tray', 'show_notifications',
                    'backup_before_archive']
        for key in bool_keys:
            if key in validated:
                validated[key] = bool(validated[key])
                
        # 验证组织方式
        valid_organize_by = ['type', 'date', 'type_and_date']
        if validated.get('organize_by') not in valid_organize_by:
            validated['organize_by'] = self.default_config['organize_by']
            
        # 验证数值
        try:
            validated['days_before_archive'] = max(0, int(validated.get('days_before_archive', 7)))
        except:
            validated['days_before_archive'] = self.default_config['days_before_archive']
            
        try:
            validated['max_file_size_mb'] = max(1, int(validated.get('max_file_size_mb', 100)))
        except:
            validated['max_file_size_mb'] = self.default_config['max_file_size_mb']
            
        try:
            validated['max_log_files'] = max(1, int(validated.get('max_log_files', 10)))
        except:
            validated['max_log_files'] = self.default_config['max_log_files']
            
        try:
            validated['archive_log_retention_days'] = max(1, int(validated.get('archive_log_retention_days', 30)))
        except:
            validated['archive_log_retention_days'] = self.default_config['archive_log_retention_days']
            
        # 验证排除模式列表
        if 'exclude_patterns' not in validated or not isinstance(validated['exclude_patterns'], list):
            validated['exclude_patterns'] = self.default_config['exclude_patterns']
            
        return validated
        
    def get_file_extensions(self, config: Dict[str, Any]) -> list:
        """根据配置获取要处理的文件扩展名列表
        
        Args:
            config: 配置字典
            
        Returns:
            文件扩展名列表
        """
        extensions = []
        
        if config.get('include_word', True):
            extensions.extend(['.doc', '.docx'])
            
        if config.get('include_excel', True):
            extensions.extend(['.xls', '.xlsx'])
            
        if config.get('include_ppt', True):
            extensions.extend(['.ppt', '.pptx'])
            
        if config.get('include_pdf', True):
            extensions.append('.pdf')
            
        if config.get('include_txt', False):
            extensions.extend(['.txt', '.rtf'])
            
        return extensions
        
    def reset_to_defaults(self) -> Dict[str, Any]:
        """重置为默认配置
        
        Returns:
            默认配置字典
        """
        return self.default_config.copy()
        
    def backup_config(self, backup_path: str = None) -> bool:
        """备份当前配置
        
        Args:
            backup_path: 备份文件路径，如果为None则使用默认路径
            
        Returns:
            备份是否成功
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{self.config_file}.backup_{timestamp}"
                
            if os.path.exists(self.config_file):
                import shutil
                shutil.copy2(self.config_file, backup_path)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"备份配置失败: {str(e)}")
            return False
            
    def restore_config(self, backup_path: str) -> bool:
        """从备份恢复配置
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            恢复是否成功
        """
        try:
            if os.path.exists(backup_path):
                import shutil
                shutil.copy2(backup_path, self.config_file)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"恢复配置失败: {str(e)}")
            return False
            
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定路径
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            导出是否成功
        """
        try:
            config = self.load_config()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"导出配置失败: {str(e)}")
            return False
            
    def import_config(self, import_path: str) -> bool:
        """从指定路径导入配置
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            导入是否成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            return self.save_config(config)
            
        except Exception as e:
            print(f"导入配置失败: {str(e)}")
            return False
            
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息
        
        Returns:
            配置文件信息字典
        """
        info = {
            'config_file_path': self.config_file,
            'config_exists': os.path.exists(self.config_file),
            'config_size': 0,
            'last_modified': None
        }
        
        try:
            if info['config_exists']:
                stat = os.stat(self.config_file)
                info['config_size'] = stat.st_size
                info['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except:
            pass
            
        return info