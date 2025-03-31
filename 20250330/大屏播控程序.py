import sys
import os
import json
import screeninfo
import win32gui
import win32con
import pythoncom  # 修正：使用pythoncom替代win32com.client
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QListWidget, QPushButton, QFileDialog, QLabel, QSlider, 
                            QComboBox, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor, QLinearGradient, QPainter, QFont
import vlc
from vlc import State

class StyledGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #2a82da;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: rgba(20, 30, 50, 180);
                color: #ffffff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

class StyledButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #3a7bd5, stop:1 #00d2ff);
                border: 1px solid #2a82da;
                border-radius: 5px;
                color: white;
                padding: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #4a8be5, stop:1 #10e2ff);
                border: 1px solid #3a92ea;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                stop:0 #2a6bc5, stop:1 #00c2ef);
                padding-top: 6px;
                padding-bottom: 4px;
            }
        """)

class StyledListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 40, 60, 200);
                border: 1px solid #2a82da;
                border-radius: 5px;
                color: #ffffff;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid rgba(42, 130, 218, 50);
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: rgba(42, 130, 218, 150);
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(30, 40, 60, 200);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2a82da;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

class StyledSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        if orientation == Qt.Horizontal:
            self.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 6px;
                    background: rgba(30, 40, 60, 200);
                    border-radius: 3px;
                }
                QSlider::sub-page:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #3a7bd5, stop:1 #00d2ff);
                    border-radius: 3px;
                }
                QSlider::add-page:horizontal {
                    background: rgba(42, 130, 218, 50);
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    width: 14px;
                    margin: -4px 0;
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                              fx:0.5, fy:0.5,
                                              stop:0 #ffffff, stop:1 #2a82da);
                    border-radius: 7px;
                }
            """)
        else:
            self.setStyleSheet("""
                QSlider::groove:vertical {
                    width: 6px;
                    background: rgba(30, 40, 60, 200);
                    border-radius: 3px;
                }
                QSlider::sub-page:vertical {
                    background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                              stop:0 #3a7bd5, stop:1 #00d2ff);
                    border-radius: 3px;
                }
                QSlider::add-page:vertical {
                    background: rgba(42, 130, 218, 50);
                    border-radius: 3px;
                }
                QSlider::handle:vertical {
                    height: 14px;
                    margin: 0 -4px;
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                              fx:0.5, fy:0.5,
                                              stop:0 #ffffff, stop:1 #2a82da);
                    border-radius: 7px;
                }
            """)

class StyledComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 40, 60, 200);
                border: 1px solid #2a82da;
                border-radius: 5px;
                color: white;
                padding: 5px;
                padding-left: 10px;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 1px solid #3a92ea;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #2a82da;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox::down-arrow {
                image: url(none);
                width: 10px;
                height: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 40, 60, 200);
                border: 1px solid #2a82da;
                selection-background-color: rgba(42, 130, 218, 150);
                color: white;
            }
        """)

class ExtendedScreenPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        pythoncom.CoInitialize()  # 修正：使用pythoncom进行COM初始化
        
        # 初始化变量
        self.playlist = []
        self.current_index = -1
        self.instance = vlc.Instance("--aout=directsound")
        self.main_player = self.instance.media_player_new("--aout=directsound")
        self.preview_player = self.instance.media_player_new("--aout=directsound")
        self.mode = "扩展模式"
        self.screen_modes = ["扩展模式", "主屏模式", "双屏模式"]
        self.play_mode = True
        self.current_volume = 100
        self._volume = 100
        
        # 初始化UI
        self.setup_ui_style()
        self.init_ui()
        self.init_screens()
        
        # 初始化定时器
        self.media_timer = QTimer(self)
        self.media_timer.timeout.connect(self.update_media_status)
        self.media_timer.start(200)
        
        # 初始化动画相关
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.fade_process)
        self.fade_duration = 8000
        self.fade_steps = 30
        self.fade_step_interval = self.fade_duration // self.fade_steps
        self.fade_animation = None
        self.fading_out = False
        self.fading_in = False
        
        # 显示初始界面
        self.show()
        self.show_home_screen()
        self.setAcceptDrops(True)
        
        self.playback_paused = False  # 新增暂停状态标记
        self.current_media_position = 0  # 记录当前播放位置

    def setup_ui_style(self):
        """设置全局UI样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #0f2027, stop:1 #2c5364);
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLabel#status_label {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(20, 30, 50, 180);
                border-radius: 5px;
                border: 1px solid #2a82da;
            }
        """)
        
        # 设置全局字体
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        QApplication.setFont(font)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('大屏播控系统')
        self.setWindowIcon(QIcon('icon.png')) if os.path.exists('icon.png') else None
        self.setGeometry(100, 100, 1200, 800)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 左侧控制面板
        control_panel = StyledGroupBox("控制面板")
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(450)
        
        # 播放列表
        self.playlist_widget = StyledListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_item)
        control_layout.addWidget(QLabel("播放列表:"))
        control_layout.addWidget(self.playlist_widget)
                
        # 播放控制按钮
        btn_layout = QHBoxLayout()
        controls = [
            ('🏠', self.show_home_screen, '返回首页画面'),
            ('⏮', self.prev_item, '播放上一项'),
            ('⏯', self.toggle_play, '播放/暂停'),
            ('⏹', self.stop, '停止播放'),
            ('⏭', self.next_item, '播放下一项')
        ]
        for text, callback, tip in controls:
            btn = StyledButton(text)
            btn.clicked.connect(callback)
            btn.setFixedSize(70, 50)
            btn.setToolTip(tip)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    min-width: 30px;
                }
            """)
            btn_layout.addWidget(btn)
        control_layout.addLayout(btn_layout)
        
        # 进度条
        self.position_slider = StyledSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        control_layout.addWidget(self.position_slider)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        self.volume_slider = StyledSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        control_layout.addLayout(volume_layout)
        
        # 文件操作按钮
        file_btn_layout = QHBoxLayout()
        file_controls = [
            ('添加文件', self.add_files),
            ('删除选中', self.remove_selected),
            ('清空列表', self.clear_playlist)
        ]
        for text, callback in file_controls:
            btn = StyledButton(text)
            btn.clicked.connect(callback)
            file_btn_layout.addWidget(btn)
        control_layout.addLayout(file_btn_layout)
        
        # 播放模式选择
        self.mode_combo = StyledComboBox()
        self.mode_combo.addItems(self.screen_modes)
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        control_layout.addWidget(QLabel("播放模式:"))
        control_layout.addWidget(self.mode_combo)
        
        # 播放模式切换按钮
        self.play_mode_btn = StyledButton('连续播放')
        self.play_mode_btn.clicked.connect(self.toggle_play_mode)
        control_layout.addWidget(self.play_mode_btn)
        
        # 列表管理按钮
        list_btn_layout = QHBoxLayout()
        list_controls = [
            ('保存列表', self.save_playlist),
            ('加载列表', self.load_playlist)
        ]
        for text, callback in list_controls:
            btn = StyledButton(text)
            btn.clicked.connect(callback)
            list_btn_layout.addWidget(btn)
        control_layout.addLayout(list_btn_layout)
        
        # 右侧预览区域
        preview_panel = StyledGroupBox("预览")
        preview_layout = QVBoxLayout()
        preview_panel.setLayout(preview_layout)
        
        # 视频预览窗口
        self.preview_window = QLabel()
        self.preview_window.setAlignment(Qt.AlignCenter)
        self.preview_window.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 2px solid #2a82da;
                border-radius: 5px;
            }
        """)
        self.preview_window.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        preview_layout.addWidget(self.preview_window)
        
        # 状态栏
        self.status_bar = QLabel('大屏准备就绪')
        self.status_bar.setObjectName("status_label")
        preview_layout.addWidget(self.status_bar)
        
        # 主布局添加组件
        main_layout.addWidget(control_panel)
        main_layout.addWidget(preview_panel)

    def init_screens(self):
        """初始化屏幕配置"""
        try:
            self.screens = screeninfo.get_monitors()
            if len(self.screens) > 1:
                self.ext_screen = self.screens[1]
                self._create_video_window()
                self._hide_taskbar()
            else:
                self.status_bar.setText('警告：未检测到扩展屏幕，将使用主屏幕播放！')
                self._create_fallback_window()
        except Exception as e:
            self.status_bar.setText(f'屏幕检测失败: {str(e)}')
            self._create_fallback_window()

    def _create_video_window(self):
        """创建扩展屏播放窗口"""
        self.video_window = QWidget()
        self.video_window.setWindowTitle('扩展屏幕播放器')
        self.video_window.setGeometry(
            self.ext_screen.x, self.ext_screen.y,
            self.ext_screen.width, self.ext_screen.height
        )
        self.video_window.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.video_window.setStyleSheet("background-color: black;")
        self.video_window.showFullScreen()

    def _create_fallback_window(self):
        """创建集成到主界面右侧的监看窗口"""
        self.video_window = self.preview_window
        self.preview_player.set_hwnd(0)

    def change_mode(self, mode):
        """切换播放模式"""
        self.mode = mode
        if mode == "扩展模式" and hasattr(self, 'ext_screen'):
            self._create_video_window()
        else:
            if hasattr(self, 'video_window') and self.video_window != self.preview_window:
                self.video_window.close()
            self.video_window = self.preview_window

    def toggle_play_mode(self):
        """切换播放模式"""
        self.play_mode = not self.play_mode
        self.play_mode_btn.setText('连续播放' if self.play_mode else '单个播放')

    def play_selected_item(self, item):
        """处理双击播放列表项事件"""
        row = self.playlist_widget.row(item)
        self.play_item(row)

    def play_item(self, index):
        """播放指定索引的媒体"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            file_path = self.playlist[index]
            is_image = file_path.lower().endswith(('.jpg', '.jpeg', '.png'))
            
            if not self.play_mode and is_image:
                self._setup_single_image_playback()
                if hasattr(self, 'video_window') and self.video_window != self.preview_window:
                    for child in self.video_window.findChildren(QLabel):
                        child.deleteLater()
                try:
                    pixmap = QPixmap(file_path)
                    if pixmap.isNull():
                        raise ValueError("图片加载失败")
                        
                    # 在主预览窗口显示
                    scaled_pixmap = pixmap.scaled(
                        QSize(800, 600),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.preview_window.setPixmap(scaled_pixmap)
                    
                    # 扩展屏显示逻辑
                    if hasattr(self, 'video_window') and self.video_window != self.preview_window:
                        ext_label = QLabel(self.video_window)
                        ext_pixmap = pixmap.scaled(
                            QSize(800, 600),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        ext_label.setPixmap(ext_pixmap)
                        ext_label.setAlignment(Qt.AlignCenter)
                        ext_label.show()
                    
                    self.status_bar.setText(f'正在显示: {os.path.basename(file_path)}')
                    return
                except Exception as e:
                    self.status_bar.setText(f'错误: {str(e)}')
                    self.show_home_screen()
                    return
            else:
                # 如果是单个播放模式且不是图片，先显示首页
                if not self.play_mode and not is_image:
                    self.show_home_screen()
                if not self.play_mode:
                    self.main_player.event_manager().event_attach(
                        vlc.EventType.MediaPlayerEndReached, 
                        self._on_single_play_end
                    )
            
            media = self.instance.media_new(self.playlist[index])
            # 主播放器设置
            self.main_player.stop()
            self.main_player.set_media(media)
            
            # 预览播放器设置（静音且独立）
            self.preview_player.stop()
            self.preview_player.set_media(media)
            self.preview_player.audio_set_mute(True)
            
            # 窗口绑定
            self.main_player.set_hwnd(0)
            self.preview_player.set_hwnd(0)
            
            if self.video_window and self.video_window != self.preview_window:
                # 双屏模式：主输出到扩展屏，预览输出到主界面
                self.main_player.set_hwnd(self.video_window.winId())
                self.preview_player.set_hwnd(self.preview_window.winId())
            else:
                # 单屏模式：主播放器输出到预览窗口
                self.main_player.set_hwnd(self.preview_window.winId())
                self.preview_player.set_hwnd(0)
            
            # 同步启动播放
            self.main_player.play()
            if self.video_window != self.preview_window:
                self.preview_player.play()
            self.fading_in = True
            self.fade_timer.start(self.fade_step_interval)
            self.start_fade_in_animation()
            
            # 更新状态和列表选择
            self.status_bar.setText(f'正在播放: {os.path.basename(self.playlist[index])}')
            self.playlist_widget.setCurrentRow(index)

    def fade_process(self):
        """处理音量渐变过程"""
        if self.fading_in:
            progress = self.fade_timer.remainingTime() / self.fade_duration
            new_volume = int(100 * (1 - progress) ** 3)
            self.set_volume(new_volume)
            if progress <= 0:
                self.fading_in = False
                self.fade_timer.stop()
        elif self.fading_out:
            progress = self.fade_timer.remainingTime() / self.fade_duration
            new_volume = int(100 * progress ** 3)
            self.set_volume(new_volume)
            if progress <= 0:
                self.fading_out = False
                self.fade_timer.stop()
                QTimer.singleShot(200, lambda: [self.main_player.stop(), self.preview_player.stop()])

    def start_fade_in_animation(self):
        """启动淡入动画"""
        self.fade_animation = QPropertyAnimation(self, b"volume")
        self.fade_animation.setDuration(self.fade_duration)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(100)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutCirc)
        self.fade_animation.start()

    def update_preview(self):
        """更新预览画面"""
        if hasattr(self, 'video_window') and self.video_window != self.preview_window:
            if self.main_player.is_playing():
                try:
                    if self.main_player.video_get_size()[0] > 0:
                        temp_file = f"preview_{id(self)}.jpg"
                        if self.main_player.video_take_snapshot(0, temp_file, 0, 0) == 0:
                            retry = 3
                            while retry > 0 and not os.path.exists(temp_file):
                                QApplication.processEvents()
                                retry -= 1
                            
                            if os.path.exists(temp_file):
                                pixmap = QPixmap(temp_file)
                                if not pixmap.isNull():
                                    target_size = QSize(800, 600)
                                    scaled_pixmap = pixmap.scaled(
                                        target_size,
                                        Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation
                                    )
                                    self.preview_window.setPixmap(scaled_pixmap)
                                os.remove(temp_file)
                except Exception as e:
                    print(f"预览更新失败: {str(e)}")
        else:
            grad = QLinearGradient(0, 0, self.preview_window.width(), 0)
            grad.setColorAt(0, QColor(42, 130, 218))
            grad.setColorAt(1, QColor(0, 210, 255))
            
            placeholder = QPixmap(self.preview_window.size())
            placeholder.fill(Qt.transparent)
            painter = QPainter(placeholder)
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(placeholder.rect(), 10, 10)
            painter.setFont(QFont("微软雅黑", 14))
            painter.drawText(placeholder.rect(), Qt.AlignCenter, "主画面播放中")
            painter.end()
            self.preview_window.setPixmap(placeholder)
        
        QTimer.singleShot(500, self.update_preview)

    def set_position(self, position):
        if self.main_player.is_playing():
            self.current_media_position = position / 1000.0
            self.main_player.set_position(self.current_media_position)

    def _ensure_media_loaded(self):
        if not self.main_player.get_media():
            media = self.instance.media_new(self.playlist[self.current_index])
            self.main_player.set_media(media)
            self.preview_player.set_media(media)

    def update_media_status(self):
        """更新媒体状态"""
        if self.main_player.is_playing():
            position = self.main_player.get_position() * 1000
            self.position_slider.setValue(int(position))
            
            if abs(self.preview_player.get_position() - self.main_player.get_position()) > 0.01:
                self.preview_player.set_position(self.main_player.get_position())
            
            if self.mode != "扩展模式" or not hasattr(self, 'ext_screen'):
                self.update_preview()
        else:
            if self.main_player.get_state() == vlc.State.Ended and self.playlist:
                if self.play_mode:
                    self.next_item()
                else:
                    self.stop()
                    self.show_home_screen()

    def toggle_play(self):
        if self.main_player.is_playing():
            self.main_player.pause()
            self.playback_paused = True
            self.status_bar.setText('已暂停')
        else:
            if self.playlist:
                if self.playback_paused:
                    # 恢复播放时保持当前位置
                    self.main_player.set_pause(0)
                    self.playback_paused = False
                else:
                    # 新增播放时保持位置
                    self._ensure_media_loaded()
                self.main_player.play()
                self.status_bar.setText('正在播放')
                #selected = self.playlist_widget.currentRow()
                #self.play_item(selected if selected != -1 else 0)

    def stop(self):
        self.main_player.stop()
        self.preview_player.stop()
        self.current_index = -1
        self.show_home_screen()

    def show_home_screen(self):
        """显示首页画面"""
        self.main_player.stop()
        self.preview_player.stop()
        
        if os.path.exists('index.jpg'):
            pixmap = QPixmap('index.jpg')
            if not pixmap.isNull():
                if len(self.screens) > 1:
                    scaled_pixmap = pixmap.scaled(QSize(800, 600), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    scaled_pixmap = pixmap.scaled(self.preview_window.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_window.setPixmap(scaled_pixmap)
                
                if hasattr(self, 'video_window') and self.video_window != self.preview_window:
                    if len(self.screens) > 1:
                        ext_pixmap = pixmap.scaled(QSize(800, 600), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    else:
                        ext_pixmap = pixmap.scaled(self.video_window.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    if hasattr(self.video_window, 'setPixmap'):
                        self.video_window.setPixmap(ext_pixmap)
                    else:
                        for child in self.video_window.children():
                            if isinstance(child, QLabel):
                                child.setPixmap(ext_pixmap)
                    label = QLabel(self.video_window)
                    label.setPixmap(pixmap.scaled(
                        self.video_window.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    ))
                    label.setAlignment(Qt.AlignCenter)
                    label.show()

    def _hide_taskbar(self):
        """隐藏扩展屏任务栏"""
        try:
            def callback(hwnd, extra):
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                if class_name == "Shell_TrayWnd" and self.ext_screen.x <= rect[0] < self.ext_screen.x + self.ext_screen.width:
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                    
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"隐藏任务栏失败: {str(e)}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        def restore_callback(hwnd, extra):
            if win32gui.GetClassName(hwnd) == "Shell_TrayWnd":
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        
        win32gui.EnumWindows(restore_callback, None)
        
        self.main_player.stop()
        if hasattr(self, 'video_window') and self.video_window != self.preview_window:
            self.video_window.close()
        event.accept()

    def _setup_single_image_playback(self):
        """配置单张图片播放"""
        self.main_player.stop()
        self.preview_player.stop()

    def _on_single_play_end(self, event):
        try:
            self.stop()
            self.show_home_screen()
        finally:
            self.main_player.event_manager().event_detach(
                vlc.EventType.MediaPlayerEndReached
            )

    def prev_item(self):
        """播放上一项"""
        if self.playlist:
            new_index = (self.current_index - 1) % len(self.playlist)
            self.play_item(new_index)

    def next_item(self):
        """播放下一项"""
        if self.playlist:
            new_index = (self.current_index + 1) % len(self.playlist)
            self.play_item(new_index)

    def remove_selected(self):
        """删除选中项"""
        selected = self.playlist_widget.currentRow()
        if selected != -1:
            self.playlist.pop(selected)
            self.playlist_widget.takeItem(selected)
            if not self.playlist:
                self.current_index = -1

    def clear_playlist(self):
        """清空播放列表"""
        self.playlist.clear()
        self.playlist_widget.clear()
        self.current_index = -1

    def save_playlist(self):
        """保存播放列表"""
        file_name, _ = QFileDialog.getSaveFileName(self, "保存播放列表", os.getcwd(), "列表文件 (*.list)")
        if file_name:
            if not file_name.endswith('.list'):
                file_name += '.list'
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(self.playlist, f, ensure_ascii=False)

    def load_playlist(self):
        """加载播放列表"""
        file_name, _ = QFileDialog.getOpenFileName(self, "加载播放列表", os.getcwd(), "列表文件 (*.list)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.playlist = json.load(f)
                    self.playlist_widget.clear()
                    self.playlist_widget.addItems([os.path.basename(f) for f in self.playlist])
                    if self.playlist:
                        self.current_index = 0
            except FileNotFoundError:
                self.status_bar.setText('播放列表文件不存在')

    def get_volume(self):
        return self.main_player.audio_get_volume()
    
    def set_volume(self, volume):
        """设置音量"""
        self.current_volume = volume
        self.main_player.audio_set_volume(volume)

    volume = pyqtProperty(int, get_volume, set_volume)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, '选择媒体文件', '',
            '媒体文件 (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.jpg *.jpeg *.png)')
            
        if files:
            self.playlist.extend(files)
            self.playlist_widget.addItems([os.path.basename(f) for f in files])
            if self.current_index == -1:
                self.current_index = 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = ExtendedScreenPlayer()
    player.show()
    sys.exit(app.exec_())
