# coding: utf-8
"""
工具函数模块
包含项目中使用的各种工具函数
"""

import time
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# 延迟导入logger，避免循环导入
# from logger.logger_config import get_logger

# 获取日志记录器（延迟初始化）
# logger = get_logger(__name__)
logger = None


def _get_logger():
    """延迟获取logger实例"""
    global logger
    if logger is None:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
    return logger


def _get_current_data_source_name() -> str:
    """
    获取当前使用的数据源名称
    :return: 数据源名称
    """
    try:
        import config
        # 获取启用的数据源
        enabled_sources = [source for source in config.GOLD_PRICE_SOURCES if source.get('enabled', True)]
        if enabled_sources:
            # 按排序获取第一个启用的数据源作为当前数据源
            sorted_sources = sorted(enabled_sources, key=lambda x: x.get('sort_order', 999))
            return sorted_sources[0]['name']
        else:
            return '系统维护'
    except Exception as e:
        _get_logger().warning(f"获取数据源名称失败: {e}")
        return '系统维护'


# 禁止运行文件路径
BLOCK_FILE_PATH = "./push_blocked.txt"
FAILURE_COUNT_FILE_PATH = "./push_failure_count.json"  # 新增：记录推送失败次数的文件


def check_and_reset_expired_block() -> None:
    """
    检查并重置过期的推送阻止文件
    这个函数应在程序启动时调用，确保不会因为过期的阻止文件导致持续无法推送
    """
    if not os.path.exists(BLOCK_FILE_PATH):
        return

    try:
        # 尝试用UTF-8编码读取
        try:
            with open(BLOCK_FILE_PATH, 'r', encoding='utf-8') as f:
                blocked_date_str = f.read().strip()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用GBK编码（Windows系统常见）
            with open(BLOCK_FILE_PATH, 'r', encoding='gbk') as f:
                blocked_date_str = f.read().strip()

        if not blocked_date_str:
            os.remove(BLOCK_FILE_PATH)
            return

        blocked_date = datetime.strptime(blocked_date_str, "%Y-%m-%d")
        today = datetime.now().date()

        # 如果文件中的日期不是今天，则删除过期的文件
        if blocked_date.date() != today:
            os.remove(BLOCK_FILE_PATH)
            _get_logger().info(f"已删除过期的推送阻止文件，原阻止日期: {blocked_date_str}")

    except Exception as e:
        _get_logger().error(f"检查过期推送阻止文件失败: {e}")
        # 出错时删除文件，避免无限禁止
        if os.path.exists(BLOCK_FILE_PATH):
            os.remove(BLOCK_FILE_PATH)


def is_push_blocked() -> bool:
    """
    检查是否被禁止推送
    :return: bool 是否被禁止推送
    """
    if not os.path.exists(BLOCK_FILE_PATH):
        return False

    try:
        # 使用utf-8编码读取文件，处理Windows系统上的编码问题
        try:
            with open(BLOCK_FILE_PATH, 'r', encoding='utf-8') as f:
                blocked_date_str = f.read().strip()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用GBK编码（Windows系统常见）
            with open(BLOCK_FILE_PATH, 'r', encoding='gbk') as f:
                blocked_date_str = f.read().strip()

        if not blocked_date_str:
            os.remove(BLOCK_FILE_PATH)
            return False

        blocked_date = datetime.strptime(blocked_date_str, "%Y-%m-%d")
        today = datetime.now().date()

        # 检查是否是当天的禁止记录
        if blocked_date.date() == today:
            _get_logger().warning(f"当天已被禁止推送，禁止日期: {blocked_date_str}")
            return True
        else:
            os.remove(BLOCK_FILE_PATH)
            return False
    except Exception as e:
        _get_logger().error(f"检查禁止推送状态失败: {e}")
        if os.path.exists(BLOCK_FILE_PATH):
            os.remove(BLOCK_FILE_PATH)
        return False


def set_push_blocked() -> None:
    """
    设置当天禁止推送
    """
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        # 使用utf-8编码写入文件，处理Windows系统上的编码问题
        with open(BLOCK_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(today_str)
        _get_logger().error(f"已设置当天禁止推送: {today_str}")

        if os.path.exists(FAILURE_COUNT_FILE_PATH):
            os.remove(FAILURE_COUNT_FILE_PATH)
    except Exception as e:
        _get_logger().error(f"设置禁止推送状态失败: {e}")


def increment_push_failure_count(push_type: str = "regular") -> int:
    """
    增加推送失败计数
    :param push_type: 推送类型 ("regular", "alert_high", "alert_low")
    :return: 当前失败次数
    """
    try:
        # 读取现有的失败计数
        failure_data: Dict[str, Any] = {}
        if os.path.exists(FAILURE_COUNT_FILE_PATH):
            with open(FAILURE_COUNT_FILE_PATH, 'r', encoding='utf-8') as f:
                failure_data = json.load(f)

        # 获取今天的日期
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 初始化今天的数据
        if today_str not in failure_data:
            failure_data[today_str] = {}

        # 初始化特定推送类型的计数
        if push_type not in failure_data[today_str]:
            failure_data[today_str][push_type] = 0

        # 增加计数
        failure_data[today_str][push_type] += 1

        # 保存更新后的数据
        with open(FAILURE_COUNT_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(failure_data, f, ensure_ascii=False, indent=2)

        return failure_data[today_str][push_type]
    except Exception as e:
        _get_logger().error(f"增加推送失败计数失败: {e}")
        return 0


def get_push_failure_count(push_type: str = "regular") -> int:
    """
    获取推送失败计数
    :param push_type: 推送类型 ("regular", "alert_high", "alert_low")
    :return: 当前失败次数
    """
    try:
        if not os.path.exists(FAILURE_COUNT_FILE_PATH):
            return 0

        with open(FAILURE_COUNT_FILE_PATH, 'r', encoding='utf-8') as f:
            failure_data = json.load(f)

        today_str = datetime.now().strftime("%Y-%m-%d")

        # 如果不是今天的记录，清零计数
        if today_str not in failure_data or push_type not in failure_data[today_str]:
            return 0

        return failure_data[today_str][push_type]
    except Exception as e:
        _get_logger().error(f"获取推送失败计数失败: {e}")
        return 0


def should_set_push_blocked(push_type: str = "regular", max_failures: int = 3) -> bool:
    """
    根据失败次数判断是否应该设置推送阻止
    :param push_type: 推送类型 ("regular", "alert_high", "alert_low")
    :param max_failures: 最大失败次数阈值，默认为3次
    :return: 是否应该设置推送阻止
    """
    current_failures = get_push_failure_count(push_type)
    _get_logger().info(f"推送类型 {push_type} 当前失败次数: {current_failures}/{max_failures}")

    if current_failures >= max_failures:
        _get_logger().warning(f"推送类型 {push_type} 失败次数达到阈值 {max_failures}，将设置推送阻止")
        return True

    return False


class PushStatusManager:
    """
    推送状态管理器
    统一管理定期推送和预警推送的状态
    """

    def __init__(self) -> None:
        # 定期推送状态
        self.last_regular_push_time: float = 0  # 上次定期推送时间
        self.last_sent_price: float = 0  # 上次推送的价格，用于防止重复推送
        self.last_regular_push_minute: int = -1  # 上次推送的分钟，用于防止同一分钟内重复推送

        # 预警推送状态
        self.alerted_high: bool = False  # 高价预警状态
        self.alerted_low: bool = False  # 低价预警状态
        self.last_push_time_high: float = 0  # 上次高价推送时间
        self.last_push_time_low: float = 0  # 上次低价推送时间
        self.push_count_high: int = 0  # 高价推送次数
        self.push_count_low: int = 0  # 低价推送次数
        self.last_alert_price_high: float = 0  # 最近一次高价预警推送的价格
        self.last_alert_price_low: float = 0  # 最近一次低价预警推送的价格

        # 全局推送限制
        self.last_global_push_time: float = 0  # 上次全局推送时间

    def reset_regular_push_status(self, current_minute: int, current_price: float) -> None:
        """
        重置定期推送状态
        :param current_minute: 当前分钟
        :param current_price: 当前价格
        """
        self.last_regular_push_time = time.time()
        self.last_sent_price = current_price
        # 存储当前小时和分钟，格式为：小时*100 + 分钟（例如：10点01分存储为1001）
        # 这样可以判断当前小时是否已经推送过
        current_hour = time.localtime().tm_hour
        self.last_regular_push_minute = current_hour * 100 + current_minute

    def reset_alert_push_status(self, direction: str, price: float) -> None:
        """
        重置预警推送状态
        :param direction: 价格变动方向
        :param price: 当前价格
        """
        current_time = time.time()
        if direction == "上涨":
            self.last_push_time_high = current_time
            self.last_alert_price_high = price
            self.push_count_high += 1
        else:
            self.last_push_time_low = current_time
            self.last_alert_price_low = price
            self.push_count_low += 1

    def reset_daily_push_counts(self) -> None:
        """
        重置每日推送计数
        """
        self.push_count_high = 0
        self.push_count_low = 0

    def update_global_push_time(self) -> None:
        """
        更新全局推送时间
        """
        self.last_global_push_time = time.time()


def build_message_data(price: float, arrow: str, gold_alert_manager: Any, direction: Optional[str] = None,
                       push_type: str = "regular", ai_analysis: str = "") -> Dict[str, Any]:
    """
    构建微信模板消息的数据
    :param price: 当前黄金价格
    :param arrow: 价格变化箭头
    :param gold_alert_manager: 黄金预警管理器实例
    :param direction: 价格变动方向（可选，用于预警消息）
    :param push_type: 推送类型，"regular" 或 "alert"
    :param ai_analysis: AI分析建议
    :return: 消息数据字典
    """
    # 获取当前时间，格式化为友好的显示格式
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 构建消息数据 - 根据提供的模板格式
    message_data = {
        "type": {
            "value": "定时消息" if push_type == "regular" else "预警消息"
        },
        "price": {
            "value": f"¥{price:.2f}/克"
        },
        "trend": {
            "value": f"{arrow}"
        },
        "source": {
            "value": _get_current_data_source_name()
        },
        "base": {
            "value": f"={gold_alert_manager.config.default_gold_price}"
        },
        "high": {
            "value": f"+{gold_alert_manager.config.price_gap_high}"
        },
        "low": {
            "value": f"-{gold_alert_manager.config.price_gap_low}"
        },
        "dynamic_base": {
            "value": f"¥{gold_alert_manager.dynamic_base_price:.2f}/克"
        },
        "time": {
            "value": current_time
        }
    }

    # 添加AI分析字段（如果提供了分析内容）
    if ai_analysis:
        message_data["analysis"] = {
            "value": ai_analysis
        }

    # 如果是预警消息，添加颜色属性
    if direction:
        message_data["dynamic_base"]["color"] = "#FF0000" if direction == "上涨" else "#00FF00"

    return message_data


def handle_push_frequency_control(push_result: Dict[str, Any], push_type: str = "regular") -> bool:
    """
    处理推送频率控制，避免死循环
    :param push_result: 推送结果字典
    :param push_type: 推送类型
    :return: bool 是否需要等待
    """
    if push_result and push_result.get('reason') == '推送过于频繁':
        _get_logger().warning(f"{push_type}推送过于频繁，建议等待后再重试")
        return True
    return False


def send_push_message(message_sender: Any, message_data: Dict[str, Any], push_type: str = "regular") -> Dict[str, Any]:
    """
    发送推送消息的通用函数
    :param message_sender: 消息发送实例
    :param message_data: 消息数据字典
    :param push_type: 推送类型，"regular" 或 "alert"
    :return: 推送结果字典
    """
    try:
        result = message_sender.send_to_all_users(message_data)

        if result is None:
            _get_logger().error(f"{push_type}消息推送失败: send_to_all_users返回None")
            return {'success': False, 'reason': 'send_to_all_users返回None'}

        if result.get("status") == "skipped":
            _get_logger().warning(f"{push_type}消息推送被跳过: {result.get('reason')}")
            return {'success': False, 'reason': result.get('reason'), 'result': result}
        elif result.get("status") == "failed":
            _get_logger().error(f"{push_type}消息推送失败: {result.get('reason')}")

            push_type_for_count = push_type
            if push_type == "alert":
                push_type_for_count = "alert_high" if "预警消息" in str(message_data) else "alert_low"

            failure_count = increment_push_failure_count(push_type_for_count)

            if should_set_push_blocked(push_type_for_count):
                from utils import set_push_blocked
                set_push_blocked()

            return {'success': False, 'reason': result.get('reason'), 'result': result}
        elif result.get("total", 0) > 0 and result.get("success", 0) == 0:
            _get_logger().error(f"{push_type}消息推送失败: 所有用户发送失败")

            push_type_for_count = push_type
            if push_type == "alert":
                push_type_for_count = "alert_high" if "预警消息" in str(message_data) else "alert_low"

            failure_count = increment_push_failure_count(push_type_for_count)

            if should_set_push_blocked(push_type_for_count):
                from utils import set_push_blocked
                set_push_blocked()

            return {'success': False, 'reason': '所有用户发送失败', 'result': result}
        elif result.get("error"):
            _get_logger().error(f"{push_type}消息推送失败: {result.get('error')}")

            push_type_for_count = push_type
            if push_type == "alert":
                push_type_for_count = "alert_high" if "预警消息" in str(message_data) else "alert_low"

            failure_count = increment_push_failure_count(push_type_for_count)

            if should_set_push_blocked(push_type_for_count):
                from utils import set_push_blocked
                set_push_blocked()

            return {'success': False, 'error': result.get('error'), 'result': result}

        if push_type == "regular":
            _get_logger().info("定期价格更新消息已发送")
        else:
            _get_logger().info("价格预警消息已推送")

        _get_logger().debug(f"send_push_message returning success: result={result}")
        push_type_for_count = push_type
        if push_type == "alert":
            push_type_for_count = "alert_high" if "预警消息" in str(message_data) else "alert_low"

        try:
            if os.path.exists(FAILURE_COUNT_FILE_PATH):
                with open(FAILURE_COUNT_FILE_PATH, 'r', encoding='utf-8') as f:
                    failure_data = json.load(f)

                today_str = datetime.now().strftime("%Y-%m-%d")
                if today_str in failure_data and push_type_for_count in failure_data[today_str]:
                    failure_data[today_str][push_type_for_count] = 0

                with open(FAILURE_COUNT_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(failure_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            _get_logger().error(f"重置推送失败计数失败: {e}")

        return {'success': True, 'result': result}
    except Exception as e:
        _get_logger().error(f"发送{push_type}消息失败: {e}")

        push_type_for_count = push_type
        if push_type == "alert":
            push_type_for_count = "alert_high" if "预警消息" in str(message_data) else "alert_low"

        failure_count = increment_push_failure_count(push_type_for_count)

        if should_set_push_blocked(push_type_for_count):
            from utils import set_push_blocked
            set_push_blocked()

        return {'success': False, 'error': str(e)}