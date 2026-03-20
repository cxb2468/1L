import re
import time
from datetime import datetime
from flask import render_template, request, redirect, url_for, session
import importlib
import os
import sys
import logging
import platform

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 配置文件路径
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.py")
# 确保路径使用正确的分隔符
CONFIG_FILE_PATH = os.path.normpath(CONFIG_FILE_PATH)

# 读取配置文件中的密码
def get_config_password():
    """从配置文件中读取密码"""
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 CONFIG_PASSWORD 配置
        match = re.search(r'CONFIG_PASSWORD\s*=\s*["\'](.*?)["\']', content)
        if match:
            return match.group(1)
        else:
            # 如果没有密码配置，返回默认值
            return "admin888"
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        logger.warning(f"读取配置密码失败: {e}")
        return "admin888"

# 保存配置到文件
def save_config_to_file(config_data, password):
    """保存配置到文件"""
    try:
        logger.info(f"开始保存配置，配置文件路径: {CONFIG_FILE_PATH}")
        # 确保文件存在
        if not os.path.exists(CONFIG_FILE_PATH):
            logger.error(f"配置文件不存在: {CONFIG_FILE_PATH}")
            return False
        
        # 检查文件是否可写
        if not os.access(CONFIG_FILE_PATH, os.W_OK):
            logger.error(f"配置文件不可写: {CONFIG_FILE_PATH}")
            return False
        
        # 读取当前配置文件内容
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"成功读取配置文件，文件大小: {len(content)} 字节")
        
        # 更新微信公众号配置
        accounts = []
        account_count = int(config_data.get('account_count', 2))
        
        for i in range(1, account_count + 1):
            app_id = config_data.get(f'app_id_{i}', '')
            app_secret = config_data.get(f'app_secret_{i}', '')
            template_id = config_data.get(f'template_id_{i}', '')
            web_url = config_data.get(f'web_url_{i}', '')
            name = config_data.get(f'name_{i}', '')
            
            # 只添加有效的账号（所有字段都不为空）
            if app_id and app_secret and template_id and web_url and name:
                accounts.append({
                    'APP_ID': app_id,
                    'APP_SECRET': app_secret,
                    'TEMPLATE_ID': template_id,
                    'WEB_URL': web_url,
                    'NAME': name
                })
        
        # 构建新的账号配置
        accounts_str = 'MULTI_ACCOUNT_CONFIG = [\n'
        for account in accounts:
            accounts_str += '    {\n'
            accounts_str += f"        'APP_ID': '{account['APP_ID']}',  # 公众号AppID\n"
            accounts_str += f"        'APP_SECRET': '{account['APP_SECRET']}',  # 公众号AppSecret\n"
            accounts_str += f"        'TEMPLATE_ID': '{account['TEMPLATE_ID']}',  # 模板消息ID\n"
            accounts_str += f"        'WEB_URL': '{account['WEB_URL']}',  # 公众号跳转URL\n"
            accounts_str += f"        'NAME': '{account['NAME']}'  # 账号名称\n"
            accounts_str += '    },\n'
        accounts_str = accounts_str.rstrip(',\n') + '\n]'
        
        # 替换账号配置
        content = re.sub(r'MULTI_ACCOUNT_CONFIG\s*=\s*\[.*?\]', accounts_str, content, flags=re.DOTALL)
        
        # 收集数据源配置
        data_sources = []
        source_count = int(config_data.get('source_count', 3))
        for i in range(1, source_count + 1):
            source_name = config_data.get(f'source_name_{i}', '')
            source_url = config_data.get(f'source_url_{i}', '')
            source_type = config_data.get(f'source_type_{i}', 'drissionpage')
            source_enabled = config_data.get(f'source_enabled_{i}', 'true') == 'true'
            source_sort_order = int(config_data.get(f'source_sort_order_{i}', i))
            
            if source_name and source_url:
                data_sources.append({
                    "name": source_name,
                    "url": source_url,
                    "type": source_type,
                    "enabled": source_enabled,
                    "sort_order": source_sort_order
                })
        
        # 按排序序号排序数据源
        data_sources.sort(key=lambda x: x['sort_order'])
        
        # 构建新的数据源配置
        # 先构建列表内容部分
        sources_list = ''
        for source in data_sources:
            sources_list += '    {\n'
            sources_list += f'        "name": "{source["name"]}",\n'
            sources_list += f'        "url": "{source["url"]}",\n'
            sources_list += f'        "type": "{source["type"]}",\n'
            sources_list += f'        "enabled": {source["enabled"]},\n'
            sources_list += f'        "sort_order": {source["sort_order"]}\n'
            sources_list += '    },\n'
        sources_list = sources_list.rstrip(',\n') + '\n'
        
        # 从原始配置中提取类型注解
        type_annotation = 'List[Dict[str, Any]]'
        type_annotation_match = re.search(r'GOLD_PRICE_SOURCES\s*[:]\s*([^=]+)=', content)
        if type_annotation_match:
            type_annotation = type_annotation_match.group(1).strip()
        
        # 构建完整的数据源配置
        sources_str = f'GOLD_PRICE_SOURCES: {type_annotation} = [\n{sources_list}]'
        
        # 替换数据源配置 - 使用手动定位方法，更可靠
        logger.info(f"尝试替换数据源配置，新配置: {sources_str[:100]}...")
        
        # 找到 GOLD_PRICE_SOURCES 的起始位置
        start_idx = content.find('GOLD_PRICE_SOURCES')
        if start_idx != -1:
            # 找到等号的位置（跳过类型注解）
            eq_idx = content.find('=', start_idx)
            if eq_idx != -1:
                # 找到等号后面的列表开始位置
                list_start = content.find('[', eq_idx)
                if list_start != -1:
                    # 找到列表结束的位置（匹配的闭括号）
                    bracket_count = 1
                    list_end = list_start + 1
                    while list_end < len(content) and bracket_count > 0:
                        if content[list_end] == '[':
                            bracket_count += 1
                        elif content[list_end] == ']':
                            bracket_count -= 1
                        list_end += 1
                    
                    if bracket_count == 0:
                        # 手动构建新内容
                        new_content = content[:start_idx] + sources_str + content[list_end:]
                        logger.info("数据源配置替换成功")
                        content = new_content
                    else:
                        logger.error("数据源配置替换失败，无法找到列表结束位置")
                else:
                    logger.error("数据源配置替换失败，无法找到列表开始位置")
            else:
                logger.error("数据源配置替换失败，无法找到等号")
        else:
            logger.error("数据源配置替换失败，无法找到 GOLD_PRICE_SOURCES")
        
        # 更新其他配置
        config_map = {
            'PUSH_START_TIME': f"'{config_data.get('push_start_time', '09:00')}'",
            'PUSH_END_TIME': f"'{config_data.get('push_end_time', '23:00')}'",
            'PUSH_INTERVAL_MINUTES': config_data.get('push_interval_minutes', 30),
            'REGULAR_PUSH_MINUTES': f"[{config_data.get('regular_push_minutes', '1,31')}]",
            'REGULAR_PUSH_WINDOW': config_data.get('regular_push_window', 5),
            'MAX_PUSH_COUNT': config_data.get('max_push_count', 1),
            'BATCH_PUSH_INTERVAL': config_data.get('batch_push_interval', 300),
            'GLOBAL_PUSH_INTERVAL': config_data.get('global_push_interval', 300),
            'DATA_FETCH_INTERVAL': config_data.get('data_fetch_interval', 300),
            'PRICE_CACHE_EXPIRATION': config_data.get('price_cache_expiration', 60),
            'DEFAULT_GOLD_PRICE': config_data.get('default_gold_price', 1100.0),
            'DEFAULT_PRICE_GAP_HIGH': config_data.get('default_price_gap_high', 15.0),
            'DEFAULT_PRICE_GAP_LOW': config_data.get('default_price_gap_low', 10.0),
            'PRICE_CHANGE_THRESHOLD': config_data.get('price_change_threshold', 5),

            'LOG_LEVEL': f"'{config_data.get('log_level', 'INFO')}'",
            'LOG_FILE': f"'{config_data.get('log_file', 'logs/gold_monitor.log')}'",
            'TEST_MODE': str(config_data.get('test_mode', False)).capitalize(),
            'ENABLE_AI_ANALYSIS': str(config_data.get('enable_ai_analysis', False)).capitalize(),
            'ENABLE_WECHAT_PUSH': str(config_data.get('enable_wechat_push', False)).capitalize(),
            'ENABLE_HTML_GENERATION': str(config_data.get('enable_html_generation', False)).capitalize(),
            'ENABLE_GUI_WINDOW': str(config_data.get('enable_gui_window', False)).capitalize(),
            'ENABLE_COMPILE': str(config_data.get('enable_compile', False)).capitalize(),
            'ENABLE_RUN_EXE': str(config_data.get('enable_run_exe', False)).capitalize(),
            'CONFIG_PASSWORD': f"'{config_data.get('config_password', password)}'",
            'DATA_SOURCE_MODE': f"'{config_data.get('data_source_mode', 'single')}'",
            'DATA_SOURCE_RETRY_COUNT': config_data.get('data_source_retry_count', 3),
            'DATA_SOURCE_RETRY_INTERVAL': config_data.get('data_source_retry_interval', 2),
            'DATA_SOURCE_TIMEOUT': config_data.get('data_source_timeout', 10)
        }
        
        for key, value in config_map.items():
            pattern = rf'{key}\s*=\s*[^\n]*'
            replacement = f'{key} = {value}'
            content = re.sub(pattern, replacement, content)
        
        # 如果没有CONFIG_PASSWORD配置，添加它
        if 'CONFIG_PASSWORD' not in content:
            # 在文件末尾添加
            content += '\n\n# ------------------------------\n'
            content += '# 配置页面密码\n'
            content += '# ------------------------------\n'
            content += f'CONFIG_PASSWORD = "{config_data.get("config_password", password)}"  # 配置页面访问密码\n'
        
        # 如果没有DATA_SOURCE_MODE配置，添加它
        if 'DATA_SOURCE_MODE' not in content:
            # 在文件末尾添加
            content += '\n\n# ------------------------------\n'
            content += '# 数据源获取配置\n'
            content += '# ------------------------------\n'
            content += 'DATA_SOURCE_MODE = "single"  # single: 单一获取, cycle: 循环获取\n'
        
        # 保存配置文件
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
            # 确保数据写入完全完成
            f.flush()  # 强制将缓冲区数据写入文件
            os.fsync(f.fileno())  # 强制将文件数据写入磁盘
        
        # 兼容模式：使用跨平台的文件系统同步
        try:
            from utils.cross_platform_utils import sync_filesystem
            sync_filesystem()
        except ImportError:
            pass  # 如果模块不可用，跳过同步
        
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 配置页面路由处理函数
def config_page_handler(app):
    """配置页面路由处理函数"""
    @app.route('/config', methods=['GET', 'POST'])
    def config_page():
        """配置页面"""
        # 获取当前密码
        current_password = get_config_password()
        
        # 导入配置
        import importlib
        import sys
        # 确保重新导入config模块
        if 'config' in sys.modules:
            del sys.modules['config']
        # 重新导入config模块
        import config
        # 确保使用的是重新导入的config模块
        from config import (
            MULTI_ACCOUNT_CONFIG, PUSH_START_TIME, PUSH_END_TIME, REGULAR_PUSH_MINUTES,
            REGULAR_PUSH_WINDOW, DATA_FETCH_INTERVAL, PUSH_INTERVAL_MINUTES, MAX_PUSH_COUNT,
            BATCH_PUSH_INTERVAL, GLOBAL_PUSH_INTERVAL, PRICE_CACHE_EXPIRATION, DEFAULT_GOLD_PRICE,
            DEFAULT_PRICE_GAP_HIGH, DEFAULT_PRICE_GAP_LOW, PRICE_CHANGE_THRESHOLD,
            LOG_LEVEL, LOG_FILE, TEST_MODE, CONFIG_PASSWORD, ENABLE_WECHAT_PUSH,
            ENABLE_HTML_GENERATION, ENABLE_GUI_WINDOW, ENABLE_COMPILE, ENABLE_RUN_EXE, ENABLE_AI_ANALYSIS,
            DATA_SOURCE_RETRY_COUNT, DATA_SOURCE_RETRY_INTERVAL, DATA_SOURCE_TIMEOUT, DATA_SOURCE_MODE,
            DATA_SOURCE_MODES, DATA_SOURCE_TYPES, GOLD_PRICE_SOURCES
        )
        
        # 清除缓存，确保使用最新的配置
        import importlib
        import sys
        # 确保重新导入config模块
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # GET请求处理
        if request.method == 'GET':
            # 首先检查admin登录状态
            if session.get('admin_logged_in'):
                # 已登录，直接显示配置页面，跳过密码验证
                return render_template('config_template.html',
                                     authenticated=True,
                                     password=current_password,
                                     update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                     MULTI_ACCOUNT_CONFIG=MULTI_ACCOUNT_CONFIG,
                                     PUSH_START_TIME=PUSH_START_TIME,
                                     PUSH_END_TIME=PUSH_END_TIME,
                                     PUSH_INTERVAL_MINUTES=PUSH_INTERVAL_MINUTES,
                                     REGULAR_PUSH_MINUTES=REGULAR_PUSH_MINUTES,
                                     REGULAR_PUSH_WINDOW=REGULAR_PUSH_WINDOW,
                                     MAX_PUSH_COUNT=MAX_PUSH_COUNT,
                                     BATCH_PUSH_INTERVAL=BATCH_PUSH_INTERVAL,
                                     GLOBAL_PUSH_INTERVAL=GLOBAL_PUSH_INTERVAL,
                                     DATA_FETCH_INTERVAL=DATA_FETCH_INTERVAL,
                                     PRICE_CACHE_EXPIRATION=PRICE_CACHE_EXPIRATION,
                                     DEFAULT_GOLD_PRICE=DEFAULT_GOLD_PRICE,
                                     DEFAULT_PRICE_GAP_HIGH=DEFAULT_PRICE_GAP_HIGH,
                                     DEFAULT_PRICE_GAP_LOW=DEFAULT_PRICE_GAP_LOW,
                                     PRICE_CHANGE_THRESHOLD=PRICE_CHANGE_THRESHOLD,
                                     LOG_LEVEL=LOG_LEVEL,
                                     LOG_FILE=LOG_FILE,
                                     TEST_MODE=TEST_MODE,
                                     ENABLE_AI_ANALYSIS=ENABLE_AI_ANALYSIS,
                                     ENABLE_WECHAT_PUSH=ENABLE_WECHAT_PUSH,
                                     ENABLE_HTML_GENERATION=ENABLE_HTML_GENERATION,
                                     ENABLE_GUI_WINDOW=ENABLE_GUI_WINDOW,
                                     ENABLE_COMPILE=ENABLE_COMPILE,
                                     ENABLE_RUN_EXE=ENABLE_RUN_EXE,
                                     CONFIG_PASSWORD=current_password,
                                     DATA_SOURCE_RETRY_COUNT=DATA_SOURCE_RETRY_COUNT,
                                     DATA_SOURCE_RETRY_INTERVAL=DATA_SOURCE_RETRY_INTERVAL,
                                     DATA_SOURCE_TIMEOUT=DATA_SOURCE_TIMEOUT,
                                     DATA_SOURCE_MODE=DATA_SOURCE_MODE,
                                     DATA_SOURCE_MODES=DATA_SOURCE_MODES,
                                     DATA_SOURCE_TYPES=DATA_SOURCE_TYPES,
                                     GOLD_PRICE_SOURCES=GOLD_PRICE_SOURCES)
            # 检查URL参数中的密码
            url_password = request.args.get('password')
            if url_password and url_password == current_password:
                # URL密码验证成功，直接显示配置页面
                return render_template('config_template.html',
                                     authenticated=True,
                                     password=url_password,
                                     update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                     MULTI_ACCOUNT_CONFIG=MULTI_ACCOUNT_CONFIG,
                                     PUSH_START_TIME=PUSH_START_TIME,
                                     PUSH_END_TIME=PUSH_END_TIME,
                                     PUSH_INTERVAL_MINUTES=PUSH_INTERVAL_MINUTES,
                                     REGULAR_PUSH_MINUTES=REGULAR_PUSH_MINUTES,
                                     REGULAR_PUSH_WINDOW=REGULAR_PUSH_WINDOW,
                                     MAX_PUSH_COUNT=MAX_PUSH_COUNT,
                                     BATCH_PUSH_INTERVAL=BATCH_PUSH_INTERVAL,
                                     GLOBAL_PUSH_INTERVAL=GLOBAL_PUSH_INTERVAL,
                                     DATA_FETCH_INTERVAL=DATA_FETCH_INTERVAL,
                                     PRICE_CACHE_EXPIRATION=PRICE_CACHE_EXPIRATION,
                                     DEFAULT_GOLD_PRICE=DEFAULT_GOLD_PRICE,
                                     DEFAULT_PRICE_GAP_HIGH=DEFAULT_PRICE_GAP_HIGH,
                                     DEFAULT_PRICE_GAP_LOW=DEFAULT_PRICE_GAP_LOW,
                                     PRICE_CHANGE_THRESHOLD=PRICE_CHANGE_THRESHOLD,
                                     LOG_LEVEL=LOG_LEVEL,
                                     LOG_FILE=LOG_FILE,
                                     TEST_MODE=TEST_MODE,
                                     ENABLE_AI_ANALYSIS=ENABLE_AI_ANALYSIS,
                                     ENABLE_WECHAT_PUSH=ENABLE_WECHAT_PUSH,
                                     ENABLE_HTML_GENERATION=ENABLE_HTML_GENERATION,
                                     ENABLE_GUI_WINDOW=ENABLE_GUI_WINDOW,
                                     ENABLE_COMPILE=ENABLE_COMPILE,
                                     ENABLE_RUN_EXE=ENABLE_RUN_EXE,
                                     CONFIG_PASSWORD=current_password,
                                     DATA_SOURCE_RETRY_COUNT=DATA_SOURCE_RETRY_COUNT,
                                     DATA_SOURCE_RETRY_INTERVAL=DATA_SOURCE_RETRY_INTERVAL,
                                     DATA_SOURCE_TIMEOUT=DATA_SOURCE_TIMEOUT,
                                     DATA_SOURCE_MODE=DATA_SOURCE_MODE,
                                     DATA_SOURCE_MODES=DATA_SOURCE_MODES,
                                     DATA_SOURCE_TYPES=DATA_SOURCE_TYPES,
                                     GOLD_PRICE_SOURCES=GOLD_PRICE_SOURCES)
            else:
                # 没有有效密码或密码错误，显示登录页面
                error_msg = '密码错误，请重新输入' if url_password else None
                return render_template('config_template.html',
                                     authenticated=False,
                                     error=error_msg)
        
        if request.method == 'POST':
            # 处理登录请求
            if 'action' not in request.form:
                password = request.form.get('password')
                if password == current_password:
                    # 登录成功，设置session状态
                    session['admin_logged_in'] = True
                    session['admin_username'] = 'config_user'
                    # 显示配置页面
                    return render_template('config_template.html',
                                         authenticated=True,
                                         password=password,
                                         update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                         MULTI_ACCOUNT_CONFIG=MULTI_ACCOUNT_CONFIG,
                                         PUSH_START_TIME=PUSH_START_TIME,
                                         PUSH_END_TIME=PUSH_END_TIME,
                                         PUSH_INTERVAL_MINUTES=PUSH_INTERVAL_MINUTES,
                                         REGULAR_PUSH_MINUTES=REGULAR_PUSH_MINUTES,
                                         REGULAR_PUSH_WINDOW=REGULAR_PUSH_WINDOW,
                                         MAX_PUSH_COUNT=MAX_PUSH_COUNT,
                                         BATCH_PUSH_INTERVAL=BATCH_PUSH_INTERVAL,
                                         GLOBAL_PUSH_INTERVAL=GLOBAL_PUSH_INTERVAL,
                                         DATA_FETCH_INTERVAL=DATA_FETCH_INTERVAL,
                                         PRICE_CACHE_EXPIRATION=PRICE_CACHE_EXPIRATION,
                                         DEFAULT_GOLD_PRICE=DEFAULT_GOLD_PRICE,
                                         DEFAULT_PRICE_GAP_HIGH=DEFAULT_PRICE_GAP_HIGH,
                                         DEFAULT_PRICE_GAP_LOW=DEFAULT_PRICE_GAP_LOW,
                                         PRICE_CHANGE_THRESHOLD=PRICE_CHANGE_THRESHOLD,
                                         LOG_LEVEL=LOG_LEVEL,
                                         LOG_FILE=LOG_FILE,
                                         TEST_MODE=TEST_MODE,
                                         ENABLE_AI_ANALYSIS=ENABLE_AI_ANALYSIS,
                                         ENABLE_WECHAT_PUSH=ENABLE_WECHAT_PUSH,
                                         ENABLE_HTML_GENERATION=ENABLE_HTML_GENERATION,
                                         ENABLE_GUI_WINDOW=ENABLE_GUI_WINDOW,
                                         ENABLE_COMPILE=ENABLE_COMPILE,
                                         ENABLE_RUN_EXE=ENABLE_RUN_EXE,
                                         CONFIG_PASSWORD=current_password,
                                         DATA_SOURCE_RETRY_COUNT=DATA_SOURCE_RETRY_COUNT,
                                         DATA_SOURCE_RETRY_INTERVAL=DATA_SOURCE_RETRY_INTERVAL,
                                         DATA_SOURCE_TIMEOUT=DATA_SOURCE_TIMEOUT,
                                         DATA_SOURCE_MODE=DATA_SOURCE_MODE,
                                         DATA_SOURCE_MODES=DATA_SOURCE_MODES,
                                         DATA_SOURCE_TYPES=DATA_SOURCE_TYPES,
                                         GOLD_PRICE_SOURCES=GOLD_PRICE_SOURCES)
                else:
                    # 登录失败
                    return render_template('config_template.html',
                                         authenticated=False,
                                         error='密码错误，请重新输入')
            # 处理保存配置请求
            elif request.form.get('action') == 'save':
                password = request.form.get('password')
                if password != current_password:
                    return render_template('config_template.html',
                                         authenticated=False,
                                         error='密码错误，无法保存配置')
                
                # 收集配置数据
                config_data = {
                    'push_start_time': request.form.get('push_start_time', '09:00'),
                    'push_end_time': request.form.get('push_end_time', '23:00'),
                    'push_interval_minutes': int(request.form.get('push_interval_minutes', 30)),
                    'regular_push_minutes': request.form.get('regular_push_minutes', '1,31'),
                    'regular_push_window': int(request.form.get('regular_push_window', 5)),
                    'max_push_count': int(request.form.get('max_push_count', 1)),
                    'batch_push_interval': int(request.form.get('batch_push_interval', 300)),
                    'global_push_interval': int(request.form.get('global_push_interval', 300)),
                    'data_fetch_interval': int(request.form.get('data_fetch_interval', 300)),
                    'price_cache_expiration': int(request.form.get('price_cache_expiration', 60)),
                    'default_gold_price': float(request.form.get('default_gold_price', 1100.0)),
                    'default_price_gap_high': float(request.form.get('default_price_gap_high', 15.0)),
                    'default_price_gap_low': float(request.form.get('default_price_gap_low', 10.0)),
                    'price_change_threshold': int(request.form.get('price_change_threshold', 5)),
                    'log_level': request.form.get('log_level', 'INFO'),
                    'log_file': request.form.get('log_file', 'logs/gold_monitor.log'),
                    'test_mode': 'test_mode' in request.form,
                    'enable_ai_analysis': 'enable_ai_analysis' in request.form,
                    'enable_wechat_push': 'enable_wechat_push' in request.form,
                    'enable_html_generation': 'enable_html_generation' in request.form,
                    'enable_gui_window': 'enable_gui_window' in request.form,
                    'enable_compile': 'enable_compile' in request.form,
                    'enable_run_exe': 'enable_run_exe' in request.form,
                    'config_password': request.form.get('config_password', current_password),
                    'data_source_mode': request.form.get('data_source_mode', 'single'),
                    'account_count': request.form.get('account_count', len(MULTI_ACCOUNT_CONFIG)),
                    'data_source_retry_count': int(request.form.get('data_source_retry_count', 3)),
                    'data_source_retry_interval': int(request.form.get('data_source_retry_interval', 2)),
                    'data_source_timeout': int(request.form.get('data_source_timeout', 10)),
                    'source_count': request.form.get('source_count', len(GOLD_PRICE_SOURCES))
                }
                
                # 收集数据源配置
                source_count = int(config_data.get('source_count', len(GOLD_PRICE_SOURCES)))
                for i in range(1, source_count + 1):
                    config_data[f'source_name_{i}'] = request.form.get(f'source_name_{i}', '')
                    config_data[f'source_url_{i}'] = request.form.get(f'source_url_{i}', '')
                    config_data[f'source_type_{i}'] = request.form.get(f'source_type_{i}', 'drissionpage')
                    config_data[f'source_enabled_{i}'] = request.form.get(f'source_enabled_{i}', 'true')
                    config_data[f'source_sort_order_{i}'] = request.form.get(f'source_sort_order_{i}', str(i))
                
                # 收集账号配置
                account_count = int(request.form.get('account_count', len(MULTI_ACCOUNT_CONFIG)))
                for i in range(1, account_count + 1):
                    config_data[f'app_id_{i}'] = request.form.get(f'app_id_{i}', '')
                    config_data[f'app_secret_{i}'] = request.form.get(f'app_secret_{i}', '')
                    config_data[f'template_id_{i}'] = request.form.get(f'template_id_{i}', '')
                    config_data[f'web_url_{i}'] = request.form.get(f'web_url_{i}', '')
                    config_data[f'name_{i}'] = request.form.get(f'name_{i}', '')
                
                # 保存配置
                if save_config_to_file(config_data, password):
                    # 彻底清除缓存
                    import importlib
                    import sys
                    # 确保重新导入config模块
                    if 'config' in sys.modules:
                        del sys.modules['config']
                    # 清除所有相关模块的缓存
                    for module_name in list(sys.modules.keys()):
                        if module_name.startswith('config'):
                            del sys.modules[module_name]
                    
                    # 添加适当的延迟，确保文件写入完全完成
                    time.sleep(1)  # 增加延迟到1秒，确保文件写入完全完成
                    
                    # 重新导入config模块
                    import config
                    # 重新导入配置变量
                    from config import (
                        MULTI_ACCOUNT_CONFIG, PUSH_START_TIME, PUSH_END_TIME, REGULAR_PUSH_MINUTES,
                        REGULAR_PUSH_WINDOW, DATA_FETCH_INTERVAL, PUSH_INTERVAL_MINUTES, MAX_PUSH_COUNT,
                        BATCH_PUSH_INTERVAL, GLOBAL_PUSH_INTERVAL, PRICE_CACHE_EXPIRATION, DEFAULT_GOLD_PRICE,
                        DEFAULT_PRICE_GAP_HIGH, DEFAULT_PRICE_GAP_LOW, PRICE_CHANGE_THRESHOLD,
                        LOG_LEVEL, LOG_FILE, TEST_MODE, CONFIG_PASSWORD, ENABLE_WECHAT_PUSH,
                        ENABLE_HTML_GENERATION, ENABLE_GUI_WINDOW, ENABLE_COMPILE, ENABLE_RUN_EXE, ENABLE_AI_ANALYSIS,
                        DATA_SOURCE_RETRY_COUNT, DATA_SOURCE_RETRY_INTERVAL, DATA_SOURCE_TIMEOUT, DATA_SOURCE_MODE,
                        DATA_SOURCE_MODES, DATA_SOURCE_TYPES, GOLD_PRICE_SOURCES
                    )
                    
                    # 显示保存成功信息
                    return render_template('config_template.html',
                                         authenticated=True,
                                         password=password,
                                         message='配置保存成功！',
                                         update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                         MULTI_ACCOUNT_CONFIG=MULTI_ACCOUNT_CONFIG,
                                         PUSH_START_TIME=PUSH_START_TIME,
                                         PUSH_END_TIME=PUSH_END_TIME,
                                         PUSH_INTERVAL_MINUTES=PUSH_INTERVAL_MINUTES,
                                         REGULAR_PUSH_MINUTES=REGULAR_PUSH_MINUTES,
                                         REGULAR_PUSH_WINDOW=REGULAR_PUSH_WINDOW,
                                         MAX_PUSH_COUNT=MAX_PUSH_COUNT,
                                         BATCH_PUSH_INTERVAL=BATCH_PUSH_INTERVAL,
                                         GLOBAL_PUSH_INTERVAL=GLOBAL_PUSH_INTERVAL,
                                         DATA_FETCH_INTERVAL=DATA_FETCH_INTERVAL,
                                         PRICE_CACHE_EXPIRATION=PRICE_CACHE_EXPIRATION,
                                         DEFAULT_GOLD_PRICE=DEFAULT_GOLD_PRICE,
                                         DEFAULT_PRICE_GAP_HIGH=DEFAULT_PRICE_GAP_HIGH,
                                         DEFAULT_PRICE_GAP_LOW=DEFAULT_PRICE_GAP_LOW,
                                         PRICE_CHANGE_THRESHOLD=PRICE_CHANGE_THRESHOLD,
                                         LOG_LEVEL=LOG_LEVEL,
                                         LOG_FILE=LOG_FILE,
                                         TEST_MODE=TEST_MODE,
                                         ENABLE_AI_ANALYSIS=ENABLE_AI_ANALYSIS,
                                         ENABLE_WECHAT_PUSH=ENABLE_WECHAT_PUSH,
                                         ENABLE_HTML_GENERATION=ENABLE_HTML_GENERATION,
                                         ENABLE_GUI_WINDOW=ENABLE_GUI_WINDOW,
                                         ENABLE_COMPILE=ENABLE_COMPILE,
                                         ENABLE_RUN_EXE=ENABLE_RUN_EXE,
                                         CONFIG_PASSWORD=config_data.get('config_password', password),
                                         DATA_SOURCE_RETRY_COUNT=DATA_SOURCE_RETRY_COUNT,
                                         DATA_SOURCE_RETRY_INTERVAL=DATA_SOURCE_RETRY_INTERVAL,
                                         DATA_SOURCE_TIMEOUT=DATA_SOURCE_TIMEOUT,
                                         DATA_SOURCE_MODE=DATA_SOURCE_MODE,
                                         DATA_SOURCE_MODES=DATA_SOURCE_MODES,
                                         DATA_SOURCE_TYPES=DATA_SOURCE_TYPES,
                                         GOLD_PRICE_SOURCES=GOLD_PRICE_SOURCES)
                else:
                    # 保存失败
                    return render_template('config_template.html',
                                         authenticated=True,
                                         password=password,
                                         message='配置保存失败，请检查错误信息',
                                         update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                         MULTI_ACCOUNT_CONFIG=MULTI_ACCOUNT_CONFIG,
                                         PUSH_START_TIME=PUSH_START_TIME,
                                         PUSH_END_TIME=PUSH_END_TIME,
                                         PUSH_INTERVAL_MINUTES=PUSH_INTERVAL_MINUTES,
                                         REGULAR_PUSH_MINUTES=REGULAR_PUSH_MINUTES,
                                         REGULAR_PUSH_WINDOW=REGULAR_PUSH_WINDOW,
                                         MAX_PUSH_COUNT=MAX_PUSH_COUNT,
                                         BATCH_PUSH_INTERVAL=BATCH_PUSH_INTERVAL,
                                         GLOBAL_PUSH_INTERVAL=GLOBAL_PUSH_INTERVAL,
                                         DATA_FETCH_INTERVAL=DATA_FETCH_INTERVAL,
                                         PRICE_CACHE_EXPIRATION=PRICE_CACHE_EXPIRATION,
                                         DEFAULT_GOLD_PRICE=DEFAULT_GOLD_PRICE,
                                         DEFAULT_PRICE_GAP_HIGH=DEFAULT_PRICE_GAP_HIGH,
                                         DEFAULT_PRICE_GAP_LOW=DEFAULT_PRICE_GAP_LOW,
                                         PRICE_CHANGE_THRESHOLD=PRICE_CHANGE_THRESHOLD,
                                         LOG_LEVEL=LOG_LEVEL,
                                         LOG_FILE=LOG_FILE,
                                         TEST_MODE=TEST_MODE,
                                         ENABLE_WECHAT_PUSH=ENABLE_WECHAT_PUSH,
                                         ENABLE_HTML_GENERATION=ENABLE_HTML_GENERATION,
                                         ENABLE_GUI_WINDOW=ENABLE_GUI_WINDOW,
                                         ENABLE_COMPILE=ENABLE_COMPILE,
                                         ENABLE_RUN_EXE=ENABLE_RUN_EXE,
                                         CONFIG_PASSWORD=current_password,
                                         DATA_SOURCE_RETRY_COUNT=DATA_SOURCE_RETRY_COUNT,
                                         DATA_SOURCE_RETRY_INTERVAL=DATA_SOURCE_RETRY_INTERVAL,
                                         DATA_SOURCE_TIMEOUT=DATA_SOURCE_TIMEOUT,
                                         DATA_SOURCE_MODE=DATA_SOURCE_MODE,
                                         DATA_SOURCE_MODES=DATA_SOURCE_MODES,
                                         DATA_SOURCE_TYPES=DATA_SOURCE_TYPES,
                                         GOLD_PRICE_SOURCES=GOLD_PRICE_SOURCES)
        
        # GET请求，显示登录页面
        return render_template('config_template.html',
                             authenticated=False)