# coding: utf-8
"""
黄金价格预警模块
负责处理黄金价格预警逻辑
"""

import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

from config.config import (
    MAX_PUSH_COUNT, DEFAULT_GOLD_PRICE, DEFAULT_PRICE_GAP_HIGH,
    DEFAULT_PRICE_GAP_LOW, PRICE_CHANGE_THRESHOLD, GLOBAL_PUSH_INTERVAL
)
from wechat.message import MessageSender
from logger.logger_config import get_logger
from utils.utils import build_message_data, send_push_message, PushStatusManager, is_push_blocked

# 获取日志记录器
logger = get_logger(__name__)
@dataclass
class GoldAlertConfig:
    """黄金预警配置类"""
    default_gold_price: float = DEFAULT_GOLD_PRICE  # 默认黄金价格（人民币/克）
    price_gap_high: float = DEFAULT_PRICE_GAP_HIGH  # 默认价格上涨浮动差额（人民币/克）
    price_gap_low: float = DEFAULT_PRICE_GAP_LOW  # 默认价格下跌浮动差额（人民币/克）
    price_change_threshold: float = PRICE_CHANGE_THRESHOLD  # 价格变化阈值（元），用于防止重复推送
    global_push_interval: int = GLOBAL_PUSH_INTERVAL  # 全局推送最小间隔（秒）

class GoldAlert:
    """
    黄金价格预警管理器
    """
    def __init__(self) -> None:
        self.config: GoldAlertConfig = GoldAlertConfig()
        self.message_sender: MessageSender = MessageSender()

        # 集成推送状态管理器
        self.push_status_manager: PushStatusManager = PushStatusManager()

        # 预警状态
        self.alerted_high: bool = False
        self.alerted_low: bool = False

        # 基准价格
        self.original_base_price: float = self.config.default_gold_price  # 原始基准价格
        self.dynamic_base_price: float = self.config.default_gold_price   # 动态基准价格

    def can_send_global_push(self) -> bool:
        """
        检查是否可以进行全局推送（防止短时间内推送过多）
        :return: bool 是否可以推送
        """
        current_time = time.time()
        if current_time - self.push_status_manager.last_global_push_time >= self.config.global_push_interval:
            return True
        return False

    def update_global_push_time(self) -> None:
        """
        更新全局推送时间
        """
        self.push_status_manager.update_global_push_time()

    def update_default_gold_price(self, new_price: float) -> None:
        """
        更新动态基准价为新的预警价格
        :param new_price: 新的价格
        :return: None
        """
        old_dynamic_price = self.dynamic_base_price
        self.dynamic_base_price = new_price
        # 不更新默认黄金价格，保持其作为初始阈值计算的基准

        logger.info(f"动态基准价已更新: {old_dynamic_price} -> {new_price}")
        logger.info(f"新的动态预警阈值: 高价={self.dynamic_base_price + self.config.price_gap_high:.2f}, 低价={self.dynamic_base_price - self.config.price_gap_low:.2f}")
        logger.info(f"初始预警阈值: 高价={self.config.default_gold_price + self.config.price_gap_high:.2f}, 低价={self.config.default_gold_price - self.config.price_gap_low:.2f}")

    def send_price_alert(self, price: float, direction: str) -> Dict[str, Any]:
        """
        发送价格预警消息
        :param price: 当前价格
        :param direction: 价格变动方向 ("上涨" 或 "下跌")
        :return: 推送结果字典
        """
        # 检查是否被禁止推送
        if is_push_blocked():
            logger.warning("当天已被禁止推送，无法发送价格预警")
            return {'success': False, 'reason': '当天已被禁止推送'}

        # 检查当前时间是否在推送时间范围内
        from monitor.monitor import is_within_push_time
        from config.config import PUSH_START_TIME, PUSH_END_TIME, TEST_MODE
        if not is_within_push_time(PUSH_START_TIME, PUSH_END_TIME, TEST_MODE):
            logger.warning("当前时间不在推送时间范围内，无法发送价格预警")
            return {'success': False, 'reason': '当前时间不在推送时间范围内'}

        # 检查全局推送限制
        if not self.can_send_global_push():
            logger.warning("为防止消息推送过于频繁，暂时跳过本次推送")
            return {'success': False, 'reason': '全局推送频率限制'}

        # 获取价格涨跌图标
        arrow = "(上涨)" if direction == "上涨" else "(下跌)"

        # 获取AI分析建议
        from ai.ai_analyzer import get_gold_analysis
        # 获取上一次价格用于分析（如果有的话）
        last_price_for_analysis = getattr(self, '_last_alert_price', None)
        ai_analysis = get_gold_analysis(price, last_price_for_analysis, direction)
        # 保存当前价格供下次分析使用
        self._last_alert_price = price

        # 使用工具函数构建消息数据，包含AI分析
        message_data = build_message_data(price, arrow, self, direction, push_type="alert", ai_analysis=ai_analysis)

        # 使用通用推送函数发送消息
        result = send_push_message(self.message_sender, message_data, push_type="alert")
        logger.debug(f"send_price_alert result: {result}, type: {type(result)}")
        if result and result.get('success'):
            self.update_global_push_time()
            logger.info(f"价格预警消息已推送，价格: ¥{price:.2f}/克，方向: {direction}")
            logger.debug(f"Returning from send_price_alert with success")
            return {'success': True, 'action': '价格预警推送成功'}
        else:
            error_msg = '未知错误'
            if result:
                error_msg = result.get('reason') or result.get('error') or '未知错误'
            logger.warning(f"价格预警推送失败: {error_msg}")
            return {'success': False, 'reason': error_msg, 'error': error_msg}

    def check_alert_conditions(self, price: float) -> Dict[str, Any]:
        """
        检查预警条件（使用固定阈值方式）
        当价格达到阈值时立即推送，不影响定时推送规则
        :param price: 当前黄金价格
        :return: 处理结果字典
        """
        try:
            # 验证价格数据类型
            float_price = float(price)
        except (ValueError, TypeError) as e:
            logger.error(f"价格数据格式无效: {price}", exc_info=True)
            return {'success': False, 'reason': '价格数据格式错误'}

        # 使用默认黄金价格计算初始阈值
        alert_high_threshold = self.config.default_gold_price + self.config.price_gap_high  # 预警高价（人民币/克）
        alert_low_threshold = self.config.default_gold_price - self.config.price_gap_low   # 预警低价（人民币/克）

        logger.debug(f"检查预警条件 - 当前价格: {float_price:.2f}, 高价阈值: {alert_high_threshold:.2f}, 低价阈值: {alert_low_threshold:.2f}")

        # 高价预警
        if float_price >= alert_high_threshold and not self.alerted_high:
            logger.debug(f"触发高价预警检查，准备调用 _handle_high_price_alert")
            try:
                result = self._handle_high_price_alert(float_price)
                logger.debug(f"_handle_high_price_alert 返回: {result}")
                return result
            except Exception as e:
                logger.error(f"_handle_high_price_alert 异常: {e}", exc_info=True)
                return {'success': False, 'reason': str(e)}

        # 低价预警
        elif float_price <= alert_low_threshold and not self.alerted_low:
            logger.debug(f"触发低价预警检查，准备调用 _handle_low_price_alert")
            try:
                result = self._handle_low_price_alert(float_price)
                logger.debug(f"_handle_low_price_alert 返回: {result}")
                return result
            except Exception as e:
                logger.error(f"_handle_low_price_alert 异常: {e}", exc_info=True)
                return {'success': False, 'reason': str(e)}

        # 重置预警状态（允许反复触发）
        # 当价格回落到正常范围时，重置预警状态
        if self.alerted_high and float_price < (self.config.default_gold_price + self.config.price_gap_high) - self.config.price_gap_high * 0.8:
            self.alerted_high = False
            self.push_status_manager.push_count_high = 0  # 重置推送次数
            logger.info(f"高价预警状态重置，当前价格: {float_price:.2f}, 默认黄金价格: {self.config.default_gold_price:.2f}")
            return {'success': True, 'action': '重置高价预警状态'}

        if self.alerted_low and float_price > (self.config.default_gold_price - self.config.price_gap_low) + self.config.price_gap_low * 0.8:
            self.alerted_low = False
            self.push_status_manager.push_count_low = 0  # 重置推送次数
            logger.info(f"低价预警状态重置，当前价格: {float_price:.2f}, 默认黄金价格: {self.config.default_gold_price:.2f}")
            return {'success': True, 'action': '重置低价预警状态'}

        return {'success': True, 'action': '无预警动作'}

    def _handle_high_price_alert(self, float_price: float) -> Dict[str, Any]:
        """
        处理高价预警
        :param float_price: 当前黄金价格
        :return: 处理结果字典
        """
        # 无论推送是否成功，都先更新动态基准价
        self.update_default_gold_price(float_price)
        logger.info(f"高价预警触发，动态基准价已更新为: {float_price:.2f}")

        # 检查是否需要推送消息（推送次数未达到上限）
        if self.push_status_manager.push_count_high < MAX_PUSH_COUNT:
            # 防止推送过于接近的价格
            if abs(float_price - self.push_status_manager.last_alert_price_high) >= self.config.price_change_threshold:
                result = self.send_price_alert(float_price, "上涨")
                if result and result.get('success'):
                    # 更新预警推送状态
                    self.push_status_manager.reset_alert_push_status("上涨", float_price)
                    self.alerted_high = True
                    return {'success': True, 'action': '高价预警推送成功'}
                else:
                    # 推送失败，返回失败信息
                    error_msg = '未知错误'
                    if result:
                        error_msg = result.get('reason') or result.get('error') or '未知错误'
                    logger.error(f"高价预警推送失败: {error_msg}")
                    self.alerted_high = True
                    return {'success': False, 'reason': error_msg, 'action': '高价预警推送失败'}
            else:
                logger.debug(f"价格变化过小，不推送: {abs(float_price - self.push_status_manager.last_alert_price_high):.2f} < {self.config.price_change_threshold}")
        else:
            logger.warning(f"高价推送次数已达上限: {self.push_status_manager.push_count_high}/{MAX_PUSH_COUNT}")

        self.alerted_high = True
        return {'success': True, 'action': '设置高价预警状态'}

    def _handle_low_price_alert(self, float_price: float) -> Dict[str, Any]:
        """
        处理低价预警
        :param float_price: 当前黄金价格
        :return: 处理结果字典
        """
        # 无论推送是否成功，都先更新动态基准价
        self.update_default_gold_price(float_price)
        logger.info(f"低价预警触发，动态基准价已更新为: {float_price:.2f}")

        # 检查是否需要推送消息（推送次数未达到上限）
        if self.push_status_manager.push_count_low < MAX_PUSH_COUNT:
            # 防止推送过于接近的价格
            if abs(float_price - self.push_status_manager.last_alert_price_low) >= self.config.price_change_threshold:
                result = self.send_price_alert(float_price, "下跌")
                logger.debug(f"_handle_low_price_alert result: {result}, type: {type(result)}")
                if result and result.get('success'):
                    # 更新预警推送状态
                    self.push_status_manager.reset_alert_push_status("下跌", float_price)
                    self.alerted_low = True
                    return {'success': True, 'action': '低价预警推送成功'}
                else:
                    # 推送失败，返回失败信息
                    error_msg = '未知错误'
                    if result:
                        error_msg = result.get('reason') or result.get('error') or '未知错误'
                    logger.error(f"低价预警推送失败: {error_msg}")
                    self.alerted_low = True
                    return {'success': False, 'reason': error_msg, 'action': '低价预警推送失败'}
            else:
                logger.debug(f"价格变化过小，不推送: {abs(float_price - self.push_status_manager.last_alert_price_low):.2f} < {self.config.price_change_threshold}")
        else:
            logger.warning(f"低价推送次数已达上限: {self.push_status_manager.push_count_low}/{MAX_PUSH_COUNT}")

        self.alerted_low = True
        return {'success': True, 'action': '设置低价预警状态'}

# 创建全局黄金预警管理器实例
gold_alert_manager = GoldAlert()