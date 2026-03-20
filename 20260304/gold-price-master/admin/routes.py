# -*- coding: utf-8 -*-
"""
后台管理路由模块
提供后台管理页面的访问接口
"""

from flask import render_template, jsonify, request, session, redirect, url_for
from . import admin_bp
import json
import os
import time
from functools import wraps

# 添加请求频率限制装饰器
def rate_limit(limit=5, per=60):
    """限制请求频率：每per秒最多limit次请求"""
    def decorator(f):
        # 存储每个IP的请求时间
        requests = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.remote_addr
            
            # 检查IP是否在请求记录中
            if client_ip in requests:
                # 获取当前时间
                current_time = time.time()
                
                # 清理过期的请求记录
                requests[client_ip] = [t for t in requests[client_ip] if current_time - t < per]
                
                # 检查请求次数是否超过限制
                if len(requests[client_ip]) >= limit:
                    return jsonify({
                        'code': 429,
                        'message': '请求过于频繁，请稍后再试'
                    })
            
            # 记录当前请求
            if client_ip not in requests:
                requests[client_ip] = []
            requests[client_ip].append(time.time())
            
            # 执行原始函数
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

@admin_bp.route('/')
def admin_root():
    """admin模块根路由"""
    # 检查是否登录
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    else:
        return redirect(url_for('admin.admin_index'))

@admin_bp.route('/login')
def admin_login():
    """后台管理登录页面"""
    # 直接返回 HTML 文件内容，避免 Jinja2 解析
    login_html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'admin', 'login.html')
    with open(login_html_path, 'r', encoding='utf-8') as f:
        return f.read()

@admin_bp.route('/index')
def admin_index():
    """后台管理首页"""
    # 检查是否登录
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # 重定向到仪表盘页面
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/dashboard')
def admin_dashboard():
    """后台管理仪表盘页面"""
    # 检查是否登录
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # 直接返回 HTML 文件内容，避免 Jinja2 解析
    dashboard_html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'admin', 'dashboard.html')
    with open(dashboard_html_path, 'r', encoding='utf-8') as f:
        return f.read()

@admin_bp.route('/price-monitor')
def admin_price_monitor():
    """后台管理价格监控页面"""
    # 检查是否登录
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # 直接返回 HTML 文件内容，避免 Jinja2 解析
    price_monitor_html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'admin', 'price-monitor.html')
    with open(price_monitor_html_path, 'r', encoding='utf-8') as f:
        return f.read()

@admin_bp.route('/config')
def admin_config():
    """后台管理系统配置页面"""
    # 检查是否登录
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # 直接返回 HTML 文件内容，避免 Jinja2 解析
    config_html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'admin', 'config.html')
    with open(config_html_path, 'r', encoding='utf-8') as f:
        return f.read()

@admin_bp.route('/api/login', methods=['POST'])
def api_login():
    """登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 从配置文件获取密码
        from config.config import CONFIG_PASSWORD
        # 简单的登录验证
        if username == 'admin' and password == CONFIG_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return jsonify({
                'code': 200,
                'message': '登录成功'
            })
        else:
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}'
        })

@admin_bp.route('/logout')
def admin_logout():
    """退出登录"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/api/system-info')
def get_system_info():
    """获取系统信息"""
    try:
        # 导入必要的模块
        import psutil
        import time
        import datetime
        import platform
        
        # 获取系统基本信息 - 跨平台兼容
        # 获取启动时间并计算运行时间
        try:
            boot_timestamp = psutil.boot_time()
            uptime_seconds = time.time() - boot_timestamp
            uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        except (OSError, AttributeError) as e:
            logger.warning(f"获取系统启动时间失败: {e}")
            uptime_str = '未知'
        
        # 获取内存使用率
        try:
            memory_usage = f'{psutil.virtual_memory().percent}%'
        except (OSError, AttributeError) as e:
            logger.warning(f"获取内存使用率失败: {e}")
            memory_usage = '未知'
        
        # 获取CPU使用率
        try:
            cpu_usage = f'{psutil.cpu_percent(interval=0.1)}%'
        except (OSError, AttributeError) as e:
            logger.warning(f"获取CPU使用率失败: {e}")
            cpu_usage = '未知'
        
        # 获取磁盘使用率 - 跨平台兼容处理
        try:
            # 尝试多个可能的路径以确保跨平台兼容
            disk_usage = '未知'
            possible_paths = []
            
            # 根据不同系统添加可能的路径
            if platform.system() == 'Windows':
                possible_paths.append(os.getcwd())
                possible_paths.append('C:\\')
            else:
                # Linux/Unix 系统
                possible_paths.append(os.getcwd())
                possible_paths.append('/')
                possible_paths.append('/home')
                possible_paths.append('/root')
            
            # 尝试每个路径
            for disk_path in possible_paths:
                try:
                    if os.path.exists(disk_path):
                        disk_usage = f'{psutil.disk_usage(disk_path).percent}%'
                        break
                except (OSError, PermissionError) as e:
                    logger.debug(f"无法访问磁盘路径 {disk_path}: {e}")
                    continue
                    
        except (OSError, PermissionError) as e:
            logger.warning(f"获取磁盘使用率失败: {e}")
            disk_usage = '未知'
        
        system_info = {
            'version': '1.0.0',
            'platform': platform.system() + ' ' + platform.release(),
            'uptime': uptime_str,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'disk_usage': disk_usage
        }
        return jsonify({
            'code': 200,
            'data': system_info,
            'message': 'success'
        })
    except ImportError as e:
        # 如果psutil模块不存在，返回默认值
        system_info = {
            'version': '1.0.0',
            'platform': '未知',
            'uptime': '未知',
            'memory_usage': '未知',
            'cpu_usage': '未知',
            'disk_usage': '未知'
        }
        return jsonify({
            'code': 200,
            'data': system_info,
            'message': 'psutil模块不可用，无法获取系统信息'
        })
    except Exception as e:
        # 如果无法获取系统信息，返回默认值
        system_info = {
            'version': '1.0.0',
            'platform': '未知',
            'uptime': '未知',
            'memory_usage': '未知',
            'cpu_usage': '未知',
            'disk_usage': '未知'
        }
        return jsonify({
            'code': 200,
            'data': system_info,
            'message': f'获取系统信息失败，使用默认值: {str(e)}'
        })

@admin_bp.route('/api/price-data')
@rate_limit(limit=3, per=10)  # 每10秒最多3次请求
def get_price_data():
    """获取价格数据"""

    try:
        # 获取请求参数中的日期，如果没有则使用当天日期
        date_param = request.args.get('date')
        if date_param:
            # 验证日期格式
            try:
                # 解析日期字符串
                date_obj = time.strptime(date_param, '%Y-%m-%d')
                # 格式化为标准格式
                selected_date = time.strftime('%Y-%m-%d', date_obj)
            except ValueError:
                # 日期格式错误，使用当天日期
                selected_date = time.strftime('%Y-%m-%d')
        else:
            # 没有指定日期，使用当天日期
            selected_date = time.strftime('%Y-%m-%d')
        
        # 构建data目录路径
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # 检查并创建data目录
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 构建json文件路径
        json_file = os.path.join(data_dir, f'{selected_date.replace("-", "")}.json')
        
        # 导入数据源模块，获取实时价格
        from sources.data_source import get_gold_price, display_price_info
        from gold_alert import gold_alert_manager
        import config
        
        # 获取当前黄金价格（实时数据或缓存数据）
        # 直接调用get_gold_price()，用户认为数据源失败的情况不可能发生
        price, is_cache = get_gold_price()
        
        # 获取上次价格（如果有）
        last_price = getattr(gold_alert_manager, 'last_price', None)
        if last_price is None:
            last_price = price
        
        # 计算价格变化
        change_amount = price - last_price
        change_percent = (change_amount / last_price * 100)
        
        # 获取价格趋势
        arrow, direction = display_price_info(price, last_price)
        
        # 构建价格数据（实时数据或缓存数据）
        price_data = {
            'current_price': round(price, 2),
            'change_amount': round(change_amount, 2),
            'change_percent': round(change_percent, 2),
            'highest': round(price * 1.01, 2),  # 模拟最高价格
            'lowest': round(price * 0.99, 2),   # 模拟最低价格
            'volume': '未知',
            'turnover': '未知',
            'trend': direction,
            'is_cache': is_cache,
            'source': '缓存' if is_cache else '实时',
            'timestamp': int(time.time())
        }
        
        # 记录获取到的价格数据，确保与日志一致
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"获取金价数据: {price:.2f}/克, 来源: {'缓存' if is_cache else '实时'}")
        
        # 更新上次价格
        gold_alert_manager.last_price = price
        
        # 获取默认黄金价格
        default_gold_price = config.DEFAULT_GOLD_PRICE
        
        # 获取历史数据（基于JSON文件）
        history_data = []
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            
            # 筛选不重复时间的数据
            unique_data = []
            seen_times = set()
            
            for item in data_list:
                if 'datetime' in item:
                    time_str = item['datetime']
                    if time_str not in seen_times:
                        seen_times.add(time_str)
                        unique_data.append(item)
            
            # 构建历史数据
            for item in unique_data:
                price_data_info = item.get('price_data', {})
                current_price = price_data_info.get('price', 0)
                last_price = price_data_info.get('last_price', current_price)
                
                # 处理 None 值
                if current_price is None:
                    current_price = 0
                if last_price is None:
                    last_price = current_price
                
                change_amount = current_price - last_price
                
                # 构建历史数据项
                history_item = {
                    'time': item['datetime'],
                    'price': round(current_price, 2),
                    'change': round(change_amount, 2),
                    'source': '文件' if not price_data_info.get('status') else price_data_info.get('status')
                }
                history_data.append(history_item)
            
            # 按时间倒序排列，最新的在前面
            history_data.reverse()
        
        # 返回数据，包含实时价格和历史数据
        return jsonify({
            'code': 200,
            'data': {
                **price_data,
                'history': history_data,
                'default_gold_price': default_gold_price
            },
            'message': 'success'
        })
    except Exception as e:
        # 如果无法获取价格数据，使用配置中的默认黄金价格
        try:
            # 导入配置模块
            import config
            # 获取默认黄金价格
            default_gold_price = config.DEFAULT_GOLD_PRICE
        except Exception as e:
            # 如果无法获取配置，抛出异常，让项目停止并报错
            raise Exception(f'获取默认黄金价格失败: {str(e)}')
        
        price_data = {
            'current_price': default_gold_price,
            'change_amount': 0,
            'change_percent': 0,
            'highest': default_gold_price * 1.01,
            'lowest': default_gold_price * 0.99,
            'volume': '未知',
            'turnover': '未知',
            'trend': '稳定',
            'is_cache': False,
            'timestamp': int(time.time())
        }
        
        # 获取历史数据（基于JSON文件）
        history_data = []
        try:
            today = time.strftime('%Y-%m-%d')
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            json_file = os.path.join(data_dir, f'{today.replace("-", "")}.json')
            
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                
                # 筛选不重复时间的数据
                unique_data = []
                seen_times = set()
                
                for item in data_list:
                    if 'datetime' in item:
                        time_str = item['datetime']
                        if time_str not in seen_times:
                            seen_times.add(time_str)
                            unique_data.append(item)
                
                # 构建历史数据
                for item in unique_data:
                    price_data_info = item.get('price_data', {})
                    current_price = price_data_info.get('price', 0)
                    last_price = price_data_info.get('last_price', current_price)
                    
                    # 处理 None 值
                    if current_price is None:
                        current_price = 0
                    if last_price is None:
                        last_price = current_price
                    
                    change_amount = current_price - last_price
                    
                    # 构建历史数据项
                    history_item = {
                        'time': item['datetime'],
                        'price': round(current_price, 2),
                        'change': round(change_amount, 2),
                        'source': '文件' if not price_data_info.get('status') else price_data_info.get('status')
                    }
                    history_data.append(history_item)
                
                # 按时间倒序排列，最新的在前面
                history_data.reverse()
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"读取历史数据失败: {e}")
        
        return jsonify({
            'code': 200,
            'data': {
                **price_data,
                'history': history_data,
                'default_gold_price': default_gold_price
            },
            'message': f'获取价格数据失败，使用默认值: {str(e)}'
        })



@admin_bp.route('/api/config', methods=['GET'])
def get_config():
    """获取系统完整配置"""
    try:
        # 导入配置模块
        import sys
        if 'config.config' in sys.modules:
            del sys.modules['config.config']
        import config.config
        
        # 获取所有配置项
        config_data = {
            # 基本配置
            'monitor_interval': getattr(config.config, 'DATA_FETCH_INTERVAL', 300),
            'alert_threshold': getattr(config.config, 'PRICE_CHANGE_THRESHOLD', 5),
            'enable_wechat': getattr(config.config, 'ENABLE_WECHAT_PUSH', False),
            'enable_ai_analysis': getattr(config.config, 'ENABLE_AI_ANALYSIS', False),
            'enable_html_generation': getattr(config.config, 'ENABLE_HTML_GENERATION', True),
            'enable_gui_window': getattr(config.config, 'ENABLE_GUI_WINDOW', False),
            'test_mode': getattr(config.config, 'TEST_MODE', False),
            
            # 推送配置
            'push_start_time': getattr(config.config, 'PUSH_START_TIME', '09:00'),
            'push_end_time': getattr(config.config, 'PUSH_END_TIME', '23:00'),
            'push_interval_minutes': getattr(config.config, 'PUSH_INTERVAL_MINUTES', 30),
            'regular_push_minutes': getattr(config.config, 'REGULAR_PUSH_MINUTES', [1, 31]),
            'regular_push_window': getattr(config.config, 'REGULAR_PUSH_WINDOW', 5),
            'max_push_count': getattr(config.config, 'MAX_PUSH_COUNT', 1),
            'batch_push_interval': getattr(config.config, 'BATCH_PUSH_INTERVAL', 300),
            'global_push_interval': getattr(config.config, 'GLOBAL_PUSH_INTERVAL', 300),
            
            # 数据源配置
            'data_source_mode': getattr(config.config, 'DATA_SOURCE_MODE', 'single'),
            'data_source_retry_count': getattr(config.config, 'DATA_SOURCE_RETRY_COUNT', 3),
            'data_source_retry_interval': getattr(config.config, 'DATA_SOURCE_RETRY_INTERVAL', 2),
            'data_source_timeout': getattr(config.config, 'DATA_SOURCE_TIMEOUT', 10),
            
            # 微信配置
            'multi_account_config': getattr(config.config, 'MULTI_ACCOUNT_CONFIG', []),
            
            # 数据源列表
            'gold_price_sources': getattr(config.config, 'GOLD_PRICE_SOURCES', []),
            
            # 系统配置
            'log_level': getattr(config.config, 'LOG_LEVEL', 'INFO'),
            'log_file': getattr(config.config, 'LOG_FILE', 'logs/gold_monitor.log'),
            'price_cache_expiration': getattr(config.config, 'PRICE_CACHE_EXPIRATION', 60),
            
            # 价格配置
            'default_gold_price': getattr(config.config, 'DEFAULT_GOLD_PRICE'),
            'default_price_gap_high': getattr(config.config, 'DEFAULT_PRICE_GAP_HIGH', 15.0),
            'default_price_gap_low': getattr(config.config, 'DEFAULT_PRICE_GAP_LOW', 10.0),

            
            # 枚举配置
            'data_source_modes': getattr(config.config, 'DATA_SOURCE_MODES', {}),
            'data_source_types': getattr(config.config, 'DATA_SOURCE_TYPES', {})
        }
        
        return jsonify({
            'code': 200,
            'data': config_data,
            'message': 'success'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f'获取配置失败: {str(e)}'
        })

@admin_bp.route('/api/config', methods=['POST'])
def update_config():
    """更新系统配置 - 集成config_web.py逻辑"""
    try:
        data = request.get_json()
        
        # 导入config_web模块的保存函数
        from config.config_web import save_config_to_file, get_config_password
        
        # 获取当前密码
        current_password = get_config_password()
        
        # 准备配置数据格式
        config_data = {
            # 基本配置
            'data_fetch_interval': data.get('monitor_interval', 300),
            'price_change_threshold': data.get('alert_threshold', 5),
            'enable_wechat_push': data.get('enable_wechat', False),
            'enable_ai_analysis': data.get('enable_ai_analysis', False),
            'enable_html_generation': data.get('enable_html_generation', True),
            'enable_gui_window': data.get('enable_gui_window', False),
            'test_mode': data.get('test_mode', False),
            
            # 推送配置
            'push_start_time': data.get('push_start_time', '09:00'),
            'push_end_time': data.get('push_end_time', '23:00'),
            'push_interval_minutes': data.get('push_interval_minutes', 30),
            'regular_push_minutes': ','.join(map(str, data.get('regular_push_minutes', [1, 31]))),
            'regular_push_window': data.get('regular_push_window', 5),
            'max_push_count': data.get('max_push_count', 1),
            'batch_push_interval': data.get('batch_push_interval', 300),
            'global_push_interval': data.get('global_push_interval', 300),
            
            # 数据源配置
            'data_source_mode': data.get('data_source_mode', 'single'),
            'data_source_retry_count': data.get('data_source_retry_count', 3),
            'data_source_retry_interval': data.get('data_source_retry_interval', 2),
            'data_source_timeout': data.get('data_source_timeout', 10),
            
            # 微信配置
            'account_count': len(data.get('multi_account_config', [])),
            
            # 数据源列表
            'source_count': len(data.get('gold_price_sources', [])),
            
            # 系统配置
            'log_level': data.get('log_level', 'INFO'),
            'log_file': data.get('log_file', 'logs/gold_monitor.log'),
            'price_cache_expiration': data.get('price_cache_expiration', 60),
            
            # 价格配置
            'default_gold_price': data.get('default_gold_price', 1100.0),
            'default_price_gap_high': data.get('default_price_gap_high', 15.0),
            'default_price_gap_low': data.get('default_price_gap_low', 10.0),
            
            # 密码配置
            'config_password': data.get('config_password', current_password)
        }
        
        # 处理微信账号配置
        multi_accounts = data.get('multi_account_config', [])
        for i, account in enumerate(multi_accounts, 1):
            config_data[f'app_id_{i}'] = account.get('APP_ID', '')
            config_data[f'app_secret_{i}'] = account.get('APP_SECRET', '')
            config_data[f'template_id_{i}'] = account.get('TEMPLATE_ID', '')
            config_data[f'web_url_{i}'] = account.get('WEB_URL', '')
            config_data[f'name_{i}'] = account.get('NAME', '')
        
        # 处理数据源配置
        sources = data.get('gold_price_sources', [])
        for i, source in enumerate(sources, 1):
            config_data[f'source_name_{i}'] = source.get('name', '')
            config_data[f'source_url_{i}'] = source.get('url', '')
            config_data[f'source_type_{i}'] = source.get('type', 'drissionpage')
            config_data[f'source_enabled_{i}'] = str(source.get('enabled', True)).lower()
            config_data[f'source_sort_order_{i}'] = source.get('sort_order', i)
        
        # 调用config_web.py的保存函数
        success = save_config_to_file(config_data, current_password)
        
        if success:
            # 动态更新日志级别
            try:
                from logger.logger_config import update_log_level
                update_log_level()
            except Exception as e:
                logger.error(f"更新日志级别失败: {str(e)}")
            
            return jsonify({
                'code': 200,
                'message': '配置更新成功'
            })
        else:
            return jsonify({
                'code': 500,
                'message': '配置保存失败'
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f'配置更新失败: {str(e)}'
        })

@admin_bp.route('/api/logs')
def get_logs():
    """获取系统日志"""
    try:
        log_dir = 'logs'
        logs = []
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    # 读取最后几行日志
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-20:]  # 取最后20行
                        logs.extend([{
                            'filename': filename,
                            'content': ''.join(lines),
                            'timestamp': os.path.getmtime(filepath)
                        }])
        
        return jsonify({
            'code': 200,
            'data': logs,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取日志失败: {str(e)}'
        })
        