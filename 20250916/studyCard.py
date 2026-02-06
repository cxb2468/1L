import sys
import os
import json
import csv
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QFrame, QTabWidget, QMessageBox, QSizePolicy,
    QTimeEdit, QGridLayout, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QSize, QTime
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPainter, QPalette, QIcon


class TimeSlotCard(QFrame):
    """自定义时间段卡片控件"""

    def __init__(self, day, slot_data=None, parent=None):
        super().__init__(parent)
        self.day = day
        self.slot_data = slot_data or {}
        self.timer_running = False
        self.elapsed_time = 0
        self.timer_start_time = 0
        self.init_ui()

    def init_ui(self):
        # 卡片样式
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)

        # 主布局
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setHorizontalSpacing(15)
        main_layout.setVerticalSpacing(10)

        # 时间标签
        time_label = QLabel("时间段:")
        time_label.setFixedWidth(200)
        time_label.setStyleSheet("font-weight: bold; color: #5c9bd1; font-size: 12px;")
        main_layout.addWidget(time_label, 0, 0)

        # 开始时间选择器
        self.start_edit = QTimeEdit()
        self.start_edit.setDisplayFormat("HH:mm")
        self.start_edit.setTime(QTime.fromString(self.slot_data.get("start", "08:00"), "HH:mm"))
        self.start_edit.setFixedHeight(30)
        self.start_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #cce6ff;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.start_edit, 0, 1)

        # 分隔符
        sep_label = QLabel("-")
        sep_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(sep_label, 0, 2)

        # 结束时间选择器
        self.end_edit = QTimeEdit()
        self.end_edit.setDisplayFormat("HH:mm")
        self.end_edit.setTime(QTime.fromString(self.slot_data.get("end", "09:30"), "HH:mm"))
        self.end_edit.setFixedHeight(30)
        self.end_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #cce6ff;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.end_edit, 0, 3)

        # 任务标签
        task_label = QLabel("任务内容:")
        task_label.setStyleSheet("font-weight: bold; color: #5c9bd1; font-size: 12px;")
        main_layout.addWidget(task_label, 1, 0)

        # 任务输入框
        self.task_edit = QLineEdit(self.slot_data.get("task", "学习内容"))
        self.task_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cce6ff;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: #f8fbff;
            }
        """)
        self.task_edit.setFixedHeight(40)
        main_layout.addWidget(self.task_edit, 1, 1, 1, 3)

        # 计时器标签
        timer_label = QLabel("计时:")
        timer_label.setStyleSheet("font-weight: bold; color: #5c9bd1; font-size: 12px;")
        main_layout.addWidget(timer_label, 2, 0)

        # 计时器显示
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                font-family: 'Consolas';
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        main_layout.addWidget(self.timer_label, 2, 1)

        # 计时器按钮
        self.timer_button = QPushButton("开始计时")
        self.timer_button.setFixedHeight(30)
        self.timer_button.setStyleSheet("""
            QPushButton {
                background-color: #5c9bd1;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a8bc2;
            }
            QPushButton:pressed {
                background-color: #3d7bb3;
            }
        """)
        self.timer_button.clicked.connect(self.toggle_timer)
        main_layout.addWidget(self.timer_button, 2, 2)

        # 状态标签
        status_label = QLabel("完成:")
        status_label.setStyleSheet("font-weight: bold; color: #5c9bd1; font-size: 12px;")
        main_layout.addWidget(status_label, 2, 3)

        # 状态按钮
        self.status_button = QPushButton("&#10003;" if self.slot_data.get("completed", False) else "&#10007;")
        self.status_button.setFixedSize(40, 30)
        self.update_status_button_style()
        self.status_button.clicked.connect(self.toggle_status)
        main_layout.addWidget(self.status_button, 2, 4)

        # 删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.setFixedHeight(30)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e57373;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d86262;
            }
            QPushButton:pressed {
                background-color: #c95151;
            }
        """)
        self.delete_button.clicked.connect(self.delete_self)
        main_layout.addWidget(self.delete_button, 2, 5)

        # 初始化计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # 恢复保存的计时器状态
        if "timer" in self.slot_data:
            h, m, s = map(int, self.slot_data["timer"].split(":"))
            self.elapsed_time = h * 3600 + m * 60 + s
            self.update_timer_display()

    def toggle_timer(self):
        """切换计时器状态"""
        if self.timer_running:
            # 停止计时器
            self.timer.stop()
            self.elapsed_time += time.time() - self.timer_start_time
            self.timer_button.setText("开始计时")
            self.timer_button.setStyleSheet("""
                QPushButton {
                    background-color: #5c9bd1;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4a8bc2;
                }
            """)
        else:
            # 开始计时器
            self.timer_start_time = time.time()
            self.timer.start(1000)  # 每秒更新一次
            self.timer_button.setText("停止计时")
            self.timer_button.setStyleSheet("""
                QPushButton {
                    background-color: #e57373;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d86262;
                }
            """)

        self.timer_running = not self.timer_running

    def update_timer(self):
        """更新计时器显示"""
        current_elapsed = self.elapsed_time + (time.time() - self.timer_start_time)
        self.update_timer_display(current_elapsed)

    def update_timer_display(self, elapsed=None):
        """更新计时器显示"""
        if elapsed is None:
            elapsed = self.elapsed_time

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def toggle_status(self):
        """切换完成状态"""
        current_text = self.status_button.text()
        if current_text == "&#10003;":
            self.status_button.setText("&#10007;")
        else:
            self.status_button.setText("&#10003;")
        self.update_status_button_style()

    def update_status_button_style(self):
        """更新状态按钮样式"""
        if self.status_button.text() == "&#10003;":
            self.status_button.setStyleSheet("""
                QPushButton {
                    background-color: #70c470;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #5da85d;
                }
            """)
        else:
            self.status_button.setStyleSheet("""
                QPushButton {
                    background-color: #e57373;
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #d86262;
                }
            """)

    def get_data(self):
        """获取卡片数据"""
        return {
            "start": self.start_edit.time().toString("HH:mm"),
            "end": self.end_edit.time().toString("HH:mm"),
            "task": self.task_edit.text(),
            "completed": self.status_button.text() == "&#10003;",
            "timer": self.timer_label.text()
        }

    def delete_self(self):
        """删除自身"""
        self.setParent(None)
        self.deleteLater()


class GradientHeader(QWidget):
    """渐变标题栏控件"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedHeight(80)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(92, 155, 209))  # #5c9bd1
        gradient.setColorAt(1, QColor(135, 206, 250))  # #87cefa
        painter.fillRect(self.rect(), gradient)

        # 绘制标题
        painter.setPen(Qt.white)
        font = QFont("微软雅黑", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.title)


class IndependentTimer(QFrame):
    """独立计时器控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 220)
        self.setStyleSheet("""
            QFrame {
                background-color: #e6f2ff;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("独立计时器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
            }
        """)
        layout.addWidget(title_label)

        # 计时器显示
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                font-family: 'Consolas';
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #cce6ff;
            }
        """)
        layout.addWidget(self.timer_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 开始按钮
        self.start_button = QPushButton("开始")
        self.start_button.setFixedSize(80, 30)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #5c9bd1;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a8bc2;
            }
        """)
        button_layout.addWidget(self.start_button)

        # 暂停按钮
        self.pause_button = QPushButton("暂停")
        self.pause_button.setFixedSize(80, 30)
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #ffb74d;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffa726;
            }
        """)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        # 重置按钮
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedSize(80, 30)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e57373;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d86262;
            }
        """)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        # 初始化计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # 计时器状态
        self.timer_running = False
        self.elapsed_time = 0
        self.timer_start_time = 0

        # 连接按钮信号
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.reset_button.clicked.connect(self.reset_timer)

    def start_timer(self):
        """启动计时器"""
        if not self.timer_running:
            self.timer_start_time = time.time()
            self.timer.start(1000)
            self.timer_running = True
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.start_button.setText("运行中")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                }
            """)

    def pause_timer(self):
        """暂停计时器"""
        if self.timer_running:
            self.timer.stop()
            self.elapsed_time += time.time() - self.timer_start_time
            self.timer_running = False
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.start_button.setText("继续")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #5c9bd1;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4a8bc2;
                }
            """)

    def reset_timer(self):
        """重置计时器"""
        self.timer.stop()
        self.elapsed_time = 0
        self.timer_running = False
        self.timer_label.setText("00:00:00")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.start_button.setText("开始")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #5c9bd1;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a8bc2;
            }
        """)

    def update_timer(self):
        """更新计时器显示"""
        current_elapsed = self.elapsed_time + (time.time() - self.timer_start_time)
        hours = int(current_elapsed // 3600)
        minutes = int((current_elapsed % 3600) // 60)
        seconds = int(current_elapsed % 60)
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")


class StudyPlannerApp(QMainWindow):
    """学习计划管理应用主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("学习计划自我监控表")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f9ff;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #e6f2ff;
                color: #2c3e50;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #5c9bd1;
                color: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #e6f2ff;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5c9bd1;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                background-color: #d1e0ed;
                border: 1px solid #cce6ff;
                border-radius: 3px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background-color: #b8d4e8;
            }
        """)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 添加渐变标题栏
        header = GradientHeader("学习计划自我监控表")
        main_layout.addWidget(header)

        # 创建中部内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)

        # 创建左侧选项卡区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)

        # 为每一天创建标签页
        self.days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.day_widgets = {}
        self.scroll_areas = {}

        for day in self.days:
            # 创建标签页容器
            tab_container = QWidget()
            tab_container.setStyleSheet("background: transparent;")
            tab_layout = QVBoxLayout(tab_container)
            tab_layout.setContentsMargins(15, 15, 15, 15)
            tab_layout.setSpacing(15)

            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # 创建滚动区域内容
            scroll_content = QWidget()
            scroll_content.setStyleSheet("background: transparent;")
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setAlignment(Qt.AlignTop)
            scroll_layout.setSpacing(15)
            scroll_layout.setContentsMargins(5, 5, 5, 5)

            scroll_area.setWidget(scroll_content)
            tab_layout.addWidget(scroll_area)

            # 添加时间段按钮
            add_button = QPushButton("+ 添加时间段")
            add_button.setFixedHeight(40)
            add_button.setStyleSheet("""
                QPushButton {
                    background-color: #70c470;
                    color: white;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5da85d;
                }
            """)
            add_button.clicked.connect(lambda _, d=day: self.add_time_slot(d))
            tab_layout.addWidget(add_button)

            # 添加到选项卡
            self.tab_widget.addTab(tab_container, day)
            self.day_widgets[day] = scroll_content
            self.scroll_areas[day] = scroll_area

        left_layout.addWidget(self.tab_widget)
        content_layout.addWidget(left_widget, 4)  # 左侧占4份空间

        # 创建右侧独立计时器区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 添加独立计时器
        self.independent_timer = IndependentTimer()
        right_layout.addWidget(self.independent_timer)

        # 添加一些空白空间
        right_layout.addStretch(1)

        content_layout.addWidget(right_widget, 1)  # 右侧占1份空间

        main_layout.addWidget(content_widget, 1)

        # 创建底部按钮区域
        footer = QWidget()
        footer.setFixedHeight(70)
        footer.setStyleSheet("background: white; border-top: 1px solid #e0e0e0;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(15)

        # 保存按钮
        save_button = QPushButton("保存数据")
        save_button.setFixedSize(120, 40)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #5c9bd1;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a8bc2;
            }
        """)
        save_button.clicked.connect(self.save_data)
        footer_layout.addWidget(save_button)

        # 导出按钮
        export_button = QPushButton("导出CSV")
        export_button.setFixedSize(120, 40)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #70c470;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5da85d;
            }
        """)
        export_button.clicked.connect(self.export_data)
        footer_layout.addWidget(export_button)

        footer_layout.addStretch(1)
        main_layout.addWidget(footer)

    def add_time_slot(self, day, slot_data=None):
        """添加新的时间段卡片"""
        card = TimeSlotCard(day, slot_data)
        self.day_widgets[day].layout().addWidget(card)

        # 连接删除按钮信号
        card.delete_button.clicked.connect(lambda: self.delete_time_slot(card, day))

    def delete_time_slot(self, card, day):
        """删除时间段卡片"""
        self.day_widgets[day].layout().removeWidget(card)
        card.deleteLater()

    def save_data(self):
        """保存数据到JSON文件"""
        try:
            save_data = {}
            for day in self.days:
                save_data[day] = []
                layout = self.day_widgets[day].layout()
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, TimeSlotCard):
                        save_data[day].append(widget.get_data())

            # 保存到JSON
            with open("study_planner_data.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "保存成功", "数据已成功保存到study_planner_data.json")
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存数据时出错:\n{str(e)}")

    def load_data(self):
        """加载保存的数据"""
        try:
            if os.path.exists("study_planner_data.json"):
                with open("study_planner_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for day in self.days:
                        if day in data:
                            for slot in data[day]:
                                self.add_time_slot(day, slot)
        except Exception as e:
            print(f"加载数据时出错: {e}")

    def export_data(self):
        """导出数据到CSV文件"""
        try:
            # 准备数据
            csv_data = []
            for day in self.days:
                layout = self.day_widgets[day].layout()
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, TimeSlotCard):
                        slot_data = widget.get_data()
                        csv_data.append({
                            "日期": day,
                            "开始时间": slot_data["start"],
                            "结束时间": slot_data["end"],
                            "学习内容": slot_data["task"],
                            "完成状态": "是" if slot_data["completed"] else "否",
                            "实际学习时间": slot_data["timer"]
                        })

            # 确保目录存在
            os.makedirs("学习记录", exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"学习记录/学习计划_{timestamp}.csv"

            # 写入CSV文件
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ["日期", "开始时间", "结束时间", "学习内容", "完成状态", "实际学习时间"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in csv_data:
                    writer.writerow(row)

            QMessageBox.information(self, "导出成功", f"学习记录已导出到:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出数据时出错:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用全局样式
    app.setStyleSheet("""
        QWidget {
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
        }
    """)

    window = StudyPlannerApp()
    window.show()
    sys.exit(app.exec_())