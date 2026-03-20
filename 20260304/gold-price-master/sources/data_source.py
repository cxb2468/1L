# coding: utf-8
"""
黄金价格数据源模块
负责获取和处理黄金价格数据
"""

import time
import requests
from typing import Optional, Dict, Any
from logger.logger_config import get_logger
from config.config import (
    PRICE_CACHE_EXPIRATION,
    GOLD_PRICE_SOURCES,
    DATA_SOURCE_RETRY_COUNT,
    DATA_SOURCE_RETRY_INTERVAL,
    DATA_SOURCE_TIMEOUT,
    DATA_SOURCE_MODE
)

# 获取日志记录器
logger = get_logger(__name__)

# 检查是否有任何配置使用 drissionpage 类型的数据源
_has_drissionpage_source = any(source.get('type') == 'drissionpage' for source in GOLD_PRICE_SOURCES)

# 只有当配置中有 drissionpage 类型的数据源时才导入
if _has_drissionpage_source:
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
    except ImportError as e:
        ChromiumPage = None
        ChromiumOptions = None
        logger.error(f"导入 DrissionPage 失败: {e}")
else:
    ChromiumPage = None
    ChromiumOptions = None

# 时间变量
TIMEOUT = DATA_SOURCE_TIMEOUT  # 通用超时时间（秒）
RETRY_COUNT = DATA_SOURCE_RETRY_COUNT  # 重试次数
RETRY_INTERVAL = DATA_SOURCE_RETRY_INTERVAL  # 重试间隔（秒）

# 在配置模块中添加当前数据源属性
def get_current_data_source():
    """
    获取当前使用的数据源名称
    :return: 当前数据源名称
    """
    import config
    return getattr(config, '_current_data_source', None)

def set_current_data_source(source_name: str):
    """
    设置当前使用的数据源名称
    :param source_name: 数据源名称
    """
    import config
    config._current_data_source = source_name

# 缓存机制
class PriceCache:
    """
    价格缓存类，管理价格数据的缓存
    用于减少重复的网络请求，提高性能
    """
    def __init__(self, expiration: int = PRICE_CACHE_EXPIRATION, max_size: int = 100) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}  # 缓存字典
        self._expiration: int = expiration  # 缓存过期时间（秒）
        self._max_size: int = max_size  # 缓存最大容量
        self._hits: int = 0  # 缓存命中次数
        self._misses: int = 0  # 缓存未命中次数
        self._last_clear_time: float = time.time()  # 上次清空缓存时间
        self._cleanup_threshold: int = max_size * 2  # 清理阈值，超过此值时主动清理过期缓存

    def get(self, key: str) -> Optional[float]:
        """
        获取缓存数据，如果过期则返回None
        :param key: 缓存键
        :return: 缓存值或None
        """
        # 主动清理过期缓存，如果缓存数量超过清理阈值
        if len(self._cache) > self._cleanup_threshold:
            self.cleanup_expired()
        
        if key in self._cache:
            cached_data = self._cache[key]
            if time.time() < cached_data['expires_at']:
                self._hits += 1
                # 更新访问时间，用于LRU策略
                cached_data['last_accessed'] = time.time()
                return cached_data['value']
            else:
                # 缓存已过期，删除它
                del self._cache[key]
                self._misses += 1
        else:
            self._misses += 1
        return None

    def set(self, key: str, value: Optional[float]) -> None:
        """
        设置缓存数据
        :param key: 缓存键
        :param value: 缓存值
        """
        # 只缓存有效的价格数据
        if value is not None and isinstance(value, (int, float)) and value > 0:
            # 检查缓存大小，如果超过最大容量，删除最旧的缓存
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + self._expiration,
                'created_at': time.time(),
                'last_accessed': time.time()
            }
    
    def _evict_oldest(self) -> None:
        """
        移除最旧的缓存项（使用LRU策略）
        """
        if not self._cache:
            return
        
        # 找到最后访问时间最早的缓存项
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k].get('last_accessed', float('inf')))
        
        if oldest_key in self._cache:
            del self._cache[oldest_key]
            logger.debug(f"缓存容量已满，移除最旧的缓存项: {oldest_key}")

    def clear(self) -> None:
        """
        清除所有缓存数据
        """
        cache_size = len(self._cache)
        hit_rate = (self._hits / (self._hits + self._misses) * 100) if (self._hits + self._misses) > 0 else 0
        logger.info(f"缓存已全部清除，共清除 {cache_size} 条记录，命中率: {hit_rate:.2f}%")
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._last_clear_time = time.time()

    def clear_key(self, key: str) -> bool:
        """
        清除指定键的缓存数据
        :param key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]
            logger.info(f"已清除缓存键: {key}")
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """
        清理所有过期的缓存项
        :return: 清理的缓存项数量
        """
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._cache.items():
            if current_time >= data['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存项")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        :return: dict 缓存统计信息
        """
        hit_rate = (self._hits / (self._hits + self._misses) * 100) if (self._hits + self._misses) > 0 else 0
        expired_count = 0
        current_time = time.time()
        
        # 统计过期缓存数量
        for key, data in list(self._cache.items()):
            if current_time >= data['expires_at']:
                expired_count += 1
        
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'expiration': self._expiration,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'expired_count': expired_count,
            'last_clear_time': self._last_clear_time
        }
    
    def force_refresh(self, key: str) -> bool:
        """
        强制刷新指定键的缓存
        :param key: 缓存键
        :return: bool 是否成功刷新
        """
        if key in self._cache:
            del self._cache[key]
            logger.info(f"已强制刷新缓存键: {key}")
            return True
        return False
    
    def is_healthy(self) -> bool:
        """
        检查缓存是否健康
        :return: bool 是否健康
        """
        # 检查缓存大小是否合理
        if len(self._cache) > self._max_size * 1.5:
            logger.warning(f"缓存大小超过最大容量的150%: {len(self._cache)} > {self._max_size * 1.5}")
            return False
        
        # 检查过期缓存比例
        current_time = time.time()
        expired_count = 0
        for key, data in list(self._cache.items()):
            if current_time >= data['expires_at']:
                expired_count += 1
        
        if expired_count > len(self._cache) * 0.5:
            logger.warning(f"过期缓存比例过高: {expired_count}/{len(self._cache)} ({expired_count/len(self._cache)*100:.2f}%)")
            return False
        
        return True

# 创建价格缓存实例
price_cache = PriceCache()  # 使用配置文件中的缓存过期时间


# 统一的数据格式转换函数
def convert_to_standard_format(data: Dict[str, Any], source_name: str) -> Optional[Dict[str, Any]]:
    """
    将各种数据源返回的数据统一转换为标准格式
    :param data: 原始数据
    :param source_name: 数据源名称
    :return: 标准格式的数据
    """
    if not data or 'price' not in data:
        logger.warning(f"{source_name} 返回的数据格式不符合预期，缺少 price 字段")
        return None

    price = data.get('price')
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        logger.warning(f"{source_name} 返回的价格数据无效: {price}")
        return None

    # 返回标准格式
    return {
        "price": float(price),
        "change": data.get('change', ''),
        "change_rate": data.get('change_rate', ''),
        "timestamp": data.get('timestamp', int(time.time())),
        "readable_time": data.get('readable_time', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
        "source": source_name
    }


# 京东 - API 数据源方法
def get_jd_api_price(url: str, name: str) -> Optional[Dict[str, Any]]:
    """
    使用京东API方式获取黄金价格
    :param url: API地址
    :param name: 数据源名称
    :return: 价格数据字典或None
    """
    try:
        # 发送HTTP请求获取数据
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()  # 检查HTTP状态码

        # 解析京东金融API返回的JSON数据
        data = response.json()

        # 检查API返回是否成功
        if data.get('success') and data.get('resultCode') == 0:
            result_data = data.get('resultData', {})
            datas = result_data.get('datas', {})

            # 提取价格数据
            price_str = datas.get('price', '')
            try:
                price = float(price_str)
                if price <= 0:
                    logger.error(f"API获取价格数据异常，获取到的价格为0或负数: {price}")
                    return None

                # 返回包含所有价格相关信息的对象
                result = {
                    "price": price,
                    "change": datas.get('upAndDownAmt', ''),
                    "change_rate": datas.get('upAndDownRate', ''),
                    "timestamp": int(time.time()),
                    "readable_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                logger.info(f"成功从 {name} API获取黄金价格: ¥{price}/克, 涨跌: {datas.get('upAndDownAmt', '')}, 涨跌幅: {datas.get('upAndDownRate', '')}")
                return result
            except ValueError as e:
                logger.error(f"API价格文本转换为数字失败: {e}, 原始文本: {price_str}")
                return None
        else:
            logger.error(f"API返回数据异常，resultCode: {data.get('resultCode')}, resultMsg: {data.get('resultMsg')}")
            return None
    except requests.exceptions.SSLError as e:
        logger.error(f"API SSL证书验证失败: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"API请求超时: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"API网络连接错误: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API HTTP请求异常: {e}")
        return None
    except ValueError as e:
        logger.error(f"API响应解析异常: {e}")
        return None
    except Exception as e:
        logger.error(f"使用API获取数据失败: {e}")
        return None


# 新浪 - 页面抓取数据源方法
def get_sina_page_price(url: str, name: str) -> Optional[Dict[str, Any]]:
    """
    使用DrissionPage从新浪页面获取黄金价格
    :param url: 页面地址
    :param name: 数据源名称
    :return: 价格数据字典或None
    """
    if ChromiumPage is None:
        logger.warning(f"DrissionPage 未导入，无法使用 {name} 数据源")
        return None

    try:
        co = ChromiumOptions()
        co.headless(True)
        co.no_imgs(True)
        co.incognito(True)
        
        page = ChromiumPage(addr_or_opts=co)
        
        page.set.headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

        page.get(url)
        page.wait(2)

        try:
            gc_container = page.ele("#realtimeGC", timeout=20)
            if not gc_container:
                logger.error("无法找到黄金价格容器")
                return None

            price_element = gc_container.ele(".r_g_price_now", timeout=10)
            if price_element:
                price_text = price_element.text
                try:
                    change_element = gc_container.ele(".r_g_price_change", timeout=5)
                    price_change_text = change_element.text if change_element else ""
                except Exception:
                    price_change_text = ""
            else:
                container_text = gc_container.text
                import re
                price_match = re.search(r'\d+\.\d+', container_text)
                if price_match:
                    price_text = price_match.group(0)
                    price_change_text = ""
                else:
                    logger.error("无法从页面提取价格")
                    return None
        except Exception as e:
            logger.error(f"获取价格元素失败: {e}")
            return None

        # 解析价格文本
        if price_text:
            # 移除可能的空格和换行符
            price_text = price_text.strip()
            try:
                price = float(price_text)
                if price <= 0:
                    logger.error(f"DrissionPage获取页面价格数据异常，获取到的价格为0或负数: {price}")
                    return None

                # 返回包含所有价格相关信息的对象
                result = {
                    "price": price,
                    "change": price_change_text.strip() if price_change_text else "",
                    "timestamp": int(time.time()),
                    "readable_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                logger.info(f"成功从 {name} 获取黄金价格: ¥{price}/克")
                return result
            except ValueError as e:
                logger.error(f"价格文本转换为数字失败: {e}, 原始文本: {price_text}")
                return None
        else:
            logger.error("无法解析页面价格数据（DrissionPage方式），未找到有效价格文本")
            return None

    except Exception as e:
        logger.error(f"使用DrissionPage抓取页面失败: {e}")
        return None


# 新浪 - API 数据源方法
def get_sina_api_price(url: str, name: str) -> Optional[Dict[str, Any]]:
    """
    使用新浪API方式获取黄金价格
    :param url: API地址
    :param name: 数据源名称
    :return: 价格数据字典或None
    """
    try:
        # 构造请求参数，获取黄金价格数据
        params = {
            '_': int(time.time()*1000),
            'list': 'gds_AUTD'  # 黄金期货代码
        }
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        # 解析返回的数据
        content = response.text
        
        # 查找黄金价格数据
        # 新浪API返回的是类似 var hq_str_hf_GC="2665.000,2664.000,2681.990,2645.000,2681.990,2682.000,......";
        import re
        match = re.search(r'hq_str_hf_GC="([^"]*)"', content)
        if match:
            data = match.group(1)
            fields = data.split(',')
            if len(fields) >= 3:
                # 第3个字段通常是当日最高价，第4个是最低价，第7个是当前价格
                try:
                    price = float(fields[6]) if len(fields) > 6 else float(fields[0])
                    result = {
                        "price": price,
                        "change": "",  # API返回的数据中可能需要计算涨跌额
                        "change_rate": "",  # 涨跌幅需要进一步计算
                        "timestamp": int(time.time()),
                        "readable_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    }
                    logger.info(f"成功从 {name} API获取黄金价格: ¥{price}/克")
                    return result
                except (ValueError, IndexError) as e:
                    logger.error(f"解析新浪API数据失败: {e}, 数据: {data}")
                    return None
        else:
            logger.error(f"未能从 {name} API获取到黄金价格数据")
            return None
            
    except requests.exceptions.SSLError as e:
        logger.error(f"新浪API SSL证书验证失败: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"新浪API请求超时: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"新浪API网络连接错误: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"新浪API HTTP请求异常: {e}")
        return None
    except Exception as e:
        logger.error(f"使用新浪API获取数据失败: {e}")
        return None


class DataFetchError(Exception):
    """数据获取失败异常"""
    pass


def get_gold_price():
    """
    获取黄金价格的主函数，根据配置模式尝试数据源
    使用缓存机制以提高性能
    :return: 元组 (黄金价格（元/克）, 是否使用缓存) 或抛出异常
    """
    # 检查缓存
    cached_price = price_cache.get('gold_price')
    if cached_price is not None:
        logger.debug(f"使用缓存的金价数据: {cached_price:.2f}/克")
        return cached_price, True
    
    # 重新导入配置以获取最新值
    import config
    current_mode = config.DATA_SOURCE_MODE
    current_sources = config.GOLD_PRICE_SOURCES
    
    # 获取启用的数据源并按排序序号排序
    enabled_sources = [source for source in current_sources if source.get('enabled', True)]
    sorted_sources = sorted(enabled_sources, key=lambda x: x.get('sort_order', 999))
    
    logger.info(f"根据配置，尝试 {len(sorted_sources)} 个启用的数据源，模式: {current_mode}")
    
    # 根据模式选择不同的获取策略
    if current_mode == 'single':
        # 单一获取模式：获取第一个可用数据源的数据
        price = _get_single_source_price(sorted_sources)
        return price, False
    elif current_mode == 'cycle':
        # 循环获取模式：按排序遍历可用数据源，获取到即停止
        price = _get_cycle_source_price(sorted_sources)
        return price, False
    else:
        # 默认使用单一获取模式
        logger.warning(f"未知的数据源模式: {current_mode}，使用默认单一获取模式")
        price = _get_single_source_price(sorted_sources)
        return price, False


def _get_single_source_price(sources):
    """
    单一获取模式：获取第一个可用数据源的数据
    :param sources: 已排序的启用数据源列表
    :return: 黄金价格或抛出异常
    """
    if not sources:
        error_msg = "没有启用的数据源可用"
        logger.error(error_msg)
        raise DataFetchError(error_msg)
    
    # 只尝试第一个数据源
    source_config = sources[0]
    source_name = source_config["name"]
    source_type = source_config["type"]
    source_url = source_config["url"]
    
    logger.info(f"单一获取模式：尝试从 {source_name} ({source_type}) 获取黄金价格")
    
    for retry in range(RETRY_COUNT):
        try:
            # 根据数据源类型调用对应的方法
            raw_data = None
            if source_type == "api":
                # 区分不同的API数据源
                if "京东" in source_name:
                    raw_data = get_jd_api_price(source_url, source_name)
                elif "新浪" in source_name:
                    raw_data = get_sina_api_price(source_url, source_name)
                else:
                    # 默认API处理
                    raw_data = get_jd_api_price(source_url, source_name)
            elif source_type == "drissionpage":
                # 区分不同的页面抓取数据源
                if "新浪" in source_name:
                    raw_data = get_sina_page_price(source_url, source_name)
                else:
                    # 默认页面抓取处理
                    raw_data = get_sina_page_price(source_url, source_name)
            
            # 将原始数据转换为标准格式
            if raw_data is not None:
                standardized_data = convert_to_standard_format(raw_data, source_name)
                if standardized_data is not None:
                    price = standardized_data["price"]
                    # 验证价格有效性
                    if price is not None and isinstance(price, (int, float)) and price > 0:
                        # 更新缓存
                        price_cache.set('gold_price', price)
                        logger.info(f"成功获取黄金价格: ¥{price}/克，来自数据源: {source_name}")
                        return price
                    else:
                        logger.warning(f"从 {source_name} 获取的价格数据无效: {price}")
            else:
                logger.warning(f"从 {source_name} 获取数据失败，第 {retry + 1} 次尝试")
                
        except Exception as e:
            logger.error(f"从 {source_name} 获取数据时发生异常: {e}, 第 {retry + 1} 次尝试")
            
        # 重试前等待
        if retry < RETRY_COUNT - 1:
            time.sleep(RETRY_INTERVAL)
    
    # 第一个数据源失败，抛出异常
    error_msg = f"单一获取模式下，首选数据源 {source_name} 获取失败"
    logger.error(error_msg)
    raise DataFetchError(error_msg)


def _get_cycle_source_price(sources):
    """
    循环获取模式：按排序遍历可用数据源，获取到即停止
    :param sources: 已排序的启用数据源列表
    :return: 黄金价格或抛出异常
    """
    if not sources:
        error_msg = "没有启用的数据源可用"
        logger.error(error_msg)
        raise DataFetchError(error_msg)
    
    logger.info(f"循环获取模式：开始遍历 {len(sources)} 个数据源")
    
    # 遍历所有启用的数据源
    for index, source_config in enumerate(sources):
        source_name = source_config["name"]
        source_type = source_config["type"]
        source_url = source_config["url"]
        
        logger.info(f"尝试从 {source_name} ({source_type}) 获取黄金价格 (第 {index + 1}/{len(sources)} 个)")
        
        for retry in range(RETRY_COUNT):
            try:
                # 根据数据源类型调用对应的方法
                raw_data = None
                if source_type == "api":
                    # 区分不同的API数据源
                    if "京东" in source_name:
                        raw_data = get_jd_api_price(source_url, source_name)
                    elif "新浪" in source_name:
                        raw_data = get_sina_api_price(source_url, source_name)
                    else:
                        # 默认API处理
                        raw_data = get_jd_api_price(source_url, source_name)
                elif source_type == "drissionpage":
                    # 区分不同的页面抓取数据源
                    if "新浪" in source_name:
                        raw_data = get_sina_page_price(source_url, source_name)
                    else:
                        # 默认页面抓取处理
                        raw_data = get_sina_page_price(source_url, source_name)
                
                # 将原始数据转换为标准格式
                if raw_data is not None:
                    standardized_data = convert_to_standard_format(raw_data, source_name)
                    if standardized_data is not None:
                        price = standardized_data["price"]
                        # 验证价格有效性
                        if price is not None and isinstance(price, (int, float)) and price > 0:
                            # 更新缓存
                            price_cache.set('gold_price', price)
                            # 设置当前使用的数据源
                            set_current_data_source(source_name)
                            current_ds = get_current_data_source()
                            logger.info(f"成功获取黄金价格: ¥{price}/克，来自数据源: {source_name}，当前数据源: {current_ds}")
                            return price
                        else:
                            logger.warning(f"从 {source_name} 获取的价格数据无效: {price}")
                else:
                    logger.warning(f"从 {source_name} 获取数据失败，第 {retry + 1} 次尝试")
                    
            except Exception as e:
                logger.error(f"从 {source_name} 获取数据时发生异常: {e}, 第 {retry + 1} 次尝试")
                
            # 重试前等待
            if retry < RETRY_COUNT - 1:
                time.sleep(RETRY_INTERVAL)
        
        # 当前数据源失败，继续尝试下一个
        logger.warning(f"数据源 {source_name} 经过 {RETRY_COUNT} 次重试后仍然失败，尝试下一个数据源")
    
    # 所有数据源都失败，抛出异常
    error_msg = "循环获取模式下，所有数据源获取失败，无法获取黄金价格"
    logger.error(error_msg)
    raise DataFetchError(error_msg)


def display_price_info(price, last_price=None):
    """
    显示价格信息和涨跌情况
    """
    arrow, direction = get_price_arrow(price, last_price)
    return arrow, direction


def get_price_arrow(price, last_price):
    """
    根据当前价格与基准价格比较，判断价格上涨或下跌
    返回相应的箭头符号和描述文字
    """
    # 如果没有上一次价格记录，则认为是持平
    if last_price is None:
        return "(持平)", "持平"

    # 判断涨跌
    if price > last_price:
        return "(上涨)", "上涨"
    elif price < last_price:
        return "(下跌)", "下跌"
    else:
        return "(持平)", "持平"