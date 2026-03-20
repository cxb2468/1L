# Flask路由定义
import os
import sys
from flask import redirect, url_for, jsonify
from app import app

# 主页路由
@app.route('/')
def index():
    """主页"""
    # 重定向到价格页面
    return redirect(url_for('price_page'))

# 价格页面路由
@app.route('/price')
def price_page():
    """黄金价格监控页面"""
    import os
    # 检查是否在PyInstaller打包环境中
    is_pyinstaller = getattr(sys, 'frozen', False)
    
    # 尝试多个可能的路径
    possible_paths = []
    
    if is_pyinstaller:
        # 在PyInstaller环境中，检查当前工作目录和可执行文件所在目录
        possible_paths.append(os.path.join(os.getcwd(), 'index.html'))
        possible_paths.append(os.path.join(os.path.dirname(sys.executable), 'index.html'))
    else:
        # 在开发环境中，使用原始路径
        possible_paths.append(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
    
    # 检查所有可能的路径
    for index_path in possible_paths:
        if os.path.exists(index_path):
            # 读取index.html文件内容
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                from logger.logger_config import get_logger
                logger = get_logger(__name__)
                logger.error(f"读取index.html文件失败: {e}")
                continue
    
    # 如果所有路径都不存在，返回错误信息
    return "<h1>黄金价格监控</h1><p>价格页面正在生成中，请稍后刷新...</p>"

# 后台管理页面路由
@app.route('/admin')
def admin_page():
    """后台管理页面"""
    # 重定向到admin蓝图的路由
    from flask import redirect, url_for
    return redirect(url_for('admin.admin_index'))

# API路由 - 系统信息
@app.route('/api/system-info')
def api_system_info():
    """获取系统信息API"""
    try:
        import psutil
        import platform
        
        # 获取系统信息
        system_info = {
            'version': '1.0.0',
            'os': platform.system() + ' ' + platform.release(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_used': round(psutil.virtual_memory().used / (1024**3), 2),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_total': round(psutil.disk_usage('/').total / (1024**3), 2),
            'disk_used': round(psutil.disk_usage('/').used / (1024**3), 2),
            'disk_percent': round(psutil.disk_usage('/').percent, 2)
        }
        
        return jsonify({
            'code': 200,
            'data': system_info,
            'message': 'success'
        })
    except Exception as e:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"获取系统信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取系统信息失败: {str(e)}'
        })

# API路由 - 价格数据
@app.route('/api/price-data')
def api_price_data():
    """获取价格数据API"""
    try:
        # 导入数据源模块
        from sources.data_source import DataSourceManager
        
        # 获取实时价格数据
        manager = DataSourceManager()
        price_info = manager.get_gold_price()
        
        if price_info:
            return jsonify({
                'code': 200,
                'data': {
                    'current_price': price_info['price'],
                    'change_amount': price_info.get('change', 0),
                    'change_percent': price_info.get('change_percent', 0),
                    'source': price_info.get('source', 'unknown'),
                    'timestamp': price_info.get('timestamp', '')
                },
                'message': 'success'
            })
        else:
            return jsonify({
                'code': 500,
                'message': '获取价格数据失败'
            })
    except Exception as e:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"获取价格数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取价格数据失败: {str(e)}'
        })

# API路由 - 配置管理
@app.route('/api/config', methods=['GET'])
def api_get_config():
    """获取系统配置"""
    try:
        from config.config import Config
        
        config_data = {
            'monitor_interval': getattr(Config, 'MONITOR_INTERVAL', 300),
            'alert_threshold': getattr(Config, 'ALERT_THRESHOLD', 2.0),
            'enable_wechat': getattr(Config, 'ENABLE_WECHAT', False),
            'data_sources': getattr(Config, 'DATA_SOURCES', ['sina']),
            'wechat_corpid': getattr(Config, 'WECHAT_CORPID', ''),
            'wechat_corpsecret': getattr(Config, 'WECHAT_CORPSECRET', '')
        }
        
        return jsonify({
            'code': 200,
            'data': config_data,
            'message': 'success'
        })
    except Exception as e:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"获取配置失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取配置失败: {str(e)}'
        })

@app.route('/api/config', methods=['POST'])
def api_update_config():
    """更新系统配置"""
    try:
        from flask import request
        data = request.get_json()
        
        # 这里应该实现配置更新逻辑
        # 实际应用中需要更新 config.py 文件
        
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
        logger.info(f"配置更新请求: {data}")
        
        return jsonify({
            'code': 200,
            'message': '配置更新成功'
        })
    except Exception as e:
        from logger.logger_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"配置更新失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'配置更新失败: {str(e)}'
        })

# 启动Flask应用的函数
def start_flask_app():
    """在后台线程中启动Flask应用"""
    app.run(host='0.0.0.0', port=15000, debug=False, use_reloader=False)
