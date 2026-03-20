# 主入口文件
import time
import threading
import sys

# 导入配置
import config
from config.config import ENABLE_WECHAT_PUSH, ENABLE_HTML_GENERATION, ENABLE_GUI_WINDOW, ENABLE_COMPILE

# 导入Flask应用
from app import app
from app.routes import start_flask_app

# 导入监控模块
from monitor.monitor import run_gold_price_monitor

# 导入窗口模块
from gui.window import show_window

# 导入JSON调度器
from utils.json_scheduler import json_scheduler

if __name__ == "__main__":
    # 显示AI服务配置状态
    print("=== 黄金价格监控系统 ===")
    if config.config.is_configured():
        available_services = config.config.get_available_services()
        print(f"✓ 已配置AI服务: {', '.join(available_services)}")
    else:
        print("[警告] 未配置AI服务API密钥")
        print("  请参考 .env.example 文件配置API密钥以启用完整AI分析功能")
    print("")
    
    # 显示当前配置状态
    print("当前功能配置:")
    print(f"  - 微信推送: {'启用' if ENABLE_WECHAT_PUSH else '禁用'}")
    print(f"  - HTML生成: {'启用' if ENABLE_HTML_GENERATION else '禁用'}")
    print(f"  - GUI窗口: {'启用' if ENABLE_GUI_WINDOW else '禁用'}")
    print(f"  - 编译EXE: {'启用' if ENABLE_COMPILE else '禁用'}")
    print("")
    

    print("开始运行黄金价格监控...\n")
    
    # 启动Flask应用线程
    flask_thread = threading.Thread(target=start_flask_app, daemon=True)
    flask_thread.start()
    
    # 启动黄金价格监控
    import logging
    from logger.logger_config import get_logger
    logger = get_logger(__name__)
    logger.info("启动黄金价格监控线程...")
    monitor_thread = threading.Thread(target=run_gold_price_monitor, daemon=True, name="GoldMonitor")
    monitor_thread.start()
    
    # 根据配置决定是否显示窗口
    if ENABLE_GUI_WINDOW:
        # 显示窗口
        try:
            show_window()
        except Exception as e:
            logger.error(f"调用show_window函数失败: {e}")
            # 即使窗口显示失败，程序也能继续运行
            logger.info("窗口显示失败，程序将在后台持续运行")
    
    # 保持程序运行，定期检查监控线程状态
    logger.info("程序将在后台持续运行，按 Ctrl+C 退出")
    try:
        while True:
            if not monitor_thread.is_alive():
                logger.warning("监控线程已退出")
                break
            time.sleep(5)  # 每5秒检查一次
    except KeyboardInterrupt:
        print("\n程序被用户中断，正在安全退出...")
        logger.info("程序被用户中断，正在安全退出")
        # 清理资源
        json_scheduler.shutdown()
        sys.exit(0)
