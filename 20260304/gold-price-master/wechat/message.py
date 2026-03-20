import requests
import json
import time
from logger.logger_config import get_logger
from wechat.access_token import AccessToken
from config.config import TEMPLATE_ID, WEB_URL, MULTI_ACCOUNT_CONFIG
from utils.utils import is_push_blocked

# 获取日志记录器
logger = get_logger(__name__)

class MessageSender(AccessToken):
    """定义发送消息的类"""
    
    def __init__(self):
        # 如果有多账号配置，使用第一个账号初始化
        if MULTI_ACCOUNT_CONFIG:
            self.current_account_index = 0
            account = MULTI_ACCOUNT_CONFIG[0]
            # 临时设置当前账号的配置
            self.APP_ID = account['APP_ID']
            self.APP_SECRET = account['APP_SECRET']
            self.TEMPLATE_ID = account['TEMPLATE_ID']
            self.WEB_URL = account['WEB_URL']
            self.ACCOUNT_NAME = account['NAME']
        else:
            # 如果没有多账号配置，使用默认配置
            self.current_account_index = 0
            self.APP_ID = None
            self.APP_SECRET = None
            self.TEMPLATE_ID = None
            self.WEB_URL = None
            self.ACCOUNT_NAME = 'Default Account'
        
        # 设置父类需要的小写属性
        self.app_id = self.APP_ID
        self.app_secret = self.APP_SECRET
        
        super().__init__()  # 调用父类构造函数
        self.opend_ids = []  # 初始化为空列表
        self.last_batch_push_time = 0  # 上次批量推送时间
        self.BATCH_PUSH_INTERVAL = 300  # 批量推送最小间隔（秒）

    def switch_to_next_account(self):
        """
        切换到下一个可用账号
        :return: bool 是否成功切换到新账号
        """
        if not MULTI_ACCOUNT_CONFIG or len(MULTI_ACCOUNT_CONFIG) <= 1:
            logger.warning("没有配置多个账号或只有一个账号，无法切换")
            return False
        
        # 尝试切换到下一个账号
        next_index = (self.current_account_index + 1) % len(MULTI_ACCOUNT_CONFIG)
        
        if next_index == 0:  # 已经回到第一个账号，说明已经尝试过所有账号
            logger.error("已尝试所有账号，均无法使用")
            return False
        
        account = MULTI_ACCOUNT_CONFIG[next_index]
        self.current_account_index = next_index
        self.APP_ID = account['APP_ID']
        self.APP_SECRET = account['APP_SECRET']
        self.TEMPLATE_ID = account['TEMPLATE_ID']
        self.WEB_URL = account['WEB_URL']
        self.ACCOUNT_NAME = account['NAME']
        
        # 更新父类需要的小写属性
        self.app_id = self.APP_ID
        self.app_secret = self.APP_SECRET
        
        # 重置父类的token，以便使用新账号获取新的token
        self._reset_token()
        
        logger.info(f"切换到账号: {self.ACCOUNT_NAME} ({self.current_account_index + 1}/{len(MULTI_ACCOUNT_CONFIG)})")
        return True

    def can_send_batch_push(self):
        """
        检查是否可以进行批量推送（防止短时间内推送过多）
        :return: bool 是否可以推送
        """
        current_time = time.time()
        if current_time - self.last_batch_push_time >= self.BATCH_PUSH_INTERVAL:
            return True
        return False

    def update_batch_push_time(self):
        """
        更新批量推送时间
        """
        self.last_batch_push_time = time.time()

    def get_access_token(self):
        """
        重写获取Access Token的方法，使用当前账号的配置
        :return: Access Token字符串或None
        """
        if not self.APP_ID or not self.APP_SECRET:
            logger.error("当前账号配置无效，无法获取Access Token")
            return None
        # 确保父类使用的是当前账号的配置
        self.app_id = self.APP_ID
        self.app_secret = self.APP_SECRET
        return super().get_access_token()

    def get_openid(self):
        """
        获取所有用户的openid
        :return: openid列表或带有错误信息的字典
        """
        # 检查是否被禁止推送
        if is_push_blocked():
            logger.warning("当天已被禁止推送，无法获取用户openid")
            return {"error": "当天已被禁止推送", "errcode": "push_blocked"}

        token = self.get_access_token()  # 确保token有效
        if not token:
            logger.error("Access Token无效，无法获取用户openid")
            return {"error": "Access Token无效", "errcode": "invalid_token"}

        next_openid = ''
        url_openid = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s' % (
            token, next_openid)
        try:
            response = requests.get(url_openid, timeout=10)
            response.raise_for_status()  # 检查HTTP状态码
            result = response.json()
            
            # 检查微信API返回的错误码
            if result.get("errcode", 0) != 0:
                logger.error(f"获取openid失败: {result}")
                return {"error": "微信API返回错误", "wechat_result": result, "errcode": result.get("errcode")}
            
            if 'data' in result:
                if 'openid' in result['data']:
                    open_ids = result['data']['openid']
                    logger.info(f"成功获取到 {len(open_ids)} 个用户openid")
                    return open_ids
                else:
                    # 没有用户关注公众号
                    logger.info("当前没有用户关注公众号")
                    return []
            else:
                logger.error(f"获取openid失败: {result}")
                return {"error": "获取openid失败", "wechat_result": result}
        except requests.exceptions.SSLError as e:
            logger.error(f"获取openid SSL证书验证失败: {e}")
            return {"error": f"SSL证书验证失败: {e}"}
        except requests.exceptions.Timeout as e:
            logger.error(f"获取openid请求超时: {e}")
            return {"error": f"请求超时: {e}"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"获取openid网络连接错误: {e}")
            return {"error": f"网络连接错误: {e}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求异常: {e}")
            return {"error": f"HTTP请求异常: {e}"}
        except ValueError as e:
            logger.error(f"响应解析异常: {e}")
            return {"error": f"响应解析异常: {e}"}
        except Exception as e:
            logger.error(f"获取openid发生未知异常: {e}")
            return {"error": f"未知异常: {e}"}

    def send_template_message(self, open_id, data):
        """
        发送模板消息给指定用户
        :param open_id: 用户的openid
        :param data: 消息数据
        :return: 发送结果字典
        """
        # 检查是否被禁止推送
        if is_push_blocked():
            logger.warning("当天已被禁止推送，无法发送模板消息")
            return {"error": "当天已被禁止推送"}

        token = self.get_access_token()  # 确保token有效
        if not token:
            return {"error": "Access Token无效"}

        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(token)

        post_data = {
            "touser": open_id,
            "template_id": self.TEMPLATE_ID,  # 使用当前账号的模板ID
            "url": self.WEB_URL,  # 使用当前账号的URL
            "topcolor": "#FF0000",
            "data": data
        }

        try:
            # 发送请求，启用证书验证
            response = requests.post(url, json=post_data, timeout=15)
            response.raise_for_status()  # 检查HTTP状态码
            result = response.json()
            
            # 检查微信API返回的错误码
            if result.get("errcode", -1) != 0:
                logger.error(f"微信API消息发送失败: {result}")
                return {"error": "微信API返回错误", "wechat_result": result, "errcode": result.get("errcode")}
            return result
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL证书验证失败: {e}")
            return {"error": f"SSL证书验证失败: {e}"}
        except requests.exceptions.Timeout as e:
            logger.error(f"HTTP请求超时: {e}")
            return {"error": f"HTTP请求超时: {e}"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"网络连接错误: {e}")
            return {"error": f"网络连接错误: {e}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求异常: {e}")
            return {"error": f"HTTP请求异常: {e}"}
        except ValueError as e:
            logger.error(f"响应解析异常: {e}")
            return {"error": f"响应解析异常: {e}"}
        except Exception as e:
            logger.error(f"发送模板消息发生未知异常: {e}")
            return {"error": f"未知异常: {e}"}

    def send_to_all_users(self, msg):
        """
        给所有用户发送消息（支持多账号切换）
        :param msg: 要发送的消息数据
        :return: 推送结果字典
        """
        # 检查是否被禁止推送
        if is_push_blocked():
            logger.warning("当天已被禁止推送，无法发送消息")
            return {"status": "blocked", "reason": "当天已被禁止推送"}

        # 检查批量推送限制
        if not self.can_send_batch_push():
            logger.warning("为防止消息推送过于频繁，暂时跳过本次批量推送")
            # 即使跳过推送，也要更新推送时间，避免死循环
            self.update_batch_push_time()
            return {"status": "skipped", "reason": "推送过于频繁"}
            
        # 循环尝试使用每个账号发送消息
        total_attempts = len(MULTI_ACCOUNT_CONFIG) if MULTI_ACCOUNT_CONFIG else 1
        for attempt in range(total_attempts):
            logger.info(f"尝试使用账号: {self.ACCOUNT_NAME} (第 {attempt + 1} 次尝试，共 {total_attempts} 次)")
            
            # 获取用户列表
            open_ids = self.get_openid()
            
            # 检查是否获取openid失败
            if isinstance(open_ids, dict) and open_ids.get("error"):
                logger.error(f"账号 {self.ACCOUNT_NAME} 获取openid失败: {open_ids}")
                
                # 如果这是最后一个账号，返回失败
                if attempt == total_attempts - 1:
                    logger.error("所有账号都无法获取用户列表，推送失败")
                    return {"status": "failed", "reason": "所有账号都无法获取用户列表", "error": open_ids}
                
                # 切换到下一个账号
                if not self.switch_to_next_account():
                    logger.error("无法切换到下一个账号，推送失败")
                    return {"status": "failed", "reason": "无法切换到下一个账号", "error": open_ids}
                continue  # 继续尝试下一个账号
                
            if not open_ids:
                logger.info(f"账号 {self.ACCOUNT_NAME} 没有用户关注该公众号，视为推送成功")
                # 更新批量推送时间
                self.update_batch_push_time()
                # 没有用户需要推送，视为推送成功，不再尝试其他账号
                return {"status": "completed", "total": 0, "success": 0, "failed": 0}

            # 发送消息给所有用户
            success_count, fail_count = self._send_messages_to_users(open_ids, msg)
            
            # 检查是否所有消息都发送失败
            if fail_count > 0 and success_count == 0:
                logger.error(f"账号 {self.ACCOUNT_NAME} 所有消息发送失败，尝试切换账号")
                
                # 如果这是最后一个账号，返回失败
                if attempt == total_attempts - 1:
                    logger.error("所有账号都无法发送消息，推送失败")
                    return {"status": "failed", "reason": "所有账号都无法发送消息", "total": len(open_ids), "success": success_count, "failed": fail_count}
                
                # 切换到下一个账号
                if not self.switch_to_next_account():
                    logger.error("无法切换到下一个账号，推送失败")
                    return {"status": "failed", "reason": "无法切换到下一个账号", "total": len(open_ids), "success": success_count, "failed": fail_count}
                continue  # 继续尝试下一个账号
            else:
                # 至少有一些消息发送成功
                logger.info(f"账号 {self.ACCOUNT_NAME} 推送完成: 总计 {len(open_ids)} 个, 成功 {success_count} 个, 失败 {fail_count} 个")
                
                # 更新批量推送时间
                self.update_batch_push_time()
                
                return {"status": "completed", "total": len(open_ids), "success": success_count, "failed": fail_count}
        
        # 如果循环结束后仍未成功（理论上不应该到达这里）
        logger.error("推送过程中出现意外错误")
        return {"status": "failed", "reason": "推送过程中出现意外错误"}
    
    def _send_messages_to_users(self, open_ids, msg):
        """
        给多个用户发送消息
        :param open_ids: 用户openid列表
        :param msg: 要发送的消息数据
        :return: (成功数量, 失败数量)
        """
        success_count = 0
        fail_count = 0
        
        logger.info(f"开始向 {len(open_ids)} 个用户发送消息 (来自账号: {self.ACCOUNT_NAME})")
        
        # 给每个用户发送消息
        for open_id in open_ids:
            result = self.send_template_message(open_id, msg)
            if "error" not in result and result.get("errcode", -1) == 0:
                success_count += 1
            else:
                logger.error(f"消息发送失败: 用户 {open_id}, 结果: {result}")
                fail_count += 1
                
        return success_count, fail_count