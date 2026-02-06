import sys
import os
import json
import csv
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                             QComboBox, QProgressBar, QFileDialog,
                             QMessageBox, QTextEdit, QHeaderView,
                             QCheckBox, QDialog, QGroupBox,
                             QFormLayout, QLineEdit,
                             QStatusBar, QToolBar,
                             QTabWidget)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import platform
import datetime

if platform.system() == 'Windows':
    import win32print


class PrintThread(QThread):
    progress_updated = pyqtSignal(int)
    file_status_updated = pyqtSignal(int, str, str)
    log_message = pyqtSignal(str)
    print_completed = pyqtSignal()

    def __init__(self, file_list, selected_indices, printer_name, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.selected_indices = selected_indices
        self.printer_name = printer_name
        self.running = True

    def run(self):
        total_files = len(self.selected_indices)
        processed_files = 0

        for index in self.selected_indices:
            if not self.running:
                break

            file_path = self.file_list[index][0]
            file_name = self.file_list[index][1]

            # 更新状态为"正在打印"
            self.file_status_updated.emit(index, "正在打印", "green")
            self.log_message.emit(f"开始打印文件: {file_name}")

            try:
                result = self.print_file(file_path, self.printer_name)
                if result:
                    status_text = "已打印"
                    status_color = "green"
                    self.log_message.emit(f"文件 {file_name} 打印成功")
                else:
                    status_text = "错误"
                    status_color = "red"
                    self.log_message.emit(f"文件 {file_name} 打印失败")
            except Exception as e:
                status_text = "错误"
                status_color = "red"
                self.log_message.emit(f"打印文件 {file_name} 时出错: {str(e)}")

            # 更新文件状态
            self.file_status_updated.emit(index, status_text, status_color)

            # 更新进度
            processed_files += 1
            progress = int((processed_files / total_files) * 100)
            self.progress_updated.emit(progress)

        if self.running:
            self.log_message.emit("所有选中的文件打印完成")
        else:
            self.log_message.emit("打印任务已取消")

        self.print_completed.emit()

    def print_file(self, file_path, printer_name):
        try:
            if not os.path.exists(file_path):
                self.log_message.emit(f"错误: 文件不存在 - {file_path}")
                return False

            # 检查文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.txt', '.docx', '.xlsx']

            if file_ext not in supported_formats:
                self.log_message.emit(f"错误: 不支持的文件格式 - {file_path}")
                return False

            # 根据不同操作系统使用不同的打印方法
            if platform.system() == 'Windows':
                self.log_message.emit(f"尝试打印 Windows 文件: {file_path}")
                os.startfile(file_path, "print")
                return True
            elif platform.system() == 'Darwin':  # macOS
                cmd = ['lpr', '-P', printer_name, file_path]
                self.log_message.emit(f"尝试打印 macOS 文件: {file_path}, 命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message.emit(f"打印命令失败: {result.stderr}")
                    return False
                return True
            else:  # Linux
                cmd = ['lpr', '-P', printer_name, file_path]
                self.log_message.emit(f"尝试打印 Linux 文件: {file_path}, 命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_message.emit(f"打印命令失败: {result.stderr}")
                    return False
                return True

        except Exception as e:
            self.log_message.emit(f"打印时发生异常: {str(e)}")
            return False

    def stop(self):
        self.running = False
        self.wait()


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.resize(600, 400)

        layout = QVBoxLayout()

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h3>使用说明</h3>
        <ol>
            <li>点击"选择打印文件夹"以选定包含打印文件的目录；</li>
            <li>点击"选择xlsx丨xls文件"并选择文件名所在列；</li>
            <li>文件名将被加载到列表框中，默认去除后缀；</li>
            <li>列表前方单选框用于选择要打印的文件；</li>
            <li>可通过"打印选中"或"打印所有"按钮发起打印；</li>
            <li>打印状态通过颜色区分：
                <ul>
                    <li style="color:yellow;">黄色：等待打印</li>
                    <li style="color:red;">红色：打印失败</li>
                    <li style="color:green;">绿色：打印成功</li>
                </ul>
            </li>
            <li>进度条反映整体打印进度，并显示百分比；</li>
            <li>打印完成或中断后，可查看下方日志信息；</li>
            <li>可在下拉菜单中选择使用的打印机；</li>
            <li>所有设置将自动保存并在下次打开时加载。</li>
        </ol>
        """)

        layout.addWidget(help_text)
        self.setLayout(layout)


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("应用设置")
        self.resize(400, 300)
        self.settings = settings

        layout = QVBoxLayout()

        # 创建选项卡
        tabs = QTabWidget()

        # 常规设置选项卡
        general_tab = QWidget()
        general_layout = QFormLayout()

        self.remember_paths_checkbox = QCheckBox()
        self.remember_paths_checkbox.setChecked(settings.get('remember_paths', True))

        self.auto_load_last_checkbox = QCheckBox()
        self.auto_load_last_checkbox.setChecked(settings.get('auto_load_last', True))

        self.auto_select_printer_checkbox = QCheckBox()
        self.auto_select_printer_checkbox.setChecked(settings.get('auto_select_printer', True))

        self.csv_start_row_edit = QLineEdit()
        self.csv_start_row_edit.setText(str(settings.get('csv_start_row', 2)))

        general_layout.addRow("记住上次使用的路径", self.remember_paths_checkbox)
        general_layout.addRow("自动加载上次的文件", self.auto_load_last_checkbox)
        general_layout.addRow("自动选择上次的打印机", self.auto_select_printer_checkbox)
        general_layout.addRow("CSV/Excel起始读取行", self.csv_start_row_edit)

        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "常规")

        # 文件类型设置选项卡
        file_types_tab = QWidget()
        file_types_layout = QFormLayout()

        self.supported_types_edit = QLineEdit()
        supported_types = settings.get('supported_types', 'pdf,jpg,jpeg,png,bmp,txt,docx,xlsx')
        self.supported_types_edit.setText(supported_types)

        file_types_layout.addRow("支持的文件类型 (逗号分隔)", self.supported_types_edit)
        file_types_tab.setLayout(file_types_layout)
        tabs.addTab(file_types_tab, "文件类型")

        layout.addWidget(tabs)

        # 按钮区域
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_settings(self):
        try:
            csv_start_row = int(self.csv_start_row_edit.text())
        except ValueError:
            csv_start_row = 2
        return {
            'remember_paths': self.remember_paths_checkbox.isChecked(),
            'auto_load_last': self.auto_load_last_checkbox.isChecked(),
            'auto_select_printer': self.auto_select_printer_checkbox.isChecked(),
            'supported_types': self.supported_types_edit.text(),
            'csv_start_row': csv_start_row
        }


class FilePrintManager(QMainWindow):
    def __init__(self):
        super().__init__()

        # 应用设置
        self.settings = {
            'print_folder': '',
            'csv_file': '',
            'csv_column': '',
            'printer_name': '',
            'remember_paths': True,
            'auto_load_last': True,
            'auto_select_printer': True,
            'supported_types': 'pdf,jpg,jpeg,png,bmp,txt,docx,xlsx',
            'csv_start_row': 2
        }

        # 加载保存的设置
        self.load_settings()

        # 存储文件列表 [文件路径, 文件名(无后缀), 状态, 状态颜色, 是否选中]
        self.file_list = []

        # 打印线程
        self.print_thread = None

        # 初始化UI
        self.init_ui()

        # 加载上次的设置（如果启用）
        if self.settings['auto_load_last']:
            self.load_last_files()

        # 启用拖拽功能
        self.setAcceptDrops(True)

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("TOMILO_文件打印管理器V1.0")
        self.resize(1000, 600)

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧面板 - 文件列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 顶部按钮区
        top_button_layout = QHBoxLayout()

        self.select_folder_button = QPushButton("选择打印文件夹")
        self.select_folder_button.clicked.connect(self.select_print_folder)

        self.select_csv_button = QPushButton("选择XLSX或XLS文件")
        self.select_csv_button.clicked.connect(self.select_csv_file)

        self.save_config_button = QPushButton("保存配置")
        self.save_config_button.clicked.connect(self.save_config)

        self.settings_button = QPushButton("设置")
        self.settings_button.clicked.connect(self.open_settings)

        self.export_log_button = QPushButton("导出日志")
        self.export_log_button.clicked.connect(self.export_log)

        self.clear_file_list_button = QPushButton("清空文件列表")
        self.clear_file_list_button.clicked.connect(self.clear_file_list)

        top_button_layout.addWidget(self.select_folder_button)
        top_button_layout.addWidget(self.select_csv_button)
        top_button_layout.addWidget(self.save_config_button)
        top_button_layout.addWidget(self.settings_button)
        top_button_layout.addWidget(self.export_log_button)
        top_button_layout.addWidget(self.clear_file_list_button)

        left_layout.addLayout(top_button_layout)

        # 文件列表表格
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["选择", "文件名", "状态"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.doubleClicked.connect(self.preview_selected_file)

        left_layout.addWidget(self.file_table)

        # 底部按钮区
        bottom_button_layout = QHBoxLayout()

        self.print_selected_button = QPushButton("打印选中")
        self.print_selected_button.clicked.connect(self.print_selected_files)

        self.print_all_button = QPushButton("打印所有")
        self.print_all_button.clicked.connect(self.print_all_files)

        self.cancel_print_button = QPushButton("取消打印")
        self.cancel_print_button.clicked.connect(self.cancel_print)
        self.cancel_print_button.setEnabled(False)

        bottom_button_layout.addWidget(self.print_selected_button)
        bottom_button_layout.addWidget(self.print_all_button)
        bottom_button_layout.addWidget(self.cancel_print_button)

        left_layout.addLayout(bottom_button_layout)

        # 右侧面板 - 打印选项和日志
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 打印机选择
        printer_group = QGroupBox("打印机选择【选择会将系统默认打印机改为所选打印机】")
        printer_layout = QVBoxLayout()

        self.printer_combo = QComboBox()
        self.printer_combo.currentIndexChanged.connect(self.set_default_printer)  # 新增连接信号

        self.refresh_printer_button = QPushButton("刷新打印机列表")
        self.refresh_printer_button.clicked.connect(self.refresh_printers)

        printer_layout.addWidget(self.printer_combo)
        printer_layout.addWidget(self.refresh_printer_button)
        printer_group.setLayout(printer_layout)

        right_layout.addWidget(printer_group)

        # CSV列选择
        csv_group = QGroupBox("XLSX、XLS文件列选择（文件名展现打印的循序）")
        csv_layout = QVBoxLayout()

        self.csv_column_combo = QComboBox()
        self.csv_column_combo.currentIndexChanged.connect(self.update_file_list)

        self.update_csv_columns_button = QPushButton("更新列列表")
        self.update_csv_columns_button.clicked.connect(self.update_csv_columns)

        csv_layout.addWidget(self.csv_column_combo)
        csv_layout.addWidget(self.update_csv_columns_button)
        csv_group.setLayout(csv_layout)

        right_layout.addWidget(csv_group)

        # 日志区域
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)

        right_layout.addWidget(log_group)

        # 添加到主布局
        main_layout.addWidget(left_panel, 7)  # 70% 宽度
        main_layout.addWidget(right_panel, 3)  # 30% 宽度

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().addPermanentWidget(self.progress_bar, 1)

        # 菜单栏
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        select_folder_action = QAction("选择打印文件夹", self)
        select_folder_action.triggered.connect(self.select_print_folder)
        file_menu.addAction(select_folder_action)

        select_csv_action = QAction("选择XLSX或XLS文件", self)
        select_csv_action.triggered.connect(self.select_csv_file)
        file_menu.addAction(select_csv_action)

        file_menu.addSeparator()

        save_config_action = QAction("保存配置", self)
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)

        export_log_action = QAction("导出日志", self)
        export_log_action.triggered.connect(self.export_log)
        file_menu.addAction(export_log_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 打印菜单
        print_menu = menubar.addMenu("打印")

        print_selected_action = QAction("打印选中", self)
        print_selected_action.triggered.connect(self.print_selected_files)
        print_menu.addAction(print_selected_action)

        print_all_action = QAction("打印所有", self)
        print_all_action.triggered.connect(self.print_all_files)
        print_menu.addAction(print_all_action)

        print_menu.addSeparator()

        cancel_print_action = QAction("取消打印", self)
        cancel_print_action.triggered.connect(self.cancel_print)
        print_menu.addAction(cancel_print_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        help_action = QAction("使用说明", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 工具栏
        toolbar = QToolBar("工具栏")
        self.addToolBar(toolbar)

        toolbar.addAction(select_folder_action)
        toolbar.addAction(select_csv_action)
        toolbar.addSeparator()
        toolbar.addAction(print_selected_action)
        toolbar.addAction(print_all_action)
        toolbar.addAction(cancel_print_action)
        toolbar.addSeparator()
        toolbar.addAction(help_action)

        # 连接信号和槽
        self.file_table.cellChanged.connect(self.on_cell_changed)

        # 移动刷新打印机列表的调用到日志区域初始化之后
        self.refresh_printers()

    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if os.path.exists('print_manager_settings.json'):
                with open('print_manager_settings.json', 'r') as f:
                    self.settings = json.load(f)
        except Exception as e:
            self.log(f"加载设置时出错: {str(e)}")

    def save_settings(self):
        """保存设置到配置文件"""
        try:
            with open('print_manager_settings.json', 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            self.log(f"保存设置时出错: {str(e)}")

    def select_print_folder(self):
        """选择打印文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择打印文件夹",
                                                  self.settings['print_folder'] if self.settings[
                                                      'print_folder'] else "")
        if folder:
            self.settings['print_folder'] = folder
            self.log(f"已选择打印文件夹: {folder}")
            self.update_file_list()

    def select_csv_file(self):
        """选择CSV、XLSX或XLS文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                   self.settings['csv_file'] if self.settings['csv_file'] else "",
                                                   "Excel文件 (*.xlsx *.xls);;所有文件 (*)")
        if file_path:
            self.settings['csv_file'] = file_path
            self.log(f"已选择文件: {file_path}")
            self.update_csv_columns()
            self.update_file_list()

    def update_csv_columns(self):
        """更新CSV列列表"""
        if not self.settings['csv_file'] or not os.path.exists(self.settings['csv_file']):
            self.log("请先选择有效的文件")
            return

        try:
            self.csv_column_combo.clear()

            file_ext = os.path.splitext(self.settings['csv_file'])[1].lower()
            if file_ext == '.csv':
                # 读取 CSV 文件
                with open(self.settings['csv_file'], 'r', encoding='ansi') as f:
                    reader = csv.reader(f)
                    for _ in range(self.settings['csv_start_row'] - 1):
                        next(reader)
                    headers = next(reader)
            elif file_ext in ['.xlsx', '.xls']:
                # 读取 Excel 文件
                df = pd.read_excel(self.settings['csv_file'], header=self.settings['csv_start_row'] - 1)
                headers = df.columns.tolist()
            else:
                self.log("不支持的文件格式")
                return

            if not headers:
                self.log("文件没有标题行")
                return

            for header in headers:
                self.csv_column_combo.addItem(header)

            # 选择上次使用的列（如果存在）
            if self.settings['csv_column'] and self.settings['csv_column'] in headers:
                index = headers.index(self.settings['csv_column'])
                self.csv_column_combo.setCurrentIndex(index)

            self.update_file_list()
        except Exception as e:
            self.log(f"读取文件时出错: {str(e)}")

    def update_file_list(self):
        """更新文件列表"""
        if not self.settings['print_folder'] or not os.path.exists(self.settings['print_folder']):
            self.log("请先选择有效的打印文件夹")
            return

        if not self.settings['csv_file'] or not os.path.exists(self.settings['csv_file']):
            self.log("请先选择有效的文件")
            return

        if self.csv_column_combo.count() == 0:
            self.log("请先更新列列表")
            return

        selected_column = self.csv_column_combo.currentText()
        self.settings['csv_column'] = selected_column

        # 清空表格
        self.file_table.setRowCount(0)
        self.file_list = []

        try:
            # 获取支持的文件类型
            supported_extensions = [f".{ext.strip().lower()}" for ext in self.settings['supported_types'].split(',')]

            file_ext = os.path.splitext(self.settings['csv_file'])[1].lower()
            if file_ext == '.csv':
                # 读取 CSV 文件
                with open(self.settings['csv_file'], 'r', encoding='ansi') as f:
                    reader = csv.DictReader(f, fieldnames=None, restkey=None, restval=None, dialect='excel')
                    for _ in range(self.settings['csv_start_row'] - 1):
                        next(reader)
                    headers = next(reader)
                    reader = csv.DictReader(f, fieldnames=headers, restkey=None, restval=None, dialect='excel')
            elif file_ext in ['.xlsx', '.xls']:
                # 读取 Excel 文件
                df = pd.read_excel(self.settings['csv_file'], header=self.settings['csv_start_row'] - 1)
                reader = df.to_dict('records')
            else:
                self.log("不支持的文件格式")
                return

            if selected_column not in next(iter(reader)):
                self.log(f"文件中找不到列: {selected_column}")
                return

            row_count = 0
            for row in reader:
                file_name = row.get(selected_column, "").strip()
                if not file_name:
                    continue

                # 尝试查找匹配的文件（不考虑扩展名）
                file_found = False
                file_path = ""

                # 检查是否已有扩展名
                if '.' in file_name and os.path.splitext(file_name)[1].lower() in supported_extensions:
                    file_path = os.path.join(self.settings['print_folder'], file_name)
                    if os.path.exists(file_path):
                        file_found = True
                else:
                    # 尝试匹配所有支持的扩展名
                    for ext in supported_extensions:
                        possible_path = os.path.join(self.settings['print_folder'], f"{file_name}{ext}")
                        if os.path.exists(possible_path):
                            file_path = possible_path
                            file_found = True
                            break

                # 去除扩展名以显示
                display_name = os.path.splitext(file_name)[0]

                # 添加到文件列表
                status = "已找到" if file_found else "文件缺失"
                color = "green" if file_found else "red"

                self.file_list.append([file_path, display_name, status, color, False])

                # 添加到表格
                self.file_table.insertRow(row_count)

                # 选择框
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                self.file_table.setItem(row_count, 0, checkbox_item)

                # 文件名
                name_item = QTableWidgetItem(display_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.file_table.setItem(row_count, 1, name_item)

                # 状态
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                status_item.setForeground(QColor(color))
                self.file_table.setItem(row_count, 2, status_item)

                row_count += 1

            self.log(f"已加载 {len(self.file_list)} 个文件")
        except Exception as e:
            self.log(f"更新文件列表时出错: {str(e)}")

    def print_selected_files(self):
        """打印选中的文件"""
        selected_indices = []
        for i in range(self.file_table.rowCount()):
            if self.file_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                selected_indices.append(i)

        if not selected_indices:
            self.log("请选择要打印的文件")
            return

        printer_name = self.printer_combo.currentText()
        if not printer_name:
            self.log("请选择打印机")
            return

        self.print_thread = PrintThread(self.file_list, selected_indices, printer_name)
        self.print_thread.progress_updated.connect(self.update_progress_bar)
        self.print_thread.file_status_updated.connect(self.update_file_status)
        self.print_thread.log_message.connect(self.log)
        self.print_thread.print_completed.connect(self.print_completed)
        self.print_thread.start()

        self.print_selected_button.setEnabled(False)
        self.print_all_button.setEnabled(False)
        self.cancel_print_button.setEnabled(True)

    def print_all_files(self):
        """打印所有文件"""
        selected_indices = list(range(len(self.file_list)))

        if not selected_indices:
            self.log("没有可打印的文件")
            return

        printer_name = self.printer_combo.currentText()
        if not printer_name:
            self.log("请选择打印机")
            return

        self.print_thread = PrintThread(self.file_list, selected_indices, printer_name)
        self.print_thread.progress_updated.connect(self.update_progress_bar)
        self.print_thread.file_status_updated.connect(self.update_file_status)
        self.print_thread.log_message.connect(self.log)
        self.print_thread.print_completed.connect(self.print_completed)
        self.print_thread.start()

        self.print_selected_button.setEnabled(False)
        self.print_all_button.setEnabled(False)
        self.cancel_print_button.setEnabled(True)

    def cancel_print(self):
        """取消打印任务"""
        if self.print_thread:
            self.print_thread.stop()
            self.print_thread = None

        self.print_selected_button.setEnabled(True)
        self.print_all_button.setEnabled(True)
        self.cancel_print_button.setEnabled(False)

    def update_progress_bar(self, progress):
        """更新进度条"""
        self.progress_bar.setValue(progress)

    def update_file_status(self, index, status_text, status_color):
        """更新文件状态"""
        status_item = self.file_table.item(index, 2)
        status_item.setText(status_text)
        status_item.setForeground(QColor(status_color))

    def print_completed(self):
        """打印完成处理"""
        self.print_selected_button.setEnabled(True)
        self.print_all_button.setEnabled(True)
        self.cancel_print_button.setEnabled(False)

    def log(self, message):
        """记录日志"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{now}] {message}")

    def save_config(self):
        """保存配置"""
        self.save_settings()
        self.log("配置已保存")

    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.save_settings()
            self.log("设置已保存")
            self.update_file_list()

    def export_log(self):
        """导出日志"""
        file_path, _ = QFileDialog.getSaveFileName(self, "导出日志", "", "文本文件 (*.txt);;所有文件 (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.log(f"日志已导出到 {file_path}")
            except Exception as e:
                self.log(f"导出日志时出错: {str(e)}")

    def clear_file_list(self):
        """清空文件列表"""
        self.file_table.setRowCount(0)
        self.file_list = []
        self.log("文件列表已清空")

    def preview_selected_file(self, index):
        """预览选中的文件"""
        file_path = self.file_list[index.row()][0]
        if file_path and os.path.exists(file_path):
            try:
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', file_path])
                else:
                    subprocess.run(['xdg-open', file_path])
            except Exception as e:
                self.log(f"预览文件时出错: {str(e)}")

    def refresh_printers(self):
        """刷新打印机列表"""
        self.printer_combo.clear()
        if platform.system() == 'Windows':
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            for printer in printers:
                printer_name = printer[2]
                self.printer_combo.addItem(printer_name)
                if printer_name == self.settings['printer_name']:
                    self.printer_combo.setCurrentIndex(self.printer_combo.count() - 1)
        else:
            try:
                result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
                lines = result.stdout.splitlines()
                for line in lines:
                    if line.startswith('printer '):
                        printer_name = line.split(' ')[1]
                        self.printer_combo.addItem(printer_name)
                        if printer_name == self.settings['printer_name']:
                            self.printer_combo.setCurrentIndex(self.printer_combo.count() - 1)
            except Exception as e:
                self.log(f"刷新打印机列表时出错: {str(e)}")

    def set_default_printer(self, index):
        """设置默认打印机"""
        printer_name = self.printer_combo.currentText()
        self.settings['printer_name'] = printer_name
        self.save_settings()

        if platform.system() == 'Windows':
            try:
                win32print.SetDefaultPrinter(printer_name)
                self.log(f"已将默认打印机设置为: {printer_name}")
            except Exception as e:
                self.log(f"设置默认打印机时出错: {str(e)}")
        else:
            try:
                subprocess.run(['lpoptions', '-d', printer_name])
                self.log(f"已将默认打印机设置为: {printer_name}")
            except Exception as e:
                self.log(f"设置默认打印机时出错: {str(e)}")

    def show_help(self):
        """显示帮助对话框"""
        dialog = HelpDialog(self)
        dialog.exec()

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "TOMILO_文件打印管理器V1.0\nBy：")

    def load_last_files(self):
        """加载上次的文件和设置"""
        if self.settings['remember_paths']:
            if self.settings['print_folder'] and os.path.exists(self.settings['print_folder']):
                self.log(f"自动加载打印文件夹: {self.settings['print_folder']}")
                self.update_file_list()
            if self.settings['csv_file'] and os.path.exists(self.settings['csv_file']):
                self.log(f"自动加载CSV文件: {self.settings['csv_file']}")
                self.update_csv_columns()
            if self.settings['auto_select_printer'] and self.settings['printer_name']:
                index = self.printer_combo.findText(self.settings['printer_name'])
                if index != -1:
                    self.printer_combo.setCurrentIndex(index)

    def on_cell_changed(self, row, column):
        """处理表格单元格变化事件"""
        if column == 0:
            is_checked = self.file_table.item(row, 0).checkState() == Qt.CheckState.Checked
            self.file_list[row][4] = is_checked


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FilePrintManager()
    window.show()
    sys.exit(app.exec())