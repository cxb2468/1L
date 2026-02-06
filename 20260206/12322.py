import datetime
import os
import socket
import threading
import sys
import webbrowser
from flask import Flask, render_template_string, request, redirect, session
from waitress import serve
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# 初始化 Flask
app = Flask(__name__)
app.secret_key = 'smart_task_board_2026'

# 文件配置
DATA_FILE = "message.txt"
HISTORY_FILE = "history.txt"
ADMIN_PASSWORD = "123"


# ----------------- 逻辑函数 -----------------

def get_host_ip():
    """获取本机局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# ----------------- HTML 模板 -----------------

# 员工查看页面：含语音朗读逻辑
USER_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><title>工作看板</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding-top: 50px; margin: 0; }
        .card { background: white; width: 85%; max-width: 900px; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 10px solid #ff9800; }
        h1 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
        .msg { font-size: 36px; color: #e65100; white-space: pre-line; line-height: 1.4; font-weight: bold; background: #fffde7; padding: 25px; border-radius: 8px; min-height: 200px; }
        .footer { color:#999; margin-top:20px; font-size: 14px; }
        .audio-tip { font-size: 13px; color: #007bff; background: #e3f2fd; padding: 8px 15px; border-radius: 5px; margin-bottom: 15px; display: inline-block; border: 1px solid #bbdefb; }
    </style>
</head>
<body>
    <div class="card">
        <div class="audio-tip">📢 语音功能已就绪。若未听到声音，请点击页面任意处激活。</div>
        <h1>📢 当前工作指令</h1>
        <div id="instruction" class="msg">{{ message }}</div>
        <div class="footer">最后更新时间: {{ time }} (每10秒自动刷新)</div>
    </div>

    <script>
        function speakMessage() {
            const text = document.getElementById('instruction').innerText.trim();
            if (!text || text === "暂无任务") return;

            // 检查内容是否更新，防止重复朗读
            const lastSpoken = localStorage.getItem('last_msg');
            if (text !== lastSpoken) {
                // 现代浏览器需要用户交互后才能播放声音
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'zh-CN';
                utterance.rate = 0.9; // 语速
                window.speechSynthesis.speak(utterance);
                localStorage.setItem('last_msg', text);
            }
        }
        // 尝试朗读
        window.onload = speakMessage;
        // 引导用户交互
        document.body.onclick = () => { 
            console.log("语音播报激活"); 
            speakMessage(); 
        };
    </script>
</body>
</html>
'''

# 管理员后台：集成历史记录显示
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><title>管理后台</title>
    <style>
        body { font-family: sans-serif; background: #2c3e50; color: white; padding: 20px; display: flex; gap: 20px; margin: 0; height: 100vh; box-sizing: border-box; }
        .main-panel { flex: 2; background: #34495e; padding: 25px; border-radius: 10px; display: flex; flex-direction: column; }
        .history-panel { flex: 1; background: #1a252f; padding: 20px; border-radius: 10px; overflow-y: auto; border: 1px solid #444; }
        textarea { width: 100%; flex-grow: 1; font-size: 18px; margin: 15px 0; padding: 12px; border-radius: 5px; border: none; box-sizing: border-box; background: #ecf0f1; color: #333; }
        button { background: #27ae60; color: white; border: none; padding: 15px; font-size: 18px; cursor: pointer; width: 100%; border-radius: 5px; font-weight: bold; }
        button:hover { background: #2ecc71; }
        .history-item { background: #2c3e50; padding: 12px; margin-bottom: 12px; border-radius: 5px; border-left: 4px solid #f1c40f; }
        .history-time { color: #bdc3c7; font-size: 11px; margin-bottom: 5px; border-bottom: 1px solid #444; }
        .history-content { white-space: pre-line; color: #ecf0f1; font-size: 13px; margin-top: 5px; }
        .logout { color: #95a5a6; text-decoration: none; font-size: 13px; float: right; }
    </style>
</head>
<body>
    <div class="main-panel">
        <div><a href="/logout" class="logout">退出登录</a><h2>🛠️ 指令发布中心</h2></div>
        <form action="/update" method="post" style="flex-grow: 1; display: flex; flex-direction: column;">
            <textarea name="new_msg" placeholder="在此输入工作指令...">{{ current_msg }}</textarea>
            <button type="submit">🚀 立即发布并保存记录</button>
        </form>
    </div>
    <div class="history-panel">
        <h3>📜 历史发布记录</h3>
        {% for item in logs %}
        <div class="history-item">
            <div class="history-time">{{ item.time }}</div>
            <div class="history-content">{{ item.content }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''


# ----------------- Flask 路由 -----------------

@app.route('/')
def index():
    msg = "暂无任务"
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            msg = f.read()
    now = datetime.datetime.now().strftime('%H:%M:%S')
    return render_template_string(USER_HTML, message=msg, time=now)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('pwd') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/admin')
        return "密码错误！"

    if not session.get('logged_in'):
        return '''<body style="background:#2c3e50;color:white;text-align:center;padding-top:100px;font-family:sans-serif;">
                    <form method="post"><h2>管理登录</h2>密码：<input type="password" name="pwd"> <button>登录</button></form>
                  </body>'''

    current_msg = ""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            current_msg = f.read()

    logs = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if " | " in line:
                    t, c = line.split(" | ", 1)
                    logs.append({"time": t, "content": c.replace("[BR]", "\n")})

    return render_template_string(ADMIN_HTML, current_msg=current_msg, logs=logs)


@app.route('/update', methods=['POST'])
def update():
    if session.get('logged_in'):
        new_msg = request.form.get("new_msg", "").strip()
        # 清理多余空行逻辑
        lines = [l.strip() for l in new_msg.splitlines() if l.strip()]
        final_msg = "\n".join(lines)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(final_msg)

        if final_msg:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} | {final_msg.replace(chr(10), '[BR]')}\n")

    return redirect('/admin')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')


# ----------------- 系统托盘与启动 -----------------

def create_tray_icon():
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (44, 62, 80))
    dc = ImageDraw.Draw(image)
    dc.ellipse((10, 10, 54, 54), fill=(255, 152, 0))
    return image


def on_quit(icon, item):
    icon.stop()
    os._exit(0)


def on_open_admin(icon, item):
    webbrowser.open(f"http://{get_host_ip()}:5000/admin")


def run_tray():
    icon = Icon("TaskBoard", create_tray_icon(), "任务看板服务器", menu=Menu(
        MenuItem("打开管理后台", on_open_admin),
        MenuItem("退出程序", on_quit)
    ))
    icon.run()


if __name__ == '__main__':
    host_ip = get_host_ip()
    print(f"服务器启动成功！\n员工访问: http://{host_ip}:5000\n后台管理: http://{host_ip}:5000/admin")

    # 启动托盘图标线程
    threading.Thread(target=run_tray, daemon=True).start()

    # 启动 Flask 服务
    serve(app, host='0.0.0.0', port=5000, threads=10)