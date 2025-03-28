import os
import json

class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            raise ValueError(f'加载配置文件失败: {str(e)}')

    @property
    def aliyun_config(self):
        """获取阿里云配置信息"""
        if not self._config or 'aliyun' not in self._config:
            raise ValueError('未找到阿里云配置信息')
        return self._config['aliyun']

    @property
    def access_key_id(self):
        return self.aliyun_config.get('access_key_id')

    @property
    def access_key_secret(self):
        return self.aliyun_config.get('access_key_secret')

    @property
    def app_key(self):
        return self.aliyun_config.get('app_key')

    @property
    def region_id(self):
        return self.aliyun_config.get('region_id')

    @property
    def deepseek_config(self):
        """获取DeepSeek配置信息"""
        if not self._config or 'deepseek' not in self._config:
            raise ValueError('未找到DeepSeek配置信息')
        return self._config['deepseek']

    @property
    def deepseek_api_key(self):
        return self.deepseek_config.get('api_key')

    @property
    def deepseek_base_url(self):
        return self.deepseek_config.get('base_url', 'https://api.deepseek.com')