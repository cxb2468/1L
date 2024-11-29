import sys
import win32gui
import win32con
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel


# 列出所有窗口标题
def enum_all_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title:
            windows.append((hwnd, window_title))


def list_open_windows():
    windows = []
    win32gui.EnumWindows(enum_all_windows_callback, windows)

    # 过滤出包含 "Edge" 的窗口
    edge_windows = [(hwnd, title) for hwnd, title in windows if "Edge" in title]

    # 将包含 "Edge" 的窗口标题赋值给 window_title
    window_titles = [title for hwnd, title in edge_windows]

    return windows, edge_windows, window_titles


# 查找并关闭 Edge 窗口
def enum_edge_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title and ("Edge" in window_title):
            windows.append((hwnd, window_title))


def close_edge_window():
    # 存储找到的窗口
    windows = []
    win32gui.EnumWindows(enum_edge_windows_callback, windows)

    if windows:
        for hwnd, title in windows:
            print(f"找到窗口: {title} (句柄: {hwnd})")
            # 尝试关闭窗口
            win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            print(f"已发送关闭消息到窗口: {title}")
    else:
        print("未找到 Microsoft Edge 窗口")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Window Manager')
        self.setGeometry(100, 100, 600, 400)

        self.list_button = QPushButton('列出所有窗口', self)
        self.list_button.clicked.connect(self.on_list_button_clicked)

        self.close_button = QPushButton('关闭 Edge 窗口', self)
        self.close_button.clicked.connect(self.on_close_button_clicked)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('日志:'))
        layout.addWidget(self.log_text)
        layout.addWidget(self.list_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def on_list_button_clicked(self):
        all_windows, edge_windows, edge_titles = list_open_windows()
        self.log_text.clear()

        # 显示所有窗口
        self.log_text.append("所有窗口:")
        for hwnd, title in all_windows:
            self.log_text.append(f"Window Handle: {hwnd}, Title: {title}")

        # 显示包含 "Edge" 的窗口
        self.log_text.append("\n包含 'Edge' 的窗口:")
        for hwnd, title in edge_windows:
            self.log_text.append(f"Window Handle: {hwnd}, Title: {title}")

        # 显示包含 "Edge" 的窗口标题
        self.log_text.append("\n包含 'Edge' 的窗口标题:")
        for title in edge_titles:
            self.log_text.append(title)

    def on_close_button_clicked(self):
        close_edge_window()
        self.log_text.append("已尝试关闭所有 Edge 窗口")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
