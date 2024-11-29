import win32gui
import win32con
import time

# 列出所有窗口标题
def enum_all_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title:
            windows.append((hwnd, window_title))

def list_open_windows():
    windows = []
    win32gui.EnumWindows(enum_all_windows_callback, windows)
    print(win32gui.EnumWindows(enum_all_windows_callback, windows))
    for hwnd, title in windows:
        print(f"Window Handle: {hwnd}, Title: {title}")

# 查找并隐藏 Edge 窗口
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

if __name__ == "__main__":
    list_open_windows()
    time.sleep(2)  # 等待2秒
    close_edge_window()
