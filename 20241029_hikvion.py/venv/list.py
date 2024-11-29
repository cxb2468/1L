import win32gui

def enum_all_windows_callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        window_title = win32gui.GetWindowText(hwnd)
        if window_title:
            windows.append((hwnd, window_title))

def list_open_windows():
    windows = []
    win32gui.EnumWindows(enum_all_windows_callback, windows)
    for hwnd, title in windows:
        print(f"Window Handle: {hwnd}, Title: {title}")

if __name__ == "__main__":
    list_open_windows()