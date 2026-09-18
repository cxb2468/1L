import sys
import os
import subprocess
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, \
    QCheckBox, QLineEdit, QMessageBox, QProgressBar
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt


class VideoProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # 允许接受拖拽事件
        self.setAcceptDrops(True)

        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.fixed_width = 640
        self.fixed_height = 480
        self.is_playing = False

    def initUI(self):
        # 创建布局
        main_layout = QVBoxLayout()

        # 选择视频文件
        file_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        file_button = QPushButton("选择视频文件")
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)
        main_layout.addLayout(file_layout)

        # 视频信息显示
        self.info_label = QLabel()
        main_layout.addWidget(self.info_label)

        # 视频预览
        self.video_label = QLabel()
        main_layout.addWidget(self.video_label)

        # 进度条和时长显示布局
        self.progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.mousePressEvent = self.progress_bar_mouse_press
        self.progress_bar.mouseMoveEvent = self.progress_bar_mouse_move
        self.progress_layout.addWidget(self.progress_bar)
        self.time_label = QLabel("0:00 / 0:00")
        self.progress_layout.addWidget(self.time_label)
        main_layout.addLayout(self.progress_layout)

        # 播放控制按钮
        self.control_layout = QHBoxLayout()
        self.play_button = QPushButton("播放")
        self.play_button.clicked.connect(self.toggle_video)
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_video)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.stop_button)
        main_layout.addLayout(self.control_layout)

        # 裁剪功能
        crop_layout = QHBoxLayout()
        self.crop_checkbox = QCheckBox("裁剪视频")
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("开始时间 (00:00:00 或 00:00 或秒数)")
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("结束时间 (00:00:00 或 00:00 或秒数)")
        self.start_time_input.textChanged.connect(self.auto_check_crop)
        self.end_time_input.textChanged.connect(self.auto_check_crop)
        crop_layout.addWidget(self.crop_checkbox)
        crop_layout.addWidget(self.start_time_input)
        crop_layout.addWidget(self.end_time_input)
        main_layout.addLayout(crop_layout)

        # 上下左右裁边功能
        trim_layout = QHBoxLayout()
        self.trim_checkbox = QCheckBox("上下左右裁边")
        self.left_trim_input = QLineEdit()
        self.left_trim_input.setPlaceholderText("左边裁边像素")
        self.right_trim_input = QLineEdit()
        self.right_trim_input.setPlaceholderText("右边裁边像素")
        self.top_trim_input = QLineEdit()
        self.top_trim_input.setPlaceholderText("上边裁边像素")
        self.bottom_trim_input = QLineEdit()
        self.bottom_trim_input.setPlaceholderText("下边裁边像素")
        self.left_trim_input.textChanged.connect(self.auto_check_trim)
        self.right_trim_input.textChanged.connect(self.auto_check_trim)
        self.top_trim_input.textChanged.connect(self.auto_check_trim)
        self.bottom_trim_input.textChanged.connect(self.auto_check_trim)
        trim_layout.addWidget(self.trim_checkbox)
        trim_layout.addWidget(self.left_trim_input)
        trim_layout.addWidget(self.right_trim_input)
        trim_layout.addWidget(self.top_trim_input)
        trim_layout.addWidget(self.bottom_trim_input)
        main_layout.addLayout(trim_layout)

        # 压缩功能
        compress_layout = QHBoxLayout()
        self.compress_checkbox = QCheckBox("压缩视频")
        self.crf_input = QLineEdit()
        self.crf_input.setPlaceholderText("CRF 值 (18 - 28) 越大越不清晰")
        self.crf_input.textChanged.connect(self.auto_check_compress)
        compress_layout.addWidget(self.compress_checkbox)
        compress_layout.addWidget(self.crf_input)
        main_layout.addLayout(compress_layout)

        # 修改分辨率功能
        resolution_layout = QHBoxLayout()
        self.resolution_checkbox = QCheckBox("修改分辨率")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("宽度")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("高度（可选）")
        self.width_input.textChanged.connect(self.auto_check_resolution)
        self.height_input.textChanged.connect(self.auto_check_resolution)
        resolution_layout.addWidget(self.resolution_checkbox)
        resolution_layout.addWidget(self.width_input)
        resolution_layout.addWidget(self.height_input)
        main_layout.addLayout(resolution_layout)

        # 截图功能
        screenshot_layout = QHBoxLayout()
        self.screenshot_checkbox = QCheckBox("截指定时间的截图")
        self.screenshot_time_input = QLineEdit()
        self.screenshot_time_input.setPlaceholderText("截图时间 (00:00:00 或 00:00 或秒数)")
        self.screenshot_time_input.textChanged.connect(self.auto_check_screenshot)
        screenshot_layout.addWidget(self.screenshot_checkbox)
        screenshot_layout.addWidget(self.screenshot_time_input)
        main_layout.addLayout(screenshot_layout)

        # 视频转GIF功能
        gif_layout = QHBoxLayout()
        self.gif_checkbox = QCheckBox("转换为GIF")
        self.gif_start_time_input = QLineEdit()
        self.gif_start_time_input.setPlaceholderText("开始时间 (00:00:00 或 00:00 或秒数)")
        self.gif_end_time_input = QLineEdit()
        self.gif_end_time_input.setPlaceholderText("结束时间 (00:00:00 或 00:00 或秒数)")
        self.gif_fps_input = QLineEdit()
        self.gif_fps_input.setPlaceholderText("FPS (默认15)")
        self.gif_scale_input = QLineEdit()
        self.gif_scale_input.setPlaceholderText("缩放比例 (0-1, 默认0.5)")
        self.gif_start_time_input.textChanged.connect(self.auto_check_gif)
        self.gif_end_time_input.textChanged.connect(self.auto_check_gif)
        self.gif_fps_input.textChanged.connect(self.auto_check_gif)
        self.gif_scale_input.textChanged.connect(self.auto_check_gif)
        gif_layout.addWidget(self.gif_checkbox)
        gif_layout.addWidget(self.gif_start_time_input)
        gif_layout.addWidget(self.gif_end_time_input)
        gif_layout.addWidget(self.gif_fps_input)
        gif_layout.addWidget(self.gif_scale_input)
        main_layout.addLayout(gif_layout)

        # 处理按钮
        self.process_button = QPushButton("处理视频")
        self.process_button.clicked.connect(self.on_btn_process)
        main_layout.addWidget(self.process_button)

        # 初始隐藏播放控制按钮和进度条
        self.play_button.setVisible(False)
        self.stop_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(False)

        self.setLayout(main_layout)
        self.setWindowTitle('视频处理工具')
        self.show()

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4)")
        if file_path:
            self.file_label.setText(file_path)
            self.cap = cv2.VideoCapture(file_path)
            self.show_video_info(file_path)
            self.toggle_video()
            # 显示播放控制按钮和进度条
            self.play_button.setVisible(True)
            self.stop_button.setVisible(True)
            self.progress_bar.setVisible(True)
            self.process_button.setEnabled(True)

            # 让 play_button 获得焦点
            self.play_button.setFocus()

    def show_video_info(self, file_path):
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为 MB
        bitrate = (file_size * 8 * 1024 * 1024) / (duration * 1000)  # 计算码率 (kbps)

        info_text = f"分辨率: {width}x{height} | 文件大小: {file_size:.2f} MB | 码率: {bitrate:.2f} kbps"
        self.info_label.setText(info_text)

        total_seconds = int(duration)
        minutes, seconds = divmod(total_seconds, 60)
        self.total_time_str = f"{minutes}:{seconds:02d}"
        self.time_label.setText(f"0:00 / {self.total_time_str}")

    def toggle_video(self):
        if self.cap:
            if self.timer.isActive():
                self.timer.stop()
                self.is_playing = False
                self.play_button.setText("播放")
            else:
                self.timer.start(30)
                self.is_playing = True
                self.play_button.setText("暂停")

    def stop_video(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.progress_bar.setValue(0)
            self.time_label.setText(f"0:00 / {self.total_time_str}")
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
            self.is_playing = False
            self.play_button.setText("播放")

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)
                total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                progress = int((current_frame / total_frames) * 100)
                self.progress_bar.setValue(progress)

                fps = self.cap.get(cv2.CAP_PROP_FPS)
                current_seconds = int(current_frame / fps)
                minutes, seconds = divmod(current_seconds, 60)
                current_time_str = f"{minutes}:{seconds:02d}"
                self.time_label.setText(f"{current_time_str} / {self.total_time_str}")
            else:
                self.stop_video()

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.fixed_width, self.fixed_height))
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.video_label.setPixmap(pixmap)

    def convert_time_format(self, time_str):
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return f"{minutes * 60 + seconds}"
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return f"{hours * 3600 + minutes * 60 + seconds}"
        return time_str

    def on_btn_process(self):
        input_file = self.file_label.text()
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的视频文件")
            return

        self.pause_video()
        self.process_button.setEnabled(False)

        if self.crop_checkbox.isChecked() or self.trim_checkbox.isChecked() or self.compress_checkbox.isChecked() or self.resolution_checkbox.isChecked():
            self.process_video(input_file)

        if self.screenshot_checkbox.isChecked():
            self.process_screenshot(input_file)

        if self.gif_checkbox.isChecked():
            self.process_gif(input_file)

    def process_video(self, input_file):

        output_file = os.path.splitext(input_file)[0] + "_processed.mp4"
        ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-y']

        if self.crop_checkbox.isChecked():
            start_time = self.start_time_input.text() or '0'
            end_time = self.end_time_input.text() or '0'
            if int(end_time) > int(start_time):
                start_time = self.convert_time_format(start_time)
                end_time = self.convert_time_format(end_time)
                ffmpeg_cmd.extend(['-ss', start_time, '-to', end_time])

        if self.trim_checkbox.isChecked():
            left_trim = self.left_trim_input.text() or '0'
            right_trim = self.right_trim_input.text() or '0'
            top_trim = self.top_trim_input.text() or '0'
            bottom_trim = self.bottom_trim_input.text() or '0'
            if int(left_trim) + int(right_trim) + int(top_trim) + int(bottom_trim) > 0:
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                new_width = width - int(left_trim) - int(right_trim)
                new_height = height - int(top_trim) - int(bottom_trim)
                ffmpeg_cmd.extend(['-filter:v', f'crop={new_width}:{new_height}:{left_trim}:{top_trim}'])

        if self.compress_checkbox.isChecked():
            crf = self.crf_input.text()
            if crf:
                ffmpeg_cmd.extend(['-crf', crf])

        if self.resolution_checkbox.isChecked():
            width = self.width_input.text()
            height = self.height_input.text()
            if width:
                if not height:
                    # 获取原视频的宽度和高度
                    original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    # 计算等比例缩放后的高度
                    height = int((int(width) / original_width) * original_height)
                ffmpeg_cmd.extend(['-s', f'{width}x{height}'])

        ffmpeg_cmd.append(output_file)
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            QMessageBox.information(self, "成功", "视频处理完成")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "错误", f"视频处理失败: {e}")
        finally:
            self.process_button.setEnabled(True)

    def process_screenshot(self, input_file):
        screenshot_time = self.screenshot_time_input.text()
        if screenshot_time:
            screenshot_time = self.convert_time_format(screenshot_time)
            screenshot_file = os.path.splitext(input_file)[0] + f"_screenshot_{screenshot_time}.jpg"
            screenshot_cmd = ['ffmpeg', '-i', input_file, '-y', '-ss', screenshot_time, '-vframes', '1',
                              screenshot_file]
            try:
                subprocess.run(screenshot_cmd, check=True)
                QMessageBox.information(self, "成功", f"截图已保存为: {screenshot_file}")
            except subprocess.CalledProcessError as e:
                QMessageBox.warning(self, "错误", f"截图失败: {e}")
            finally:
                self.process_button.setEnabled(True)

    def process_gif(self, input_file):
        gif_output = os.path.splitext(input_file)[0] + ".gif"
        gif_cmd = ['ffmpeg', '-i', input_file]

        # 添加开始和结束时间
        start_time = self.gif_start_time_input.text()
        end_time = self.gif_end_time_input.text()
        if start_time:
            start_time = self.convert_time_format(start_time)
            gif_cmd.extend(['-ss', start_time])
        if end_time:
            end_time = self.convert_time_format(end_time)
            gif_cmd.extend(['-to', end_time])

        # 添加FPS设置
        fps = self.gif_fps_input.text() if self.gif_fps_input.text() else "15"

        # 添加缩放设置
        scale = self.gif_scale_input.text() if self.gif_scale_input.text() else "0.5"

        # 添加GIF转换参数
        gif_cmd.extend([
            '-vf',
            f'fps={fps},scale=iw*{scale}:ih*{scale}:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0', '-y',
            gif_output
        ])

        try:
            subprocess.run(gif_cmd, check=True)
            QMessageBox.information(self, "成功", f"GIF已保存为: {gif_output}")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "错误", f"GIF转换失败: {e}")
        finally:
            self.process_button.setEnabled(True)

    def progress_bar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            total_width = self.progress_bar.width()
            click_x = event.pos().x()
            progress = int((click_x / total_width) * 100)
            self.seek_video(progress)

    def progress_bar_mouse_move(self, event):
        if event.buttons() & Qt.LeftButton:
            total_width = self.progress_bar.width()
            click_x = event.pos().x()
            progress = int((click_x / total_width) * 100)
            self.seek_video(progress)

    def seek_video(self, progress):
        if self.cap:
            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            target_frame = int((progress / 100) * total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            current_seconds = int(target_frame / fps)
            minutes, seconds = divmod(current_seconds, 60)
            current_time_str = f"{minutes}:{seconds:02d}"
            self.time_label.setText(f"{current_time_str} / {self.total_time_str}")
            self.progress_bar.setValue(progress)

            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.toggle_video()

    def pause_video(self):
        if self.timer.isActive():
            self.timer.stop()
            self.is_playing = False
            self.play_button.setText("播放")

    def auto_check_crop(self):
        if self.start_time_input.text() or self.end_time_input.text():
            self.crop_checkbox.setChecked(True)

    def auto_check_trim(self):
        if self.left_trim_input.text() or self.right_trim_input.text() or self.top_trim_input.text() or self.bottom_trim_input.text():
            self.trim_checkbox.setChecked(True)

    def auto_check_compress(self):
        if self.crf_input.text():
            self.compress_checkbox.setChecked(True)

    def auto_check_resolution(self):
        if self.width_input.text() or self.height_input.text():
            self.resolution_checkbox.setChecked(True)

    def auto_check_screenshot(self):
        if self.screenshot_time_input.text():
            self.screenshot_checkbox.setChecked(True)

    def auto_check_gif(self):
        if (self.gif_start_time_input.text() or self.gif_end_time_input.text() or
                self.gif_fps_input.text() or self.gif_scale_input.text()):
            self.gif_checkbox.setChecked(True)

    def dragEnterEvent(self, event):
        # 检查拖拽的是否是文件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # 获取拖拽的文件路径
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            # 检查文件是否为视频文件（简单示例，可根据需要扩展）
            if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                self.file_label.setText(file_path)
                self.cap = cv2.VideoCapture(file_path)
                self.show_video_info(file_path)
                self.toggle_video()
                # 显示播放控制按钮和进度条
                self.play_button.setVisible(True)
                self.stop_button.setVisible(True)
                self.progress_bar.setVisible(True)
                self.process_button.setEnabled(True)

                # 让 play_button 获得焦点
                self.play_button.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    processor = VideoProcessor()
    sys.exit(app.exec_())