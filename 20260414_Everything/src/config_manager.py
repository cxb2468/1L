#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
用于管理应用的配置文件，包括工具栏按钮的配置
"""

import os
import json
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('config_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self):
        """
        初始化配置管理器
        """
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "toolbar_buttons": [
                {
                    "text": "🖼️ 今天修改的图片",
                    "search_query": "*.jpg|*.jpeg|*.png|*.gif|*.bmp|*.webp|*.svg|*.ico|*.tiff|*.raw dm:today",
                    "bg_color": "#3498db",
                    "hover_color": "#2980b9",
                    "text_color": "white"
                },
                {
                    "text": "📄 今天修改的文档",
                    "search_query": "*.pdf|*.doc|*.docx|*.txt|*.xls|*.xlsx|*.ppt|*.pptx|*.md|*.rtf dm:today",
                    "bg_color": "#2ecc71",
                    "hover_color": "#27ae60",
                    "text_color": "white"
                },
                {
                    "text": "🎬 今天修改的视频",
                    "search_query": "*.mp4|*.avi|*.mkv|*.mov|*.wmv|*.flv|*.webm|*.m4v|*.mpg|*.mpeg dm:today",
                    "bg_color": "#e74c3c",
                    "hover_color": "#c0392b",
                    "text_color": "white"
                },
                {
                    "text": "🎵 今天修改的音频",
                    "search_query": "*.mp3|*.wav|*.flac|*.aac|*.ogg|*.wma|*.m4a|*.opus dm:today",
                    "bg_color": "#9b59b6",
                    "hover_color": "#8e44ad",
                    "text_color": "white"
                },
                {
                    "text": "📦 今天修改的压缩包",
                    "search_query": "*.zip|*.rar|*.7z|*.tar|*.gz|*.bz2|*.xz|*.iso dm:today",
                    "bg_color": "#f39c12",
                    "hover_color": "#e67e22",
                    "text_color": "white"
                },
                {
                    "text": "⚙️ 今天修改的程序",
                    "search_query": "*.exe|*.msi|*.bat|*.cmd|*.ps1|*.sh|*.com dm:today",
                    "bg_color": "#95a5a6",
                    "hover_color": "#7f8c8d",
                    "text_color": "white"
                },
                {
                    "text": "🕐 今天修改",
                    "search_query": "dm:today",
                    "bg_color": "#34495e",
                    "hover_color": "#2c3e50",
                    "text_color": "white"
                },
                {
                    "text": "📏 今天访问的大文件",
                    "search_query": "size:>100MB da:today",
                    "bg_color": "#e67e22",
                    "hover_color": "#d35400",
                    "text_color": "white"
                }
            ],
            "window": {
                "width": 1200,
                "height": 700,
                "title": "Everything搜索助手"
            },
            "tips": "就绪 - 点击列标题可排序，多条件用 | 分隔表示'或'"
        }
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        :return: 配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"成功加载配置文件: {self.config_file}")
                    return config
            except Exception as e:
                logger.error(f"加载配置文件时出错: {str(e)}，使用默认配置")
                return self.default_config
        else:
            # 如果配置文件不存在，创建默认配置
            logger.info(f"配置文件不存在，创建默认配置: {self.config_file}")
            self._save_config(self.default_config)
            return self.default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """
        保存配置文件
        :param config: 配置字典
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存配置文件: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件时出错: {str(e)}")
    
    def get_toolbar_buttons(self) -> List[Dict[str, Any]]:
        """
        获取工具栏按钮配置
        :return: 按钮配置列表
        """
        return self.config.get("toolbar_buttons", self.default_config["toolbar_buttons"])
    
    def set_toolbar_buttons(self, buttons: List[Dict[str, Any]]):
        """
        设置工具栏按钮配置
        :param buttons: 按钮配置列表
        """
        self.config["toolbar_buttons"] = buttons[:50]  # 最多50个按钮
        self._save_config(self.config)
    
    def get_window_config(self) -> Dict[str, Any]:
        """
        获取窗口配置
        :return: 窗口配置字典
        """
        return self.config.get("window", self.default_config["window"])
    
    def set_window_config(self, window_config: Dict[str, Any]):
        """
        设置窗口配置
        :param window_config: 窗口配置字典
        """
        self.config["window"] = window_config
        self._save_config(self.config)
    
    def get_toolbar_config(self) -> Dict[str, Any]:
        """
        获取工具栏配置
        :return: 工具栏配置字典
        """
        default_toolbar = {"buttons_per_row": 5}
        return self.config.get("toolbar", default_toolbar)
    
    def set_toolbar_config(self, toolbar_config: Dict[str, Any]):
        """
        设置工具栏配置
        :param toolbar_config: 工具栏配置字典
        """
        self.config["toolbar"] = toolbar_config
        self._save_config(self.config)
    
    def get_column_widths(self) -> Dict[str, int]:
        """
        获取列表列宽配置
        :return: 列宽配置字典
        """
        default_widths = {
            "name": 250,
            "path": 550,
            "size": 100,
            "date": 150
        }
        return self.config.get("column_widths", default_widths)
    
    def set_column_widths(self, column_widths: Dict[str, int]):
        """
        设置列表列宽配置
        :param column_widths: 列宽配置字典
        """
        self.config["column_widths"] = column_widths
        self._save_config(self.config)
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置
        :return: 完整配置字典
        """
        return self.config
    
    def set_config(self, config: Dict[str, Any]):
        """
        设置完整配置
        :param config: 完整配置字典
        """
        self.config = config
        self._save_config(self.config)
    
    def reset_config(self):
        """
        重置配置为默认值
        """
        self.config = self.default_config
        self._save_config(self.config)
