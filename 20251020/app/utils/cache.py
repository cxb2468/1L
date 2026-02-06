from flask import Flask
from flask_caching import Cache

# 缓存配置
cache = Cache(config={
    'CACHE_TYPE': 'simple',  # 在生产环境中可以使用Redis或Memcached
    'CACHE_DEFAULT_TIMEOUT': 300  # 5分钟默认超时
})


def init_cache(app: Flask):
    """
    初始化缓存
    """
    cache.init_app(app)


def get_cache_key(prefix, **kwargs):
    """
    生成缓存键
    """
    key_parts = [prefix]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return "|".join(key_parts)