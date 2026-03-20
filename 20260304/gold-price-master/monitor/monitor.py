# 核心监控逻辑模块
import time
import json
import os
import sys
from datetime import datetime, time as dt_time
import importlib

# 导入配置模块
import config

# 导入配置文件（主循环之前使用的变量）
from config import (
    ENABLE_COMPILE, ENABLE_RUN_EXE
)
# 导入数据获取和处理模块
from sources.data_source import get_gold_price, display_price_info, DataFetchError
# 导入黄金预警管理器
from gold_alert import gold_alert_manager
# 导入消息发送模块
from wechat.message import MessageSender
# 导入日志配置
from logger.logger_config import get_logger
# 导入工具函数
from utils.utils import build_message_data, send_push_message, is_push_blocked
# 导入JSON调度器
from utils.json_scheduler import json_scheduler

# 获取日志记录器
logger = get_logger(__name__)

# 全局变量
last_price = None  # 记录上一次的价格，用于比较价格变化
first_run = True  # 标记是否为首次运行

# 监控状态变量
last_data_fetch_time = 0  # 上次数据抓取时间
last_json_generate_time = 0  # 上次JSON生成时间
last_health_check_time = 0  # 上次健康检查时间

# 消息发送实例 - 延迟初始化，在run_gold_price_monitor函数中创建
message_sender = None

# 健康检查配置
HEALTH_CHECK_INTERVAL = 300  # 健康检查间隔（秒）
MAX_DATA_FETCH_INTERVAL = 600  # 最大数据抓取间隔（秒）
MAX_JSON_GENERATE_INTERVAL = 900  # 最大JSON生成间隔（秒）

# 导入价格缓存
from sources.data_source import price_cache

def perform_health_check(current_time):
    """
    执行健康检查
    :param current_time: 当前时间戳
    """
    try:
        logger.info("执行健康检查")
        
        # 检查数据抓取时间
        if current_time - last_data_fetch_time > MAX_DATA_FETCH_INTERVAL:
            logger.warning(f"数据抓取时间间隔过长: {current_time - last_data_fetch_time:.2f}秒 > {MAX_DATA_FETCH_INTERVAL}秒")
        else:
            logger.debug(f"数据抓取时间间隔正常: {current_time - last_data_fetch_time:.2f}秒")
        
        # 检查JSON生成时间
        if current_time - last_json_generate_time > MAX_JSON_GENERATE_INTERVAL:
            logger.warning(f"JSON生成时间间隔过长: {current_time - last_json_generate_time:.2f}秒 > {MAX_JSON_GENERATE_INTERVAL}秒")
        else:
            logger.debug(f"JSON生成时间间隔正常: {current_time - last_json_generate_time:.2f}秒")
        
        # 检查缓存健康状态
        try:
            cache_stats = price_cache.get_stats()
            logger.info(f"缓存状态: 大小={cache_stats['size']}, 命中率={cache_stats['hit_rate']:.2f}%, 过期={cache_stats['expired_count']}")
            
            if not price_cache.is_healthy():
                logger.warning("缓存状态不健康，正在清理过期缓存")
                cleaned_count = price_cache.cleanup_expired()
                logger.info(f"清理了 {cleaned_count} 个过期缓存")
            
        except Exception as e:
            logger.error(f"检查缓存状态失败: {e}", exc_info=True)  # 记录完整的异常信息
        
        # 检查JSON调度器状态
        try:
            write_status = json_scheduler.get_write_status()
            logger.info(f"JSON调度器状态: 队列大小={write_status['queue_size']}, 成功={write_status['write_success_count']}, 失败={write_status['write_error_count']}")
            
            if write_status['write_error_count'] > 5:
                logger.warning("JSON写入错误次数过多，可能存在问题")
                # 尝试重置JSON调度器状态
                try:
                    json_scheduler.reset_status()
                    logger.info("已重置JSON调度器状态")
                except Exception as reset_error:
                    logger.error(f"重置JSON调度器状态失败: {reset_error}")
            
        except Exception as e:
            logger.error(f"检查JSON调度器状态失败: {e}", exc_info=True)  # 记录完整的异常信息
    except Exception as e:
        logger.error(f"执行健康检查时发生异常: {e}", exc_info=True)  # 记录完整的异常信息

def generate_initial_json_data(price=None):
    """
    程序启动时生成初始JSON数据文件
    :param price: 初始价格（可选）
    :return: JSON文件路径或None
    """
    try:
        logger.info("程序启动，生成初始JSON数据文件")
        
        # 构建初始数据
        initial_data_entry = {
            'timestamp': int(time.time()),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price_data': {
                'price': price,  # 使用传入的价格
                'last_price': price,
                'timestamp': int(time.time()),
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '程序启动'
            },
            'message_data': None
        }
        
        # 强制生成初始JSON文件，传入初始数据
        file_path = json_scheduler.force_generate(initial_data_entry)
        if file_path:
            logger.info(f"初始JSON数据文件生成成功: {file_path}")
            # 更新JSON生成时间戳
            global last_json_generate_time
            last_json_generate_time = time.time()
            logger.debug(f"更新JSON生成时间戳: {last_json_generate_time}")
            return file_path
        else:
            logger.warning("初始JSON数据文件生成失败")
            return None
            
    except Exception as e:
        logger.error(f"生成初始JSON数据失败: {e}", exc_info=True)  # 记录完整的异常信息
        return None

def is_within_push_time(push_start_time, push_end_time, test_mode=False):
    """
    检查当前时间是否在推送时间范围内（工作日）
    :param push_start_time: 推送开始时间
    :param push_end_time: 推送结束时间
    :param test_mode: 测试模式
    :return: bool 是否在推送时间范围内
    """
    # 获取当前日期和时间
    current_datetime = datetime.now()
    now = current_datetime.time()
    weekday = current_datetime.weekday()  # 获取星期几，0=周一，4=周五，5=周六，6=周日
    
    # 检查是否为工作日（周一到周五）
    if weekday > 4:  # 周六或周日
        logger.debug(f"当前为非工作日（{weekday}），跳过推送")
        return False
    
    # 如果是测试模式，记录日志但不忽略时间限制
    if test_mode:
        logger.info("[测试模式] 按照正常时间范围进行推送")
    
    start_time = dt_time.fromisoformat(push_start_time)
    end_time = dt_time.fromisoformat(push_end_time)
    
    # 处理跨日期的情况（例如：22:00 到 06:00）
    if start_time <= end_time:
        # 不跨日期，正常区间判断
        return start_time <= now <= end_time
    else:
        # 跨日期，例如 22:00 到 06:00
        return now >= start_time or now <= end_time

def is_push_minute(regular_push_minutes, regular_push_window, test_mode=False, last_push_status=-1):
    """
    检查当前时间是否应该进行定期推送
    逻辑：
    1. 检查当前时间是否在配置的推送分钟点的时间窗口内
    2. 确保每个推送周期只推送一次
    :param regular_push_minutes: 定期推送分钟点
    :param regular_push_window: 推送时间窗口
    :param test_mode: 测试模式
    :param last_push_status: 上次推送状态
    :return: bool 是否为推送分钟
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    # 解析上次推送的小时和分钟
    if last_push_status > 100:
        last_push_hour = last_push_status // 100
        last_push_min = last_push_status % 100
    else:
        # 兼容旧格式
        last_push_hour = -1
        last_push_min = last_push_status
    
    # 检查当前推送周期是否已经推送过
    # 推送周期是指：当前小时的当前分钟（测试模式下）或配置的推送分钟点（正式模式下）
    if test_mode:
        # 测试模式下，每个小时只推送一次
        current_push_cycle = current_hour
        last_push_cycle = last_push_hour
        logger.info("[测试模式] 忽略推送分钟限制，允许随时推送，但每个小时只推送一次")
    else:
        # 正式模式下，检查当前时间是否在配置的推送分钟点的时间窗口内
        # 计算当前应该推送的分钟点
        should_push = False
        target_minute = None
        
        for push_min in regular_push_minutes:
            # 计算推送窗口的开始和结束时间
            window_start = push_min
            window_end = push_min + regular_push_window
            
            # 处理分钟值超过59的边界情况
            if window_end > 59:
                window_end = 59
            
            # 检查当前分钟是否在推送窗口内
            if window_start <= current_minute <= window_end:
                should_push = True
                target_minute = push_min
                break
        
        if not should_push:
            return False
        
        # 正式模式下，推送周期是当前小时的当前推送分钟点
        current_push_cycle = current_hour * 100 + target_minute
        last_push_cycle = last_push_hour * 100 + last_push_min if last_push_hour != -1 else -1
    
    # 如果当前推送周期已经推送过，直接返回False
    if current_push_cycle == last_push_cycle:
        logger.debug(f"当前推送周期 {current_push_cycle} 已经推送过，跳过本次推送")
        return False
    
    # 当前时间符合推送条件，允许推送
    return True

def send_regular_price_update(price, arrow):
    """
    发送定期价格更新消息
    :param price: 当前价格
    :param arrow: 价格变化箭头
    :return: 推送结果
    """
    # 使用工具函数构建消息数据
    message_data = build_message_data(price, arrow, gold_alert_manager, push_type="regular")
    
    # 使用通用推送函数发送消息
    result = send_push_message(message_sender, message_data, push_type="regular")
    
    # 返回推送结果，由调用方决定如何处理
    return result

def generate_error_html(generate_type, error_message):
    """
    生成包含错误信息的HTML文件
    :param generate_type: 生成类型
    :param error_message: 错误信息
    :return: None
    """
    if generate_type:
        from generate_html import HTMLGenerator
        html_generator = HTMLGenerator()
        
        # 生成包含错误信息的HTML
        html_data = {
            'error': error_message
        }
        
        html_path = html_generator.generate_html(html_data)
        if html_path:
            logger.info(f"成功生成错误HTML文件: {html_path}")
        else:
            logger.error("生成HTML文件失败")

def run_gold_price_monitor():
    """
    运行黄金价格监控循环
    根据需求调整逻辑：
    1. 每5分钟抓取一次黄金价格数据
    2. 在指定时间点（每小时01分和31分）进行定期推送
    3. 当价格达到预警阈值时立即推送（不影响定时推送规则）
    4. 生成HTML文件用于Web预览（根据配置）
    5. 编译Windows运行文件（根据配置）
    """
    # 声明全局变量
    global last_price, message_sender
    
    # 重新导入配置变量，确保使用最新值
    from config.config import (
        ENABLE_COMPILE, ENABLE_RUN_EXE
    )
    
    # 在程序启动时检查并重置过期的推送阻止文件
    from utils import check_and_reset_expired_block
    check_and_reset_expired_block()
    
    # 初始化消息发送实例
    if message_sender is None:
        message_sender = MessageSender()
    
    # 检查是否在PyInstaller打包环境中
    is_pyinstaller = getattr(sys, 'frozen', False)
    
    # 编译Windows运行文件（根据配置，只执行一次，且不在PyInstaller环境中执行）
    if ENABLE_COMPILE and not is_pyinstaller:
        logger.info("开始编译Windows运行文件...")
        try:
            from utils.windows_compile import WindowsCompiler
            compiler = WindowsCompiler()
            if compiler.compile(onefile=True, console=True):
                logger.info("Windows运行文件编译成功")
            else:
                logger.error("Windows运行文件编译失败")
                logger.error("编译失败，程序将停止运行")
                return  # 编译失败，停止程序运行
        except Exception as e:
            logger.error(f"编译Windows运行文件时发生异常: {e}")
            logger.error("编译失败，程序将停止运行")
            return
    elif ENABLE_COMPILE and is_pyinstaller:
        logger.info("在PyInstaller环境中运行，跳过编译步骤")
    elif not ENABLE_COMPILE:
        logger.info("ENABLE_COMPILE=False，跳过编译Windows运行文件，只运行监控逻辑")
    
    # 1. 先获取当前金价（用于初始JSON数据）
    initial_price = None
    try:
        logger.info("准备获取初始金价")
        price_result = get_gold_price()
        # 处理返回值，可能是元组(price, is_cache)或单个price
        if isinstance(price_result, tuple):
            initial_price, _ = price_result
        else:
            initial_price = price_result
        logger.info(f"初始金价获取成功: {initial_price}")
    except Exception as e:
        logger.warning(f"初始金价获取失败，使用默认值: {e}")
    
    # 2. 程序启动时生成初始JSON数据（传入获取的价格）
    logger.info("准备调用初始JSON数据生成函数")
    generate_initial_json_data(initial_price)
    logger.info("初始JSON数据生成函数调用完成")
    
    # 主循环
    logger.info("进入主循环")
    loop_count = 0
    last_loop_time = time.time()
    
    while True:
        # 重新加载配置模块，确保获取最新的配置值
        try:
            # 先检查sys.modules中是否有config模块
            if 'config' in sys.modules:
                # 如果有，先删除它，然后重新导入
                del sys.modules['config']
            # 重新导入config模块
            import config
            # 然后重新加载它，确保获取最新的配置值
            importlib.reload(config)
        except Exception as e:
            logger.error(f"重新加载配置模块失败: {e}")
            # 如果重新加载失败，尝试直接导入config模块
            try:
                import config
            except Exception as e2:
                logger.error(f"导入config模块失败: {e2}")
                # 如果导入也失败，使用默认值
                PUSH_START_TIME = "09:00"
                PUSH_END_TIME = "23:00"
                REGULAR_PUSH_MINUTES = [1, 31]
                REGULAR_PUSH_WINDOW = 5
                DATA_FETCH_INTERVAL = 300
                MULTI_ACCOUNT_CONFIG = []
                PUSH_INTERVAL_MINUTES = 30
                MAX_PUSH_COUNT = 1
                BATCH_PUSH_INTERVAL = 300
                GLOBAL_PUSH_INTERVAL = 300
                PRICE_CACHE_EXPIRATION = 60
                DEFAULT_GOLD_PRICE = 1100.0
                DEFAULT_PRICE_GAP_HIGH = 15.0
                DEFAULT_PRICE_GAP_LOW = 10.0
                PRICE_CHANGE_THRESHOLD = 5
                ENABLE_WECHAT_PUSH = False
                ENABLE_AI_ANALYSIS = False
                ENABLE_HTML_GENERATION = True
                ENABLE_GUI_WINDOW = False
                TEST_MODE = False
                LOG_LEVEL = "INFO"
                LOG_FILE = "logs/gold_monitor.log"
                DATA_SOURCE_MODE = "single"
                DATA_SOURCE_RETRY_COUNT = 3
                DATA_SOURCE_RETRY_INTERVAL = 2
                DATA_SOURCE_TIMEOUT = 10
                GOLD_PRICE_SOURCES = []
                logger.warning("使用默认配置值，因为无法导入config模块")
                continue
        
        # 从配置模块获取最新配置值
        PUSH_START_TIME = config.PUSH_START_TIME
        PUSH_END_TIME = config.PUSH_END_TIME
        REGULAR_PUSH_MINUTES = config.REGULAR_PUSH_MINUTES
        REGULAR_PUSH_WINDOW = config.REGULAR_PUSH_WINDOW
        DATA_FETCH_INTERVAL = config.DATA_FETCH_INTERVAL
        MULTI_ACCOUNT_CONFIG = config.MULTI_ACCOUNT_CONFIG
        PUSH_INTERVAL_MINUTES = config.PUSH_INTERVAL_MINUTES
        MAX_PUSH_COUNT = config.MAX_PUSH_COUNT
        BATCH_PUSH_INTERVAL = config.BATCH_PUSH_INTERVAL
        GLOBAL_PUSH_INTERVAL = config.GLOBAL_PUSH_INTERVAL
        PRICE_CACHE_EXPIRATION = config.PRICE_CACHE_EXPIRATION
        DEFAULT_GOLD_PRICE = config.DEFAULT_GOLD_PRICE
        DEFAULT_PRICE_GAP_HIGH = config.DEFAULT_PRICE_GAP_HIGH
        DEFAULT_PRICE_GAP_LOW = config.DEFAULT_PRICE_GAP_LOW
        PRICE_CHANGE_THRESHOLD = config.PRICE_CHANGE_THRESHOLD
        LOG_LEVEL = config.LOG_LEVEL
        LOG_FILE = config.LOG_FILE
        TEST_MODE = config.TEST_MODE
        ENABLE_WECHAT_PUSH = config.ENABLE_WECHAT_PUSH
        ENABLE_HTML_GENERATION = config.ENABLE_HTML_GENERATION
        ENABLE_GUI_WINDOW = config.ENABLE_GUI_WINDOW
        ENABLE_COMPILE = config.ENABLE_COMPILE
        ENABLE_RUN_EXE = config.ENABLE_RUN_EXE
        
        # 验证配置的有效性
        try:
            from config import validate_push_config
            is_valid, error_message = validate_push_config()
            if not is_valid:
                logger.error(f"配置验证失败: {error_message}")
                # 使用默认配置值
                logger.warning("使用默认配置值，因为当前配置无效")
                PUSH_START_TIME = "09:00"
                PUSH_END_TIME = "23:00"
                REGULAR_PUSH_MINUTES = [1, 31]
                REGULAR_PUSH_WINDOW = 5
                PUSH_INTERVAL_MINUTES = 30
            else:
                logger.debug(f"配置验证通过: {error_message}")
        except ImportError:
            logger.warning("配置验证功能不可用，跳过验证")
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
        
        loop_count += 1
        current_loop_time = time.time()
        loop_duration = current_loop_time - last_loop_time
        last_loop_time = current_loop_time
        
        if loop_count % 10 == 0:
            logger.info(f"主循环第 {loop_count} 次执行，上次循环耗时: {loop_duration:.2f}秒")
            logger.info(f"当前配置状态: 微信推送={ENABLE_WECHAT_PUSH}, HTML生成={ENABLE_HTML_GENERATION}, GUI窗口={ENABLE_GUI_WINDOW}, 编译EXE={ENABLE_COMPILE}")
        
        # 健康检查
        current_time = time.time()
        global last_health_check_time
        if current_time - last_health_check_time >= HEALTH_CHECK_INTERVAL:
            perform_health_check(current_time)
            last_health_check_time = current_time
        
        try:
            # 检查是否被禁止推送
            if is_push_blocked():
                logger.warning("当天推送已禁止，跳过本次循环")
                time.sleep(DATA_FETCH_INTERVAL)
                continue
            
            # 1. 获取当前金价
            price = None
            is_cache_data = False
            try:
                price_result = get_gold_price()
                # 处理返回值，可能是元组(price, is_cache)或单个price
                if isinstance(price_result, tuple):
                    price, is_cache_data = price_result
                else:
                    price = price_result
                # 更新数据抓取时间戳
                global last_data_fetch_time
                last_data_fetch_time = time.time()
                logger.debug(f"更新数据抓取时间戳: {last_data_fetch_time}")
            except DataFetchError as e:
                logger.error(f"获取金价失败: {e}", exc_info=True)  # 记录完整的异常信息
                # 生成错误HTML
                if ENABLE_HTML_GENERATION:
                    generate_error_html(ENABLE_HTML_GENERATION, str(e))
                
                # 检查是否是页面抓取方式失败
                error_msg = str(e)
                if "页面抓取方式获取黄金价格失败" in error_msg or "API方式获取黄金价格失败" in error_msg:
                    logger.error("优先数据源获取失败，尝试使用备用数据源")
                    # 不停止程序，让程序继续运行并在下次循环中重试
                    # 清理资源
                    try:
                        json_scheduler.shutdown()
                    except Exception as shutdown_error:
                        logger.error(f"关闭JSON调度器时发生异常: {shutdown_error}")
                    time.sleep(10)
                    continue
                
                logger.warning("无法获取金价数据，程序将继续运行并稍后重试")
                time.sleep(10)
                continue
            except Exception as e:
                logger.error(f"获取金价时发生未知异常: {e}", exc_info=True)  # 记录完整的异常信息
                # 生成错误HTML
                if ENABLE_HTML_GENERATION:
                    generate_error_html(ENABLE_HTML_GENERATION, f"获取金价时发生异常: {str(e)}")
                
                logger.warning("无法获取金价数据，程序将继续运行并稍后重试")
                time.sleep(10)
                continue

            # 构建价格数据对象
            # 对于首次运行，使用当前价格作为last_price
            if last_price is None:
                current_last_price = price
            else:
                current_last_price = last_price
            
            price_data = {
                'price': price,
                'last_price': current_last_price,
                'timestamp': int(time.time()),
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 记录当前价格用于下次比较
            last_price = price
            
            # 初始化消息数据为None
            message_data = None

            # 2. 检查预警条件（立即推送）
            within_push_time = is_within_push_time(PUSH_START_TIME, PUSH_END_TIME, TEST_MODE)
            alert_failed = False
            alert_error_message = ""
            original_base_price = gold_alert_manager.dynamic_base_price
            arrow = ""
            direction = ""
            
            # 只有当ENABLE_WECHAT_PUSH为True时才进行微信消息推送（包括预警推送）
            if ENABLE_WECHAT_PUSH and not is_push_blocked() and within_push_time and price is not None:
                # 正常情况下的数据处理
                # 显示价格信息并获取价格变化趋势
                arrow, direction = display_price_info(price, last_price)
                
                # 保存原始的dynamic_base_price，用于HTML生成
                original_base_price = gold_alert_manager.dynamic_base_price
                
                # 尝试检查预警条件，但即使失败也不影响程序继续运行
                try:
                    alert_result = gold_alert_manager.check_alert_conditions(price)
                    
                    # 构建消息数据对象
                    if alert_result:
                        message_data = {
                            'alert_type': 'price_alert',
                            'success': alert_result.get('success', True),
                            'reason': alert_result.get('reason', ''),
                            'price': price,
                            'base_price': gold_alert_manager.dynamic_base_price
                        }
                    
                    # 检查预警推送是否失败
                    if alert_result and not alert_result.get('success', True):
                        logger.warning(f"预警推送失败: {alert_result.get('reason', '未知错误')}")
                        alert_failed = True
                        alert_error_message = alert_result.get('reason', '未知错误')
                except Exception as e:
                    logger.error(f"检查预警条件时发生异常: {e}")
                    alert_failed = True
                    alert_error_message = f"检查预警条件失败: {str(e)}"
            elif not ENABLE_WECHAT_PUSH:
                # 当ENABLE_WECHAT_PUSH为False时，只更新价格信息，不进行微信消息推送（包括预警推送）
                if loop_count % 30 == 0:  # 每30次循环记录一次，减少日志输出
                    logger.info("ENABLE_WECHAT_PUSH=False，跳过微信消息推送，只处理价格数据")
                arrow, direction = display_price_info(price, last_price)
                original_base_price = gold_alert_manager.dynamic_base_price
                # 手动更新动态基础价格
                gold_alert_manager.dynamic_base_price = price

            # 3. 生成HTML文件（根据配置，不受时间范围和微信推送逻辑影响）
            if ENABLE_HTML_GENERATION:
                try:
                    from generate_html import HTMLGenerator
                    html_generator = HTMLGenerator()
                    
                    # 检查是否被禁止推送（可能在获取价格或执行其他操作期间被设置）
                    if is_push_blocked():
                        # 被禁止推送时，显示错误信息
                        html_data = {
                            'error': '当天已被禁止推送'
                        }
                    elif price is None:
                        # 无法获取价格数据时，显示错误信息
                        html_data = {
                            'error': '无法获取黄金价格数据'
                        }
                    elif alert_failed:
                        # 预警推送失败时，仍然显示正常的价格数据，但添加推送错误信息
                        try:
                            from ai.ai_analyzer import get_gold_analysis
                            html_ai_analysis = get_gold_analysis(price, last_price, direction if direction else "稳定")
                        except Exception as e:
                            logger.warning(f"获取AI分析失败: {e}")
                            html_ai_analysis = "AI分析暂时不可用"
                        html_data = {
                            'price': price,
                            'current_price': price,
                            'last_price': last_price,
                            'base_price': original_base_price,
                            'ai_analysis': html_ai_analysis,
                            'push_error': alert_error_message  # 添加推送错误信息
                        }
                    else:
                        # 生成HTML时使用原始的base_price，这样可以显示预警信息
                        # 获取AI分析建议用于HTML显示
                        try:
                            from ai.ai_analyzer import get_gold_analysis
                            html_ai_analysis = get_gold_analysis(price, last_price, direction if direction else "稳定")
                        except Exception as e:
                            logger.warning(f"获取AI分析失败: {e}")
                            html_ai_analysis = "AI分析暂时不可用"
                        html_data = {
                            'price': price,
                            'current_price': price,
                            'last_price': last_price,
                            'base_price': original_base_price,
                            'ai_analysis': html_ai_analysis
                        }
                    
                    html_path = html_generator.generate_html(html_data)
                    if html_path:
                        if loop_count % 10 == 0:
                            logger.info(f"成功生成HTML文件: {html_path}")
                    else:
                        logger.error("生成HTML文件失败")
                except Exception as e:
                    logger.error(f"生成HTML文件时发生异常: {e}")
            
            # 4. 使用JSON调度器管理数据生成
            try:
                # 只要数据获取成功（price不为None）且不是缓存数据，就添加到待处理队列
                if price is not None and not is_cache_data:
                    json_scheduler.add_data(price_data, message_data)
                    
                    # 检查是否应该生成JSON文件
                    if json_scheduler.should_generate():
                        file_path = json_scheduler.generate_json_file()
                        if file_path:
                            # 更新JSON生成时间戳
                            global last_json_generate_time
                            last_json_generate_time = time.time()
                            logger.debug(f"更新JSON生成时间戳: {last_json_generate_time}")
                            if loop_count % 10 == 0:
                                pending_count = json_scheduler.get_pending_count()
                                logger.info(f"JSON数据文件已更新: {file_path}，待处理数据: {pending_count}条")
                        else:
                            logger.warning("生成JSON文件失败")
            except Exception as e:
                logger.error(f"处理JSON数据时发生异常: {e}", exc_info=True)  # 记录完整的异常信息
                
                # 尝试清理JSON调度器资源
                try:
                    json_scheduler.shutdown()
                except Exception as shutdown_error:
                    logger.error(f"关闭JSON调度器时发生异常: {shutdown_error}")

            # 5. 检查推送失败后是否被阻止
            if is_push_blocked():
                logger.warning("由于推送失败，当天已被禁止推送")
                # 生成错误HTML但不停止程序，让程序继续运行以便在明天自动恢复
                if ENABLE_HTML_GENERATION:
                    generate_error_html(ENABLE_HTML_GENERATION, '当天已被禁止推送')
            else:
                # 处理价格获取成功的后续逻辑
                if price is not None:
                    # 检查是否需要进行定期推送（只有当ENABLE_WECHAT_PUSH为True时才执行）
                    if ENABLE_WECHAT_PUSH and within_push_time:
                        # 检查当前是否为推送分钟
                        if is_push_minute(REGULAR_PUSH_MINUTES, REGULAR_PUSH_WINDOW, TEST_MODE, gold_alert_manager.push_status_manager.last_regular_push_minute):
                            try:
                                # 如果之前没有获取价格变化趋势，现在获取
                                if not arrow:
                                    arrow, direction = display_price_info(price, last_price)
                                # 获取AI分析建议
                                try:
                                    from ai.ai_analyzer import get_gold_analysis
                                    ai_analysis = get_gold_analysis(price, last_price, direction)
                                except Exception as e:
                                    logger.warning(f"获取AI分析失败: {e}")
                                    ai_analysis = "AI分析暂时不可用"
                                # 构建消息数据，包含AI分析
                                message_data = build_message_data(price, arrow, gold_alert_manager, push_type="regular", ai_analysis=ai_analysis)
                                # 发送定期价格更新
                                result = send_push_message(message_sender, message_data, push_type="regular")
                                if result and result.get('success'):
                                    # 更新推送状态
                                    now = datetime.now()
                                    current_minute = now.minute
                                    gold_alert_manager.push_status_manager.reset_regular_push_status(current_minute, price)
                                    logger.info(f"定期推送完成，重置推送状态: 分钟={current_minute}")
                                else:
                                    # 使用新的频率控制处理函数
                                    from utils import handle_push_frequency_control
                                    if handle_push_frequency_control(result, "定期"):
                                        logger.warning("推送被跳过，等待适当时间后重试")
                                        # 等待一段时间再继续，避免死循环
                                        time.sleep(60)  # 等待1分钟
                                    else:
                                        # 如果是其他推送失败，记录失败原因，但不再立即设置全天阻止
                                        error_msg = '未知错误'
                                        if result:
                                            error_msg = result.get('reason') or result.get('error') or '未知错误'
                                        logger.warning(f"定期推送失败: {error_msg}")
                            except Exception as e:
                                logger.error(f"定期推送过程中发生异常: {e}")
        
                # 6. 根据配置的数据获取间隔进行休眠，但要确保不会在推送分钟附近错过推送
                # 无论是否使用缓存数据，都保持适当的执行频率
                sleep_remaining = DATA_FETCH_INTERVAL
                while sleep_remaining > 0:
                    # 检查是否接近推送分钟，如果是则提前唤醒
                    if is_within_push_time(PUSH_START_TIME, PUSH_END_TIME, TEST_MODE) and is_push_minute(REGULAR_PUSH_MINUTES, REGULAR_PUSH_WINDOW, TEST_MODE, gold_alert_manager.push_status_manager.last_regular_push_minute):
                        logger.debug("检测到推送时间点，提前结束休眠")
                        break
                    
                    # 每次休眠1秒，以便更灵活地响应时间变化
                    sleep_time = min(1, sleep_remaining)
                    time.sleep(sleep_time)
                    sleep_remaining -= sleep_time
                
                # 确保每次循环至少有60秒的间隔，避免使用缓存数据时循环过快
                time.sleep(60)
            
            # 即使无法获取价格数据，也继续循环而不是停止程序
            if price is None:
                logger.warning("无法获取金价数据，程序将继续运行并在下次循环中重试")
                # 短暂休眠后继续下一次循环
                time.sleep(10)
                continue
            
            logger.debug("主循环一轮执行完成，准备进入下一轮")

        except KeyboardInterrupt:
            # 处理用户中断
            logger.info("程序已退出")
            break
        except Exception as e:
            # 处理其他异常
            logger.error(f"程序运行异常: {e}", exc_info=True)  # 记录完整的异常信息
            
            # 即使出现异常，也要生成包含错误信息的HTML页面
            if ENABLE_HTML_GENERATION:
                generate_error_html(ENABLE_HTML_GENERATION, f'程序运行异常: {str(e)}')
            
            # 检查是否被禁止推送
            if is_push_blocked():
                logger.warning("当天已被禁止推送，程序将继续运行")
            
            # 短暂休眠后重试，而不是停止程序
            time.sleep(10)

        finally:
            # 清理资源
            pass
    
    # 程序退出时清理资源
    logger.info("清理资源，关闭JSON调度器")
    try:
        json_scheduler.shutdown()
    except Exception as e:
        logger.error(f"关闭JSON调度器时发生异常: {e}")
    logger.info("黄金价格监控线程已退出")