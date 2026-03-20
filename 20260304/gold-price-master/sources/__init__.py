# coding: utf-8
"""
数据源模块包
包含黄金价格数据获取的相关功能
"""

from .data_source import (
    get_gold_price,
    display_price_info,
    DataFetchError,
    price_cache,
    get_current_data_source,
    set_current_data_source
)

__all__ = [
    'get_gold_price',
    'display_price_info', 
    'DataFetchError',
    'price_cache',
    'get_current_data_source',
    'set_current_data_source'
]