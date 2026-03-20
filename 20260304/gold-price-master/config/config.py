# 微信公众号配置文件
import os
from typing import List, Dict, Any

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ------------------------------
# 微信公众号基本配置
# ------------------------------
# 多账号配置：定义多个公众号账号的配置信息
MULTI_ACCOUNT_CONFIG: List[Dict[str, str]] = []

# 账号1配置
if os.getenv('WECHAT_APP_ID_1'):
    MULTI_ACCOUNT_CONFIG.append({
        'APP_ID': os.getenv('WECHAT_APP_ID_1', ''),
        'APP_SECRET': os.getenv('WECHAT_APP_SECRET_1', ''),
        'TEMPLATE_ID': os.getenv('WECHAT_TEMPLATE_ID_1', ''),
        'WEB_URL': os.getenv('WECHAT_WEB_URL_1', ''),
        'NAME': os.getenv('WECHAT_ACCOUNT_NAME_1', 'Account 1')
    })

# 账号2配置
if os.getenv('WECHAT_APP_ID_2'):
    MULTI_ACCOUNT_CONFIG.append({
        'APP_ID': os.getenv('WECHAT_APP_ID_2', ''),
        'APP_SECRET': os.getenv('WECHAT_APP_SECRET_2', ''),
        'TEMPLATE_ID': os.getenv('WECHAT_TEMPLATE_ID_2', ''),
        'WEB_URL': os.getenv('WECHAT_WEB_URL_2', ''),
        'NAME': os.getenv('WECHAT_ACCOUNT_NAME_2', 'Account 2')
    })

# 如果没有环境变量配置，使用占位符配置（需要用户配置环境变量）
if not MULTI_ACCOUNT_CONFIG:
    import warnings
    warnings.warn(
        "未检测到微信公众账号环境变量配置。请设置以下环境变量：\n"
        "  - WECHAT_APP_ID_1, WECHAT_APP_SECRET_1, WECHAT_TEMPLATE_ID_1\n"
        "  - WECHAT_WEB_URL_1, WECHAT_ACCOUNT_NAME_1\n"
        "参考 .env.example 文件进行配置。",
        UserWarning
    )
    MULTI_ACCOUNT_CONFIG = [
    {
        'APP_ID': '',  # 公众号AppID
        'APP_SECRET': '',  # 公众号AppSecret
        'TEMPLATE_ID': '',  # 模板消息ID
        'WEB_URL': '',  # 公众号跳转URL
        'NAME': ''  # 账号名称
    },
    {
        'APP_ID': '',  # 公众号AppID
        'APP_SECRET': '',  # 公众号AppSecret
        'TEMPLATE_ID': '',  # 模板消息ID
        'WEB_URL': '',  # 公众号跳转URL
        'NAME': ''  # 账号名称
    }
]

# 为了向后兼容，使用第一个账号作为默认配置
if MULTI_ACCOUNT_CONFIG:
    DEFAULT_ACCOUNT = MULTI_ACCOUNT_CONFIG[0]
    APP_ID = DEFAULT_ACCOUNT['APP_ID']
    APP_SECRET = DEFAULT_ACCOUNT['APP_SECRET']
    TEMPLATE_ID = DEFAULT_ACCOUNT['TEMPLATE_ID']
    WEB_URL = DEFAULT_ACCOUNT['WEB_URL']

# ------------------------------
# 推送时间配置
# ------------------------------
PUSH_START_TIME = '09:00'
PUSH_END_TIME = '23:00'
PUSH_INTERVAL_MINUTES = 30
REGULAR_PUSH_MINUTES = [1,31]
REGULAR_PUSH_WINDOW = 5

# ------------------------------
# 推送频率限制配置
# ------------------------------
MAX_PUSH_COUNT = 1
BATCH_PUSH_INTERVAL = 300
GLOBAL_PUSH_INTERVAL = 300

# ------------------------------
# 黄金价格配置
# ------------------------------
DATA_FETCH_INTERVAL = 300
PRICE_CACHE_EXPIRATION = 60

# ------------------------------
# 黄金价格预警配置
# ------------------------------
DEFAULT_GOLD_PRICE = 1190
DEFAULT_PRICE_GAP_HIGH = 15
DEFAULT_PRICE_GAP_LOW = 10
PRICE_CHANGE_THRESHOLD = 5

# ------------------------------
# 日志配置
# ------------------------------
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/gold_monitor.log'

# ------------------------------
# 测试模式配置
# ------------------------------
TEST_MODE = False

# ------------------------------
# 功能控制配置
# ------------------------------
# 微信推送控制
ENABLE_WECHAT_PUSH = os.getenv('ENABLE_WECHAT_PUSH', 'True').lower() in ('true', '1', 'yes')

# HTML文件生成控制
ENABLE_HTML_GENERATION = True

# GUI窗口显示控制
ENABLE_GUI_WINDOW = False

# Windows可执行文件编译控制
ENABLE_COMPILE = False

# Windows 可执行文件运行控制
ENABLE_RUN_EXE = False

# ------------------------------
# AI 大模型配置
# ------------------------------
ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'False').lower() in ('true', '1', 'yes')

# ------------------------------
# 配置页面密码
# ------------------------------
CONFIG_PASSWORD = 'admin888'

# ------------------------------
# AI大模型配置
# ------------------------------
ENABLE_AI_ANALYSIS = False

# ------------------------------
# 黄金价格数据源配置
# ------------------------------
# 数据源类型定义
DATA_SOURCE_TYPES: Dict[str, str] = {
    "api": "API接口",
    "drissionpage": "页面抓取"
}

# 数据源获取模式
DATA_SOURCE_MODES: Dict[str, str] = {
    "single": "单一获取",
    "cycle": "循环获取"
}

# 数据源配置：定义多个黄金价格数据源
GOLD_PRICE_SOURCES: List[Dict[str, Any]] = [
    {
        "name": "京东金融-黄金API",
        "url": "https://ms.jr.jd.com/gw/generic/hj/h5/m/latestPrice",
        "type": "api",
        "enabled": True,
        "sort_order": 1
    },
    {
        "name": "黄金价格|白银价格",
        "url": "https://finance.sina.com.cn/nmetal/",
        "type": "drissionpage",
        "enabled": False,
        "sort_order": 2
    },
    {
        "name": "新浪-股票|基金API",
        "url": "https://hq.sinajs.cn/",
        "type": "api",
        "enabled": False,
        "sort_order": 3
    }
]

# 数据源获取配置
DATA_SOURCE_MODE = 'single'
DATA_SOURCE_RETRY_COUNT = 3
DATA_SOURCE_RETRY_INTERVAL = 2
DATA_SOURCE_TIMEOUT = 10

# coding: utf-8
"""
配置文件
管理API密钥和其他配置参数
"""

# 注意：os 和 typing 已在文件开头导入

class Config:
    """配置类"""
    
    # 阿里云百炼配置
    ALIYUN_API_KEY = os.getenv('ALIYUN_API_KEY', '')  # 从环境变量获取
    
    # 百度文心一言配置
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', '')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', '')
    
    # 讯飞星火配置
    XUNFEI_API_KEY = os.getenv('XUNFEI_API_KEY', '')
    
    # AI 大模型配置
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'False').lower() in ('true', '1', 'yes')
    
    # 应用配置
    MAX_ANALYSIS_LENGTH = 200  # 最大分析文字长度
    REQUEST_TIMEOUT = 10       # 请求超时时间（秒）
    RETRY_COUNT = 3           # 重试次数
    
    @classmethod
    def is_configured(cls) -> bool:
        """检查是否配置了至少一个AI服务"""
        return any([
            cls.ALIYUN_API_KEY,
            cls.BAIDU_API_KEY and cls.BAIDU_SECRET_KEY,
            cls.XUNFEI_API_KEY
        ])
    
    @classmethod
    def get_available_services(cls) -> list:
        """获取可用的服务列表"""
        services = []
        if cls.ALIYUN_API_KEY:
            services.append("阿里云百炼")
        if cls.BAIDU_API_KEY and cls.BAIDU_SECRET_KEY:
            services.append("百度文心一言")
        if cls.XUNFEI_API_KEY:
            services.append("讯飞星火")
        return services

# 全局配置实例
config = Config()

# 配置变更日志记录
import logging
from datetime import datetime

def log_config_change(config_name: str, old_value: Any, new_value: Any) -> None:
    """
    记录配置变更日志
    :param config_name: 配置项名称
    :param old_value: 旧值
    :param new_value: 新值
    """
    try:
        logger = logging.getLogger('config')
        if logger is None:
            logger = logging.getLogger()
        
        change_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"[配置变更] {change_time} - {config_name}: {old_value} -> {new_value}")
    except Exception as e:
        # 记录异常而不是静默忽略
        logging.error(f"记录配置变更日志失败: {e}")

def validate_push_config() -> tuple:
    """
    验证推送时间配置的有效性
    :return: (is_valid, message) 元组
    """
    try:
        # 验证时间格式
        from datetime import time as dt_time
        
        start_time = dt_time.fromisoformat(PUSH_START_TIME)
        end_time = dt_time.fromisoformat(PUSH_END_TIME)
        
        # 验证分钟点
        for minute in REGULAR_PUSH_MINUTES:
            if not isinstance(minute, int) or minute < 0 or minute > 59:
                return False, f"推送分钟点无效: {minute}，应在0-59之间"
        
        # 验证推送窗口
        if REGULAR_PUSH_WINDOW < 0 or REGULAR_PUSH_WINDOW > 60:
            return False, f"推送窗口无效: {REGULAR_PUSH_WINDOW}，应在0-60之间"
        
        # 验证间隔配置
        if PUSH_INTERVAL_MINUTES < 1:
            return False, f"推送间隔无效: {PUSH_INTERVAL_MINUTES}，应大于0"
        
        if MAX_PUSH_COUNT < 1:
            return False, f"最大推送次数无效: {MAX_PUSH_COUNT}，应大于0"
        
        # 验证价格预警配置
        if DEFAULT_PRICE_GAP_HIGH < 0:
            return False, f"上涨浮动差额无效: {DEFAULT_PRICE_GAP_HIGH}，应大于等于0"
        
        if DEFAULT_PRICE_GAP_LOW < 0:
            return False, f"下跌浮动差额无效: {DEFAULT_PRICE_GAP_LOW}，应大于等于0"
        
        return True, "配置验证通过"
        
    except ValueError as e:
        return False, f"时间格式无效: {e}"
    except Exception as e:
        return False, f"配置验证失败: {e}"

def get_config_value(config_name: str, default: Any = None) -> Any:
    """
    获取配置值
    :param config_name: 配置项名称
    :param default: 默认值
    :return: 配置值
    """
    try:
        if hasattr(config, config_name):
            return getattr(config, config_name)
        elif config_name in dir():
            return eval(config_name)
        else:
            return default
    except (AttributeError, NameError, SyntaxError):
        return default
    except Exception as e:
        # 记录异常而不是静默忽略
        logging.error(f"获取配置值失败: {e}")
        return default

def set_config_value(config_name: str, value: Any) -> bool:
    """
    设置配置值
    :param config_name: 配置项名称
    :param value: 要设置的值
    :return: 是否设置成功
    """
    try:
        old_value = get_config_value(config_name)
        if old_value == value:
            return True
        
        if hasattr(config, config_name):
            setattr(config, config_name, value)
        elif config_name in dir():
            exec(f"{config_name} = {repr(value)}")
        else:
            return False
        
        log_config_change(config_name, old_value, value)
        return True
    except AttributeError:
        return False
    except Exception as e:
        # 记录异常而不是静默忽略
        logging.error(f"设置配置值失败: {e}")
        return False