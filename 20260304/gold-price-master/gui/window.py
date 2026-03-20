# 窗口显示模块
import os
import webbrowser

# 尝试导入tkinter用于创建窗口
try:
    import tkinter as tk
    from tkinter import ttk
    import tkinter.messagebox
    has_tkinter = True
except ImportError:
    has_tkinter = False

# 导入日志配置
from logger.logger_config import get_logger

# 获取日志记录器
logger = get_logger(__name__)

def show_window():
    """
    显示Windows窗口，提供系统状态和访问按钮
    """
    if not has_tkinter:
        logger.info("tkinter未安装，跳过窗口显示")
        return
    
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("黄金价格监控系统")
        root.geometry("800x600")
        root.resizable(True, True)
        
        # 设置窗口图标
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'favicon', 'favicon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"无法设置窗口图标: {e}")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        title_label = ttk.Label(main_frame, text="黄金价格监控系统", font=("微软雅黑", 20, "bold"))
        title_label.pack(pady=20)
        
        # 添加状态信息
        status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        status_text = ttk.Label(status_frame, text="系统正在运行中...", font=("微软雅黑", 12))
        status_text.pack(pady=10)
        
        # 添加访问按钮
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # 配置页面按钮
        config_btn = ttk.Button(buttons_frame, text="访问配置页面", command=lambda: webbrowser.open("http://localhost:5000/config"))
        config_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 价格页面按钮
        price_btn = ttk.Button(buttons_frame, text="访问价格页面", command=lambda: webbrowser.open("http://localhost:5000/price"))
        price_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # 添加提示信息
        tips_frame = ttk.LabelFrame(main_frame, text="使用提示", padding="10")
        tips_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tips_text = """使用说明：

1. 系统会自动监控黄金价格变化
2. 当价格达到预警阈值时，会通过微信公众号发送提醒
3. 点击上方按钮访问配置页面和价格页面
4. 配置页面默认密码：admin888
5. 登录后请立即修改密码

系统状态：
- Flask服务器运行在 http://localhost:5000
- 黄金价格监控正在进行中
- 数据获取间隔：5分钟
"""
        tips_label = ttk.Label(tips_frame, text=tips_text, font=("微软雅黑", 10), justify=tk.LEFT, anchor=tk.NW)
        tips_label.pack(fill=tk.BOTH, expand=True)
        
        # 添加关闭按钮
        close_btn = ttk.Button(main_frame, text="关闭窗口", command=root.destroy)
        close_btn.pack(pady=20, fill=tk.X, expand=True)
        
        # 运行窗口主循环
        root.mainloop()
    except Exception as e:
        logger.error(f"显示窗口失败: {e}")
