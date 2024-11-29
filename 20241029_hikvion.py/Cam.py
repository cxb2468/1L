import sys
import cv2
import win32gui
import win32con
import numpy as np
from datetime import datetime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider


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

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            exit("摄像头未能成功打开")

        self.hide_windows = False
        self.hwnd = -1

        # 设置窗口初始信息
        self.setGeometry(100, 100, 200, 320)  # 自行修改窗口尺寸，适配下面的画面展示
        self.setWindowTitle('Video Player')
        self.label = QLabel(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(99)
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(40)
        self.set_opacity(self.slider.value())
        self.slider.valueChanged.connect(self.set_opacity_and_update_label)
        self.opacity_label = QLabel(str(self.slider.value()), self)
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.slider)
        opacity_layout.addWidget(self.opacity_label)
        layout = QVBoxLayout()
        layout.addLayout(opacity_layout)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.drag_position = QPoint()

        # 用于存储上一帧的ROI，进行对比
        self.previous_roi = None
        self.show()

        # 创建定时器
        self.change_detected_timer = QTimer(self)
        self.change_detected_timer.timeout.connect(self.reset_hide_window)
        self.change_detected_timer.setSingleShot(True)

    # 按下 ESC 键，关闭应用
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # 设置窗体透明度
    def set_opacity_and_update_label(self, value):
        self.set_opacity(value)
        self.opacity_label.setText(str(value))

    # 将滑动条的值映射到0.1-1.0的范围
    def set_opacity(self, value):
        opacity = value / 100.0
        self.setWindowOpacity(opacity)

    # 鼠标可以拖动窗体
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    # 从摄像头获取画面
    def show_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 获取指定区域的画面
            # 这是楼主环境下需要监控的区域大小，请自行调整
            x, y, w, h = 100, 100, 400, 400
            roi = frame[y:y + h, x:x + w]

            # 在这里对ROI进行翻转、镜像等处理
            # roi = cv2.flip(roi, 1)  # 1表示水平翻转
            roi = cv2.rotate(roi, cv2.ROTATE_180)  # 旋转180度

            # 变化检测
            if self.previous_roi is not None:
                # 计算两帧之间的差异
                diff = cv2.absdiff(self.previous_roi, roi)
                gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
                change_detected = np.sum(thresh) > 30000  # 预警值
                if change_detected:
                    # 触发特定动作
                    self.on_change_detected(np.sum(thresh))

                # 叠加差异图像到原始视频帧上
                diff_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                overlay = cv2.addWeighted(roi, 0.7, diff_image, 0.3, 0)

                # 获取当前时间并添加到图像上
                cv2.putText(overlay, f"{datetime.now()}", (4, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (255, 255, 255), 1)
                # 添加 np.sum(thresh) 和 self.hide_windows 的值
                hide_windows_status = f'{"Hidden" if self.hide_windows else "Visible"} thresh: {np.sum(thresh)}'
                text_color = (0, 0, 255) if change_detected else (255, 255, 255)
                cv2.putText(overlay, f'{hide_windows_status}', (4, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)

                # 使用叠加后的图像
                display_image = overlay
            else:
                display_image = roi

            # 更新上一帧
            self.previous_roi = roi

            rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)  # 转换颜色通道
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.label.setPixmap(pixmap)

    # 这里可以执行你想要的特定动作
    def on_change_detected(self, change_detected):
        print(f"{datetime.now()}  检测到变化！{change_detected}")
        if not self.hide_windows:
            self.hide_windows = True
            print(f'{datetime.now()}  hide_windows:{"隐藏" if self.hide_windows else "可见"}')
            self.hide_other_window()  # 隐藏指定窗口
        self.change_detected_timer.start(10000)  # 启动10秒定时器
        self.setWindowTitle(
            f'{datetime.now().strftime("%H:%M:%S")}-{"隐藏" if self.hide_windows else "可见"}-Video Player')

    # 替换为您要隐藏的窗口的信息
    # 查找并隐藏 Edge 窗口

    # 查找并关闭 Edge 窗口

    def hide_other_window(self):
        close_edge_window()
        print(f'{datetime.now()}  hide_windows:{"关闭" if self.hide_windows else "可见"}')


    # def hide_other_window(self):
    #     window_class = None
    #     window_title = "企业微信"
    #     # 查找窗口句柄
    #     self.hwnd = win32gui.FindWindow(window_class, window_title)
    #
    #     if self.hwnd:
    #         # 隐藏窗口
    #         win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def reset_hide_window(self):
        self.hide_windows = False
        print(f'{datetime.now()}  hide_windows:{"隐藏" if self.hide_windows else "可见"}')
        self.setWindowTitle(f'Video Player-可见')
        # 恢复窗口
        if self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    # 退出程序
    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()


    def update_frame():
        player.show_frame()
        # 递归调用自身，实现无限循环
        QTimer.singleShot(30, update_frame)


    update_frame()  # 第一次调用
    sys.exit(app.exec_())