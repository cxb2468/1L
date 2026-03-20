import time
import threading
import pyautogui
from pynput.keyboard import Key, Listener

# ========== 用户配置区 ==========
CLICK_INTERVAL = 0.3            # 每个点击之间的间隔（秒）
CLICK_BUTTON = 'left'            # 'left' 或 'right'
LOOP_COUNT = 0                   # 循环次数，0表示无限循环
RECORD_HOTKEY = Key.f3            # 记录当前鼠标位置为点击点
START_HOTKEY = Key.f1             # 开始循环点击
STOP_HOTKEY = Key.f2              # 停止点击
EXIT_HOTKEY = Key.esc             # 完全退出程序
# ===============================

class MultiPointClicker:
    def __init__(self):
        self.points = []           # 存储点击点 [(x1,y1), (x2,y2), ...]
        self.running = False       # 是否正在循环点击
        self.thread = None          # 点击线程
        self.click_button = CLICK_BUTTON   # ✅ 直接使用字符串，例如 'left'

    def add_point(self):
        """记录当前鼠标位置为一个点击点"""
        x, y = pyautogui.position()
        self.points.append((x, y))
        print(f"[+] 已记录点 {len(self.points)}: ({x}, {y})")

    def show_points(self):
        """显示所有记录的点位"""
        if not self.points:
            print("[-] 当前没有记录任何点击点")
        else:
            print(" 当前点击点列表：")
            for i, (x, y) in enumerate(self.points, 1):
                print(f"   点 {i}: ({x}, {y})")

    def clear_points(self):
        """清空所有记录的点位"""
        self.points.clear()
        print("[+] 所有点击点已清空")

    def start_loop(self):
        """开始循环点击"""
        if not self.points:
            print("[-] 请先记录至少一个点击点（按 F3 记录）")
            return
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._click_loop)
            self.thread.daemon = True
            self.thread.start()
            print(f"[+] 开始循环点击，共 {len(self.points)} 个点，间隔 {CLICK_INTERVAL*1000:.0f}ms")

    def stop_loop(self):
        """停止循环点击"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1)
            print("[+] 循环点击已停止")

    def _click_loop(self):
        """点击循环（在新线程中运行）"""
        count = 0
        while self.running:
            for x, y in self.points:
                if not self.running:
                    break
                # 移动到该点并点击
                pyautogui.moveTo(x, y)
                pyautogui.click(button=self.click_button)   # ✅ 现在正确接受字符串
                time.sleep(CLICK_INTERVAL)
            # 完成一轮，增加计数
            count += 1
            if LOOP_COUNT > 0 and count >= LOOP_COUNT:
                print(f"[+] 已完成 {LOOP_COUNT} 轮循环，自动停止")
                self.running = False
                break

    def on_press(self, key):
        """键盘按下事件处理"""
        try:
            if key == RECORD_HOTKEY:
                self.add_point()
            elif key == START_HOTKEY:
                self.start_loop()
            elif key == STOP_HOTKEY:
                self.stop_loop()
            elif key == EXIT_HOTKEY:
                print("[+] 退出程序")
                self.stop_loop()
                return False   # 停止监听，退出程序
        except Exception as e:
            print(f"[-] 键盘处理出错: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=== 多点循环连点器 2.0 ===")
    print(f"记录点: {RECORD_HOTKEY}  开始: {START_HOTKEY}  停止: {STOP_HOTKEY}  退出: {EXIT_HOTKEY}")
    print(f"当前设置: 按键={CLICK_BUTTON}, 间隔={CLICK_INTERVAL*1000:.0f}ms, 循环次数={LOOP_COUNT if LOOP_COUNT>0 else '无限'}")
    print("\n操作指南：")
    print("1. 将鼠标移动到要点击的位置，按 F3 记录该点")
    print("2. 重复步骤1记录所有需要的点（至少一个）")
    print("3. 按 F1 开始循环点击")
    print("4. 按 F2 暂停点击，按 ESC 退出程序")
    print("\n程序已启动，正在监听键盘...")

    try:
        clicker = MultiPointClicker()
        with Listener(on_press=clicker.on_press) as listener:
            listener.join()
    except Exception as e:
        print(f"[-] 程序启动失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n程序已退出。按回车键关闭窗口...")
    input()  # 暂停，让用户看到信息

if __name__ == "__main__":
    main()