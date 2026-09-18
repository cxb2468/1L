import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QDialog, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QListWidget, QStackedWidget, QTableWidget, QTableWidgetItem,
                             QTabWidget, QMessageBox, QAbstractItemView, QHeaderView,
                             QFormLayout, QFrame, QComboBox, QToolButton)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QLinearGradient, QBrush


# ======================
# 登录对话框
# ======================
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统登录")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            background-color: #f5f7fa;
            font-family: 'Microsoft YaHei';
        """)

        # 创建渐变背景
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor("#4facfe"))
        gradient.setColorAt(1, QColor("#00f2fe"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # 标题
        title = QLabel("欢迎来到个人信息管理系统")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: red;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)

        # 输入框容器
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 20px;
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(20)

        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #4facfe;
            }
        """)

        # 密码输入
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())

        # 登录按钮
        login_btn = QPushButton("登 录")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8bce;
            }
        """)
        login_btn.clicked.connect(self.check_credentials)

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_btn)

        layout.addWidget(title)
        layout.addWidget(form_frame)
        self.setLayout(layout)

    def check_credentials(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # 简单验证（实际应用中应使用数据库验证）
        if username == "admin" and password == "password":
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")


# ======================
# 主界面
# ======================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据管理系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            background-color: #f5f7fa;
            font-family: 'Microsoft YaHei';
        """)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧导航栏 (1/12宽度)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(int(self.width() / 7))
        self.sidebar.setStyleSheet("""
            background-color: #2c3e50;
            border-right: 1px solid #34495e;
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)

        # 导航按钮
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                color: #ecf0f1;
                font-size: 16px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-left: 4px solid transparent;
            }
            QListWidget::item:selected {
                background-color: #34495e;
                border-left: 4px solid #3498db;
            }
        """)
        self.nav_list.setFrameShape(QListWidget.NoFrame)
        self.nav_list.setFixedSize(300, 800)
        item_height = 80  # 400 / 10 = 40px
        self.nav_list.setGridSize(QSize(0, item_height))  # 宽度自适应，高度固定

        # 固定导航栏总高度
        self.nav_list.setFixedHeight(10 * item_height)
        self.nav_list.addItems([
            "账号密码管理",
            "随礼记录",
            "栏目三",
            "栏目四",
            "栏目五",
            "栏目六",
            "栏目七",
            "栏目八",
            "栏目九",
            "栏目十"
        ])
        self.nav_list.currentRowChanged.connect(self.switch_page)

        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()

        # 右侧堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            background-color: white;
            border-radius: 0;
        """)

        # 添加各个页面
        self.account_page = AccountPasswordPage()
        self.gift_page = GiftRecordPage()

        self.stacked_widget.addWidget(self.account_page)
        self.stacked_widget.addWidget(self.gift_page)

        # 添加8个占位页面
        for i in range(8):
            placeholder = QWidget()
            placeholder.setStyleSheet("background-color: white;")
            layout = QVBoxLayout(placeholder)
            label = QLabel(f"栏目 {i + 3} 开发中...")
            label.setStyleSheet("font-size: 24px; color: #7f8c8d;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self.stacked_widget.addWidget(placeholder)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.setCentralWidget(main_widget)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def load_data(self):
        # 尝试加载账号数据
        try:
            self.account_page.load_account_data()
        except Exception as e:
            QMessageBox.warning(self, "数据加载错误", f"账号数据加载失败: {str(e)}")

        # 尝试加载随礼数据
        try:
            self.gift_page.load_gift_data()
        except Exception as e:
            QMessageBox.warning(self, "数据加载错误", f"随礼数据加载失败: {str(e)}")


# ======================
# 账号密码管理页面
# ======================
class AccountPasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.account_data = {
            'int_info_account': pd.DataFrame(columns=['id', '名称', '网址', '账号', '密码', '备注']),
            'personal_account': pd.DataFrame(columns=['id', '名称', '网址', '账号', '密码', '备注'])
        }
        self.current_table = 'int_info_account'
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 标题
        title = QLabel("账号密码管理")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)

        # 选项卡
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-bottom: none;
                padding: 10px 20px;
                font-size: 14px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #3498db;
                color: #3498db;
                font-weight: bold;
            }
        """)

        # 创建两个选项卡
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "  单位账号  ")
        self.tabs.addTab(self.tab2, "  个人账号  ")
        self.tabs.currentChanged.connect(self.tab_changed)

        # 初始化选项卡内容
        self.init_tab(self.tab1, 'int_info_account')
        self.init_tab(self.tab2, 'personal_account')

        main_layout.addWidget(title)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_tab(self, tab, table_name):
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 操作栏
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)

        # 添加按钮
        add_btn = QPushButton("添加账号")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_account(table_name))

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索名称、账号或备注...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)

        action_layout.addWidget(add_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.search_input)

        # 表格
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID', '名称', '网址', '账号', '密码', '备注'])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #d6eaf8;
                color: black;
            }
        """)

        if table_name == 'int_info_account':
            self.table1 = table
        else:
            self.table2 = table

        # 按钮组
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        # 查看密码按钮
        view_pwd_btn = QPushButton("查看密码")
        view_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        view_pwd_btn.clicked.connect(lambda: self.view_password(table_name))

        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_account(table_name))

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_account(table_name))

        btn_layout.addWidget(view_pwd_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        layout.addWidget(action_bar)
        layout.addWidget(table)
        layout.addWidget(btn_group)

    def tab_changed(self, index):
        self.current_table = 'int_info_account' if index == 0 else 'personal_account'

    def load_account_data(self):
        # 尝试从Excel文件加载数据
        try:
            # 内部信息账号
            df1 = pd.read_excel('账号密码.xls', sheet_name='int_info_account')
            if not df1.empty:
                self.account_data['int_info_account'] = df1
                self.populate_table(self.table1, df1)

            # 个人账号
            df2 = pd.read_excel('账号密码.xls', sheet_name='personal_account')
            if not df2.empty:
                self.account_data['personal_account'] = df2
                self.populate_table(self.table2, df2)
        except:
            # 如果文件不存在，创建空的DataFrame
            self.account_data = {
                'int_info_account': pd.DataFrame(columns=['id', '名称', '网址', '账号', '密码', '备注']),
                'personal_account': pd.DataFrame(columns=['id', '名称', '网址', '账号', '密码', '备注'])
            }

    def populate_table(self, table, df):
        table.setRowCount(len(df))

        for row_idx, row in df.iterrows():
            for col_idx, col in enumerate(['id', '名称', '网址', '账号', '密码', '备注']):
                item = QTableWidgetItem(str(row[col]) if pd.notna(row[col]) else "")
                table.setItem(row_idx, col_idx, item)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        table = self.table1 if self.current_table == 'int_info_account' else self.table2
        df = self.account_data[self.current_table]

        if search_text:
            filtered_df = df[
                df['名称'].str.lower().str.contains(search_text) |
                df['账号'].str.lower().str.contains(search_text) |
                df['备注'].str.lower().str.contains(search_text)
                ]
        else:
            filtered_df = df

        self.populate_table(table, filtered_df)

    def add_account(self, table_name):
        dialog = AccountDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 获取表单数据
            new_data = dialog.get_data()

            # 获取当前表数据
            df = self.account_data[table_name]

            # 生成新ID
            new_id = df['id'].max() + 1 if not df.empty else 1

            # 添加新行
            new_row = {
                'id': new_id,
                '名称': new_data['name'],
                '网址': new_data['url'],
                '账号': new_data['username'],
                '密码': new_data['password'],
                '备注': new_data['notes']
            }

            # 更新数据
            self.account_data[table_name] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # 更新表格
            table = self.table1 if table_name == 'int_info_account' else self.table2
            self.populate_table(table, self.account_data[table_name])

            # 保存到Excel
            self.save_account_data()

    def view_password(self, table_name):
        table = self.table1 if table_name == 'int_info_account' else self.table2
        selected_row = table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "操作失败", "请先选择一个账号")
            return

        # 获取密码
        password = table.item(selected_row, 4).text()

        # 显示密码
        QMessageBox.information(self, "密码信息", f"账号密码为: {password}")

    def edit_account(self, table_name):
        table = self.table1 if table_name == 'int_info_account' else self.table2
        selected_row = table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "操作失败", "请先选择一个账号")
            return

        # 获取当前行数据
        account_id = int(table.item(selected_row, 0).text())
        name = table.item(selected_row, 1).text()
        url = table.item(selected_row, 2).text()
        username = table.item(selected_row, 3).text()
        password = table.item(selected_row, 4).text()
        notes = table.item(selected_row, 5).text()

        # 打开编辑对话框
        dialog = AccountDialog(edit_mode=True)
        dialog.set_data({
            'name': name,
            'url': url,
            'username': username,
            'password': password,
            'notes': notes
        })

        if dialog.exec_() == QDialog.Accepted:
            # 获取更新后的数据
            updated_data = dialog.get_data()

            # 更新数据
            df = self.account_data[table_name]
            idx = df[df['id'] == account_id].index[0]

            df.at[idx, '名称'] = updated_data['name']
            df.at[idx, '网址'] = updated_data['url']
            df.at[idx, '账号'] = updated_data['username']
            df.at[idx, '密码'] = updated_data['password']
            df.at[idx, '备注'] = updated_data['notes']

            # 更新表格
            self.populate_table(table, df)

            # 保存到Excel
            self.save_account_data()

    def delete_account(self, table_name):
        table = self.table1 if table_name == 'int_info_account' else self.table2
        selected_row = table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "操作失败", "请先选择一个账号")
            return

        # 确认删除
        account_name = table.item(selected_row, 1).text()
        reply = QMessageBox.question(
            self, '确认删除',
            f"确定要删除账号 '{account_name}' 吗?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 获取ID
            account_id = int(table.item(selected_row, 0).text())

            # 从数据中删除
            df = self.account_data[table_name]
            self.account_data[table_name] = df[df['id'] != account_id]

            # 更新表格
            self.populate_table(table, self.account_data[table_name])

            # 保存到Excel
            self.save_account_data()

    def save_account_data(self):
        try:
            with pd.ExcelWriter('账号密码.xls') as writer:
                self.account_data['int_info_account'].to_excel(writer, sheet_name='int_info_account', index=False)
                self.account_data['personal_account'].to_excel(writer, sheet_name='personal_account', index=False)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"数据保存失败: {str(e)}")


# ======================
# 账号对话框
# ======================
class AccountDialog(QDialog):
    def __init__(self, edit_mode=False):
        super().__init__()
        self.setWindowTitle("添加账号" if not edit_mode else "编辑账号")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Microsoft YaHei';
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # 标题
        title = QLabel(self.windowTitle())
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 1px solid #3498db;
        """)
        title.setAlignment(Qt.AlignCenter)

        # 表单
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # 名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("必填")
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)

        # 网址
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("例如: https://example.com")
        self.url_input.setStyleSheet(self.name_input.styleSheet())

        # 账号
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(self.name_input.styleSheet())

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.name_input.styleSheet())

        # 显示密码按钮
        self.toggle_pwd_btn = QToolButton()
        self.toggle_pwd_btn.setIcon(QIcon.fromTheme("view-hidden"))
        self.toggle_pwd_btn.setCheckable(True)
        self.toggle_pwd_btn.setStyleSheet("""
            QToolButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.toggle_pwd_btn.toggled.connect(self.toggle_password_visibility)

        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.password_input)
        pwd_layout.addWidget(self.toggle_pwd_btn)

        # 备注
        self.notes_input = QLineEdit()
        self.notes_input.setStyleSheet(self.name_input.styleSheet())

        # 添加表单行
        form_layout.addRow("名称:", self.name_input)
        form_layout.addRow("网址:", self.url_input)
        form_layout.addRow("账号:", self.username_input)
        form_layout.addRow("密码:", pwd_layout)
        form_layout.addRow("备注:", self.notes_input)

        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        save_btn.clicked.connect(self.validate_and_accept)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(title)
        layout.addWidget(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pwd_btn.setIcon(QIcon.fromTheme("view-visible"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pwd_btn.setIcon(QIcon.fromTheme("view-hidden"))

    def set_data(self, data):
        self.name_input.setText(data['name'])
        self.url_input.setText(data['url'])
        self.username_input.setText(data['username'])
        self.password_input.setText(data['password'])
        self.notes_input.setText(data['notes'])

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'notes': self.notes_input.text().strip()
        }

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "输入错误", "名称不能为空")
            self.name_input.setFocus()
            return

        self.accept()


# ======================
# 随礼记录页面
# ======================
class GiftRecordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.gift_data = pd.DataFrame(columns=['序号', '姓名', '事由', '金额'])
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 标题
        title = QLabel("随礼记录管理")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 2px solid #9b59b6;
        """)

        # 操作栏
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)

        # 添加按钮
        add_btn = QPushButton("添加记录")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        add_btn.clicked.connect(self.add_gift_record)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索姓名或事由...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #9b59b6;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)

        # 统计标签
        self.sum_label = QLabel("总金额: 0元")
        self.sum_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #9b59b6;
            padding: 8px 12px;
        """)

        action_layout.addWidget(add_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.search_input)
        action_layout.addSpacing(15)
        action_layout.addWidget(self.sum_label)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['序号', '姓名', '事由', '金额'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #eee;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #e8d5f0;
                color: black;
            }
        """)

        # 按钮组
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        edit_btn.clicked.connect(self.edit_gift_record)

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(self.delete_gift_record)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(action_bar)
        main_layout.addWidget(self.table)
        main_layout.addWidget(btn_group)
        self.setLayout(main_layout)

    def load_gift_data(self):
        # 尝试从Excel文件加载数据
        try:
            df = pd.read_excel('随礼记录.xls')
            if not df.empty:
                self.gift_data = df
                self.populate_table()
        except:
            # 如果文件不存在，创建空的DataFrame
            self.gift_data = pd.DataFrame(columns=['序号', '姓名', '事由', '金额'])

    def populate_table(self):
        self.table.setRowCount(len(self.gift_data))

        for row_idx, row in self.gift_data.iterrows():
            for col_idx, col in enumerate(['序号', '姓名', '事由', '金额']):
                item = QTableWidgetItem(str(row[col]) if pd.notna(row[col]) else "")
                self.table.setItem(row_idx, col_idx, item)

        # 更新总金额
        total = self.gift_data['金额'].sum()
        self.sum_label.setText(f"总金额: {total}元")

    def filter_table(self):
        search_text = self.search_input.text().lower()

        if search_text:
            filtered_df = self.gift_data[
                self.gift_data['姓名'].str.lower().str.contains(search_text) |
                self.gift_data['事由'].str.lower().str.contains(search_text)
                ]
        else:
            filtered_df = self.gift_data

        self.table.setRowCount(len(filtered_df))

        for row_idx, row in filtered_df.iterrows():
            for col_idx, col in enumerate(['序号', '姓名', '事由', '金额']):
                item = QTableWidgetItem(str(row[col]) if pd.notna(row[col]) else "")
                self.table.setItem(row_idx, col_idx, item)

        # 更新总金额
        total = filtered_df['金额'].sum()
        self.sum_label.setText(f"总金额: {total}元")

    def add_gift_record(self):
        dialog = GiftDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 获取表单数据
            new_data = dialog.get_data()

            # 生成新ID
            new_id = self.gift_data['序号'].max() + 1 if not self.gift_data.empty else 1

            # 添加新行
            new_row = {
                '序号': new_id,
                '姓名': new_data['name'],
                '事由': new_data['reason'],
                '金额': new_data['amount']
            }

            # 更新数据
            self.gift_data = pd.concat([self.gift_data, pd.DataFrame([new_row])], ignore_index=True)

            # 更新表格
            self.populate_table()

            # 保存到Excel
            self.save_gift_data()

    def edit_gift_record(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "操作失败", "请先选择一个记录")
            return

        # 获取当前行数据
        record_id = int(self.table.item(selected_row, 0).text())
        name = self.table.item(selected_row, 1).text()
        reason = self.table.item(selected_row, 2).text()
        amount = float(self.table.item(selected_row, 3).text())

        # 打开编辑对话框
        dialog = GiftDialog(edit_mode=True)
        dialog.set_data({
            'name': name,
            'reason': reason,
            'amount': amount
        })

        if dialog.exec_() == QDialog.Accepted:
            # 获取更新后的数据
            updated_data = dialog.get_data()

            # 更新数据
            idx = self.gift_data[self.gift_data['序号'] == record_id].index[0]

            self.gift_data.at[idx, '姓名'] = updated_data['name']
            self.gift_data.at[idx, '事由'] = updated_data['reason']
            self.gift_data.at[idx, '金额'] = updated_data['amount']

            # 更新表格
            self.populate_table()

            # 保存到Excel
            self.save_gift_data()

    def delete_gift_record(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "操作失败", "请先选择一个记录")
            return

        # 确认删除
        person_name = self.table.item(selected_row, 1).text()
        reply = QMessageBox.question(
            self, '确认删除',
            f"确定要删除 '{person_name}' 的随礼记录吗?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 获取ID
            record_id = int(self.table.item(selected_row, 0).text())

            # 从数据中删除
            self.gift_data = self.gift_data[self.gift_data['序号'] != record_id]

            # 更新表格
            self.populate_table()

            # 保存到Excel
            self.save_gift_data()

    def save_gift_data(self):
        try:
            self.gift_data.to_excel('随礼记录.xls', index=False)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"数据保存失败: {str(e)}")


# ======================
# 随礼对话框
# ======================
class GiftDialog(QDialog):
    def __init__(self, edit_mode=False):
        super().__init__()
        self.setWindowTitle("添加随礼记录" if not edit_mode else "编辑随礼记录")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Microsoft YaHei';
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # 标题
        title = QLabel(self.windowTitle())
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 1px solid #9b59b6;
        """)
        title.setAlignment(Qt.AlignCenter)

        # 表单
        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # 姓名
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #9b59b6;
            }
        """)

        # 事由
        self.reason_input = QLineEdit()
        self.reason_input.setStyleSheet(self.name_input.styleSheet())

        # 金额
        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet(self.name_input.styleSheet())

        form_layout.addRow("姓名:", self.name_input)
        form_layout.addRow("事由:", self.reason_input)
        form_layout.addRow("金额:", self.amount_input)

        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        save_btn.clicked.connect(self.validate_and_accept)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(title)
        layout.addWidget(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def set_data(self, data):
        self.name_input.setText(data['name'])
        self.reason_input.setText(data['reason'])
        self.amount_input.setText(str(data['amount']))

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'reason': self.reason_input.text().strip(),
            'amount': float(self.amount_input.text()) if self.amount_input.text() else 0
        }

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "输入错误", "姓名不能为空")
            self.name_input.setFocus()
            return

        try:
            float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "金额必须是数字")
            self.amount_input.setFocus()
            return

        self.accept()


# ======================
# 应用入口
# ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建并显示登录对话框
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())