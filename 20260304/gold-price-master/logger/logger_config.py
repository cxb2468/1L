import logging
import os
from config.config import LOG_LEVEL, LOG_FILE

# 确保日志目录存在
log_file_path = LOG_FILE
if not os.path.isabs(log_file_path):
    # 如果是相对路径，转换为相对于项目根目录的绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = os.path.join(project_root, log_file_path)

# 创建日志目录（如果不存在）
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 将日志级别字符串转换为logging模块的常量
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 获取配置的日志级别
log_level = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

# 配置日志输出格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 配置日志处理器
# 1. 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format))
# 设置控制台编码为utf-8，解决乱码问题
console_handler.encoding = 'utf-8'

# 2. 文件处理器
# 使用UTF-8编码创建日志文件，确保中文正常显示
file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8', delay=False)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format))

# 获取根logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)

# 移除所有默认处理器
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 添加自定义处理器
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# 创建一个通用的获取Logger函数
def get_logger(name):
    """
    获取指定名称的logger实例
    :param name: logger名称
    :return: logger实例
    """
    return logging.getLogger(name)


def update_log_level():
    """
    动态更新日志级别
    从config.py读取最新的LOG_LEVEL配置并应用
    """
    from config.config import LOG_LEVEL
    
    # 获取配置的日志级别
    log_level = LOG_LEVEL_MAP.get(LOG_LEVEL, logging.INFO)
    
    # 更新根logger的级别
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 更新所有处理器的级别
    for handler in root_logger.handlers:
        handler.setLevel(log_level)
    
    # 记录日志级别更新
    logger = get_logger(__name__)
    logger.info(f"日志级别已更新为: {LOG_LEVEL}")
