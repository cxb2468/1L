import requests
import time
from logger.logger_config import get_logger
from config.config import APP_ID, APP_SECRET, MULTI_ACCOUNT_CONFIG
# 获取日志记录器
logger = get_logger(__name__)
class AccessToken:
    """
    微信公众号 Access Token 管理类
    """
    def __init__(self):
        self.access_token = None
        self.token_expire_time = 0
        # 初始化时使用默认配置，但允许子类覆盖
        self.app_id = APP_ID
        self.app_secret = APP_SECRET

    def get_access_token(self):
        """
        获取access_token
        :return: access_token或None
        """
        # 检查token是否仍然有效
        if self.access_token and time.time() < self.token_expire_time:
            logger.debug("使用缓存的Access Token")
            return self.access_token

        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
            self.app_id, self.app_secret)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查HTTP状态码
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                # 设置过期时间（提前5分钟刷新）
                expires_in = result.get('expires_in', 7200)
                self.token_expire_time = time.time() + expires_in - 300
                logger.info("成功获取新的Access Token")
                return self.access_token
            else:
                logger.error(f"获取Access Token失败: {result}")
                self._reset_token()
                return None
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL证书验证失败: {e}")
            self._reset_token()
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"HTTP请求超时: {e}")
            self._reset_token()
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"网络连接错误: {e}")
            self._reset_token()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求异常: {e}")
            self._reset_token()
            return None
        except ValueError as e:
            logger.error(f"响应解析异常: {e}")
            self._reset_token()
            return None
        except Exception as e:
            logger.error(f"获取Access Token发生未知异常: {e}")
            self._reset_token()
            return None
            
    def _reset_token(self):
        """
        重置token信息
        """
        self.access_token = None
        self.token_expire_time = 0

    def refresh_access_token(self):
        """
        手动刷新access_token
        """
        # 清除当前token信息
        self.access_token = None
        self.token_expire_time = 0
        self.get_access_token()