# coding: utf-8
"""
AI金融分析模块
负责对接免费金融数据分析AI接口，分析黄金和贵金属行情并给出建议
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from logger.logger_config import get_logger
from config.config import config

# 获取日志记录器
logger = get_logger(__name__)

class AIAnalyzer:
    """
    AI金融分析器
    """
    
    def __init__(self):
        # 配置可用的免费AI接口
        self.api_endpoints = [
            # 阿里云百炼免费模型
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            # 百度文心一言免费接口
            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
            # 讯飞星火免费接口
            "https://spark-api-open.xf-yun.com/v1/chat/completions"
        ]
        # 完全移除缓存机制，确保每次都调用真实接口获取最新分析
        self.cache = {}
        self.cache_timeout = 0  # 设置为0表示不使用缓存
    
    def get_ai_analysis(self, current_price: float, last_price: Optional[float] = None, 
                       trend_direction: str = "稳定") -> str:
        """
        获取AI分析建议 - 根据配置决定是否调用AI接口
        :param current_price: 当前价格
        :param last_price: 上次价格
        :param trend_direction: 趋势方向
        :return: AI分析建议文本（控制在200字以内）
        """
        # 检查AI分析功能是否启用
        if not config.ENABLE_AI_ANALYSIS:
            logger.info("AI分析功能未启用，返回基础分析")
            return self._get_disabled_analysis(current_price, last_price, trend_direction)
        
        try:
            # 构造完整的分析请求数据
            analysis_data = {
                "current_price": current_price,
                "last_price": last_price,
                "trend_direction": trend_direction,
                "commodity": "黄金",
                "currency": "人民币/克",
                "price_change": self._calculate_price_change(current_price, last_price),
                "market_context": self._get_market_context(),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 直接调用外部AI接口，不使用任何缓存
            analysis_result = self._call_external_ai_api(analysis_data)
            
            if analysis_result and len(analysis_result.strip()) > 0:
                # 确保返回的分析内容在合理范围内
                if len(analysis_result) > 200:
                    analysis_result = analysis_result[:200]
                logger.info("成功获取外部AI接口分析结果")
                return analysis_result
            else:
                # 只有当外部接口完全失败时才使用默认分析
                logger.warning("外部AI接口调用失败，使用默认分析作为降级方案")
                return self._get_default_analysis(current_price, last_price, trend_direction)
                
        except Exception as e:
            logger.error(f"AI分析调用异常: {e}")
            # 异常情况下也只使用默认分析
            return self._get_default_analysis(current_price, last_price, trend_direction)
    
    def _call_external_ai_api(self, data: Dict[str, Any]) -> Optional[str]:
        """
        调用外部AI分析接口 - 完全依赖数据接口返回的原始分析
        :param data: 完整的市场分析数据
        :return: 直接返回AI接口的原始分析结果
        """
        # 检查是否有配置的AI服务
        available_services = config.get_available_services()
        if not available_services:
            logger.info("未检测到配置的AI服务，直接使用降级分析")
            return None
        
        logger.info(f"检测到可用AI服务: {', '.join(available_services)}")
        
        # 按顺序尝试调用不同的免费AI接口
        for i, endpoint in enumerate(self.api_endpoints):
            try:
                logger.info(f"正在调用第{i+1}个AI接口: {endpoint}")
                result = self._request_ai_analysis(endpoint, data)
                
                # 详细记录返回结果
                if result is not None:
                    result_length = len(str(result).strip())
                    logger.debug(f"从 {endpoint} 收到响应，长度: {result_length} 字符")
                    
                    if result_length > 10:  # 确保返回有效内容
                        logger.info(f"成功从 {endpoint} 获取AI分析，长度: {result_length} 字符")
                        return str(result).strip()
                    else:
                        logger.warning(f"从 {endpoint} 获取的分析内容过短({result_length}字符)，视为无效")
                else:
                    logger.warning(f"从 {endpoint} 获取的分析结果为None")
                    
            except Exception as e:
                logger.warning(f"调用 {endpoint} 失败: {e}")
                continue
        
        logger.error("所有AI接口调用均失败")
        return None
    
    def _request_ai_analysis(self, endpoint: str, data: Dict[str, Any]) -> Optional[str]:
        """
        向指定AI接口发送分析请求
        :param endpoint: API端点
        :param data: 分析数据
        :return: 分析结果
        """
        # 根据不同平台构造请求
        if "aliyuncs.com" in endpoint:
            return self._call_aliyun_api(endpoint, data)
        elif "baidubce.com" in endpoint:
            return self._call_baidu_api(endpoint, data)
        elif "xf-yun.com" in endpoint:
            return self._call_xunfei_api(endpoint, data)
        else:
            return None
    
    def _call_aliyun_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[str]:
        """
        调用阿里云百炼API
        """
        if not config.ALIYUN_API_KEY:
            logger.warning("未配置阿里云API密钥")
            return None
            
        headers = {
            "Authorization": f"Bearer {config.ALIYUN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = self._construct_analysis_prompt(data)
        payload = {
            "model": "qwen-plus",
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "max_tokens": config.MAX_ANALYSIS_LENGTH,
                "temperature": 0.7
            }
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=config.REQUEST_TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            return result.get("output", {}).get("text", "")
        return None
    
    def _call_baidu_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[str]:
        """
        调用百度文心一言API
        """
        if not config.BAIDU_API_KEY or not config.BAIDU_SECRET_KEY:
            logger.warning("未配置百度API密钥")
            return None
            
        access_token = self._get_baidu_access_token()
        if not access_token:
            return None
            
        headers = {
            "Content-Type": "application/json"
        }
        
        prompt = self._construct_analysis_prompt(data)
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_output_tokens": config.MAX_ANALYSIS_LENGTH
        }
        
        url = f"{endpoint}?access_token={access_token}"
        response = requests.post(url, headers=headers, json=payload, timeout=config.REQUEST_TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            return result.get("result", "")
        return None
    
    def _call_xunfei_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[str]:
        """
        调用讯飞星火API
        """
        if not config.XUNFEI_API_KEY:
            logger.warning("未配置讯飞API密钥")
            return None
            
        headers = {
            "Authorization": f"Bearer {config.XUNFEI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = self._construct_analysis_prompt(data)
        payload = {
            "model": "general",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": config.MAX_ANALYSIS_LENGTH,
            "temperature": 0.7
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=config.REQUEST_TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
        return None
    
    def _get_baidu_access_token(self) -> Optional[str]:
        """
        获取百度API访问令牌
        """
        if not config.BAIDU_API_KEY or not config.BAIDU_SECRET_KEY:
            return None
            
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={config.BAIDU_API_KEY}&client_secret={config.BAIDU_SECRET_KEY}"
        
        try:
            response = requests.post(url, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get("access_token")
        except Exception as e:
            logger.error(f"获取百度access_token失败: {e}")
        return None
    
    def _construct_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """
        构造AI分析提示词
        :param data: 完整的市场数据
        :return: 格式化的提示词
        """
        prompt = f"""
作为专业的金融分析师，请分析以下黄金市场数据并给出投资建议：

商品：{data['commodity']}
当前价格：{data['current_price']:.2f} {data['currency']}
价格变化：{data['price_change']:.2f}%
趋势方向：{data['trend_direction']}
市场环境：{data['market_context']}
时间戳：{data['timestamp']}

请提供简洁的投资建议（200字以内）：
1. 当前市场状况分析
2. 短期走势预测
3. 投资操作建议
"""
        return prompt
    
    def _calculate_price_change(self, current_price: float, last_price: Optional[float]) -> float:
        """
        计算价格变化百分比
        :param current_price: 当前价格
        :param last_price: 上次价格
        :return: 价格变化百分比
        """
        if last_price is not None and last_price > 0:
            return ((current_price - last_price) / last_price) * 100
        return 0.0
    
    def _get_market_context(self) -> str:
        """
        获取市场环境上下文
        :return: 市场环境描述
        """
        # 这里可以集成更多市场数据，如：
        # - 美元指数
        # - 原油价格
        # - 美债收益率
        # - VIX恐慌指数等
        return "当前全球金融市场环境"
    
    def _get_disabled_analysis(self, current_price: float, last_price: Optional[float], 
                              trend_direction: str) -> str:
        """
        AI功能禁用时的基础分析
        :param current_price: 当前价格
        :param last_price: 上次价格
        :param trend_direction: 趋势方向
        :return: 基础行情分析文本
        """
        try:
            price_change = self._calculate_price_change(current_price, last_price)
            analysis = f"【基础分析】当前金价{current_price:.2f}元/克，{trend_direction}趋势({price_change:+.2f}%)。AI分析功能已禁用，可在配置页面启用。"
            
            # 严格控制长度
            if len(analysis) > 200:
                analysis = analysis[:197] + "..."
                
            return analysis
            
        except Exception as e:
            logger.error(f"生成禁用状态分析失败: {e}")
            return f"【系统维护】当前金价{current_price:.2f}元/克，请稍后重试。"
    
    def _get_default_analysis(self, current_price: float, last_price: Optional[float], 
                            trend_direction: str) -> str:
        """
        默认分析建议 - 仅作为最后的降级方案
        :param current_price: 当前价格
        :param last_price: 上次价格
        :param trend_direction: 趋势方向
        :return: 简单的分析文本
        """
        try:
            price_change = self._calculate_price_change(current_price, last_price)
            
            # 更友好的降级提示，区分不同情况
            if not config.is_configured():
                analysis = f"【提示】未配置AI服务密钥，显示基础行情信息。当前金价{current_price:.2f}元/克，{trend_direction}趋势({price_change:+.2f}%)。配置API密钥可获得专业AI分析。"
            else:
                analysis = f"【系统降级】当前金价{current_price:.2f}元/克，{trend_direction}趋势({price_change:+.2f}%)。AI服务暂时不可用，请稍后重试。"
            
            # 严格控制长度
            if len(analysis) > 200:
                analysis = analysis[:197] + "..."
                
            return analysis
            
        except Exception as e:
            logger.error(f"生成默认分析失败: {e}")
            return f"【系统维护】当前金价{current_price:.2f}元/克，请稍后重试。"

# 全局AI分析器实例
ai_analyzer = AIAnalyzer()

def get_gold_analysis(current_price: float, last_price: Optional[float] = None, 
                     trend_direction: str = "稳定") -> str:
    """
    获取黄金AI分析建议的便捷函数
    :param current_price: 当前价格
    :param last_price: 上次价格
    :param trend_direction: 趋势方向
    :return: AI分析建议
    """
    return ai_analyzer.get_ai_analysis(current_price, last_price, trend_direction)