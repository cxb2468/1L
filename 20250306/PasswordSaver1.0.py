import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QHeaderView, QCheckBox, QAbstractItemView, QLabel, QComboBox, QMenu
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QColor, QClipboard

class AddPasswordDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.setWindowTitle('添加/编辑记录')
        self.setModal(True)

        # 布局
        layout = QFormLayout(self)

        # 输入框
        self.website_input = QLineEdit(self)
        self.website_input.setPlaceholderText('网址')
        layout.addRow('网址:', self.website_input)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('用户名')
        layout.addRow('用户名:', self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('密码')
        layout.addRow('密码:', self.password_input)

        self.notes_input = QLineEdit(self)
        self.notes_input.setPlaceholderText('备注')
        layout.addRow('备注:', self.notes_input)

        # 按钮
        buttons_layout = QHBoxLayout()
        save_button = QPushButton('保存', self)
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton('取消', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)

        # 如果是编辑模式，填充数据
        if record:
            self.website_input.setText(record[1])
            self.username_input.setText(record[2])
            self.password_input.setText(record[3])
            self.notes_input.setText(record[4])

    def get_data(self):
        return (
            self.website_input.text(),
            self.username_input.text(),
            self.password_input.text(),
            self.notes_input.text()
        )

class PasswordManager(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 1  # 当前页
        self.page_size = 10  # 每页显示的记录数
        self.total_pages = 1  # 总页数
        self.initUI()

    def initUI(self):
        self.setWindowTitle('密码管理器')
        self.setGeometry(100, 100, 1000, 800)  # 设置窗口大小

        # 主布局
        main_layout = QVBoxLayout()

        # 顶部布局（搜索框和按钮）
        top_layout = QHBoxLayout()

        # 添加按钮（绿色）放在左上角
        add_button = QPushButton('添加', self)
        add_button.setStyleSheet('background-color: green; color: white; font-weight: bold; font-size: 18px; padding: 10px;')
        add_button.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(add_button, alignment=Qt.AlignLeft)

        # 搜索框
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('搜索（网址、用户名、备注）')
        self.search_input.textChanged.connect(self.search_passwords)
        top_layout.addWidget(self.search_input)

        # 删除按钮（红色）放在右上角
        delete_button = QPushButton('删除', self)
        delete_button.setStyleSheet('background-color: red; color: white; font-weight: bold; font-size: 18px; padding: 10px;')
        delete_button.clicked.connect(self.delete_password)
        top_layout.addWidget(delete_button, alignment=Qt.AlignRight)

        main_layout.addLayout(top_layout)

        # 密码表格
        self.password_table = QTableWidget(self)
        self.password_table.setColumnCount(6)  # 添加一列用于选择框
        self.password_table.setHorizontalHeaderLabels(['选择', '网站', '用户名', '密码', '备注', '操作'])
        self.password_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应列宽
        self.password_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
        self.password_table.cellDoubleClicked.connect(self.open_website)  # 双击打开网址
        self.password_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 单击行即可选择
        self.password_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用右键菜单
        self.password_table.customContextMenuRequested.connect(self.show_context_menu)  # 右键菜单事件
        main_layout.addWidget(self.password_table)

        # 底部布局（全选、分页符号、跳转页码、每页条数）
        bottom_layout = QHBoxLayout()

        # 全选框放在最左侧
        self.select_all_checkbox = QCheckBox('全选', self)
        self.select_all_checkbox.stateChanged.connect(self.select_all_checkbox_changed)
        bottom_layout.addWidget(self.select_all_checkbox, alignment=Qt.AlignLeft)

        # 分页符号和页码
        pagination_layout = QHBoxLayout()

        # 上一页按钮
        prev_button = QPushButton('<', self)
        prev_button.setStyleSheet('font-size: 14px;')
        prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_button)

        # 当前页码和总页数
        self.page_info_label = QLabel(f'第 {self.current_page} 页 / {self.total_pages} 页', self)
        self.page_info_label.setStyleSheet('font-size: 16px; color: #333;')
        pagination_layout.addWidget(self.page_info_label)

        # 下一页按钮
        next_button = QPushButton('>', self)
        next_button.setStyleSheet('font-size: 14px;')
        next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_button)

        # 跳转到第几页
        self.jump_to_page_input = QLineEdit(self)
        self.jump_to_page_input.setPlaceholderText('跳转到第几页')
        self.jump_to_page_input.setFixedWidth(100)
        pagination_layout.addWidget(self.jump_to_page_input)

        jump_button = QPushButton('跳转', self)
        jump_button.setStyleSheet('font-size: 14px;')
        jump_button.clicked.connect(self.jump_to_page)
        pagination_layout.addWidget(jump_button)

        # 每页显示条数
        self.page_size_combo = QComboBox(self)
        self.page_size_combo.addItems(['10', '20', '50', '100'])
        self.page_size_combo.setCurrentText(str(self.page_size))
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        pagination_layout.addWidget(QLabel('每页显示条数:', self))
        pagination_layout.addWidget(self.page_size_combo)

        bottom_layout.addLayout(pagination_layout)
        main_layout.addLayout(bottom_layout)

        # 设置主布局
        self.setLayout(main_layout)

        # 加载密码列表
        self.load_passwords()

    def show_add_dialog(self, record=None):
        dialog = AddPasswordDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            website, username, password, notes = dialog.get_data()

            if website and username and password:
                conn = sqlite3.connect('passwords.db')
                c = conn.cursor()
                if record:
                    # 编辑模式
                    c.execute("UPDATE passwords SET website = ?, username = ?, password = ?, notes = ? WHERE id = ?",
                              (website, username, password, notes, record[0]))
                else:
                    # 添加模式
                    c.execute("SELECT id FROM passwords WHERE website = ?", (website,))
                    if c.fetchone():
                        QMessageBox.warning(self, '错误', '该网址已存在！')
                    else:
                        c.execute("INSERT INTO passwords (website, username, password, notes) VALUES (?, ?, ?, ?)",
                                  (website, username, password, notes))
                conn.commit()
                conn.close()

                self.load_passwords()
            else:
                QMessageBox.warning(self, '错误', '请填写网址、用户名和密码')

    def load_passwords(self, search_keyword=None):
        self.password_table.setRowCount(0)  # 清空表格

        # 计算偏移量
        offset = (self.current_page - 1) * self.page_size

        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        if search_keyword:
            # 全局搜索，不限制当前页
            c.execute(f"SELECT id, website, username, password, notes FROM passwords WHERE website LIKE ? OR username LIKE ? OR notes LIKE ?",
                      (f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%"))
        else:
            # 分页查询
            c.execute(f"SELECT id, website, username, password, notes FROM passwords LIMIT ? OFFSET ?",
                      (self.page_size, offset))
        passwords = c.fetchall()

        # 获取总记录数，用于计算总页数
        if search_keyword:
            # 如果是搜索模式，总页数基于搜索结果
            self.total_pages = (len(passwords) + self.page_size - 1) // self.page_size
        else:
            # 如果不是搜索模式，总页数基于全部数据
            c.execute("SELECT COUNT(*) FROM passwords")
            total_count = c.fetchone()[0]
            self.total_pages = (total_count + self.page_size - 1) // self.page_size
        conn.close()

        for row, password in enumerate(passwords):
            self.password_table.insertRow(row)

            # 选择框列
            checkbox = QCheckBox(self)
            checkbox.setChecked(False)
            checkbox.setProperty("id", password[0])  # 使用 setProperty 存储ID
            self.password_table.setCellWidget(row, 0, checkbox)

            # 网站列（可点击超链接）
            website_item = QTableWidgetItem(password[1])
            website_item.setData(Qt.UserRole, password[1])  # 存储网址
            website_item.setForeground(QColor(0, 0, 255))  # 蓝色字体
            website_item.setFlags(website_item.flags() | Qt.ItemIsEnabled)  # 启用点击
            self.password_table.setItem(row, 1, website_item)

            self.password_table.setItem(row, 2, QTableWidgetItem(password[2]))
            self.password_table.setItem(row, 3, QTableWidgetItem(password[3]))
            self.password_table.setItem(row, 4, QTableWidgetItem(password[4]))

            # 操作列（编辑按钮）
            edit_button = QPushButton('编辑', self)
            edit_button.setStyleSheet('background-color: blue; color: white; font-weight: bold;')
            edit_button.clicked.connect(lambda _, record=password: self.show_add_dialog(record))
            self.password_table.setCellWidget(row, 5, edit_button)

        # 更新页码显示
        self.page_info_label.setText(f'第 {self.current_page} 页 / {self.total_pages} 页')

    def search_passwords(self):
        search_keyword = self.search_input.text()
        self.current_page = 1  # 搜索时重置到第一页
        self.load_passwords(search_keyword)

    def delete_password(self):
        selected_records = []
        for row in range(self.password_table.rowCount()):
            checkbox = self.password_table.cellWidget(row, 0)
            if checkbox.isChecked():
                # 获取选中行的信息
                website = self.password_table.item(row, 1).text()
                username = self.password_table.item(row, 2).text()
                notes = self.password_table.item(row, 4).text()
                selected_records.append(f"网站: {website}, 用户名: {username}, 备注: {notes}")

        if selected_records:
            confirmation = QMessageBox.question(self, '确认删除', f"确认删除以下记录：\n\n" + "\n".join(selected_records),
                                                QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                conn = sqlite3.connect('passwords.db')
                c = conn.cursor()
                for row in range(self.password_table.rowCount()):
                    checkbox = self.password_table.cellWidget(row, 0)
                    if checkbox.isChecked():
                        password_id = checkbox.property("id")
                        c.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
                conn.commit()
                conn.close()

                self.load_passwords()
        else:
            QMessageBox.warning(self, '错误', '请选择一条或多条记录')

    def select_all_checkbox_changed(self, state):
        # 全选框改变时，设置所有行的选择框
        for row in range(self.password_table.rowCount()):
            checkbox = self.password_table.cellWidget(row, 0)
            checkbox.setChecked(state == Qt.Checked)

    def open_website(self, row, column):
        if column == 1:  # 只有网站列可以点击
            website = self.password_table.item(row, column).data(Qt.UserRole)
            if website:
                if not website.startswith("http://") and not website.startswith("https://"):
                    website = f"https://{website}"
                QDesktopServices.openUrl(QUrl(website))

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_passwords()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_passwords()

    def jump_to_page(self):
        try:
            page = int(self.jump_to_page_input.text())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.load_passwords()
            else:
                QMessageBox.warning(self, '错误', f'页码必须在 1 到 {self.total_pages} 之间！')
        except ValueError:
            QMessageBox.warning(self, '错误', '请输入有效的页码！')

    def change_page_size(self, size):
        self.page_size = int(size)
        self.current_page = 1  # 重置到第一页
        self.load_passwords()

    def show_context_menu(self, pos):
        # 获取当前选中的行和列
        row = self.password_table.rowAt(pos.y())
        col = self.password_table.columnAt(pos.x())

        # 只有用户名（列2）和密码（列3）支持右键复制
        if row >= 0 and col in [2, 3]:
            menu = QMenu(self)

            # 复制用户名
            if col == 2:
                copy_username_action = menu.addAction('复制用户名')
                copy_username_action.triggered.connect(lambda: self.copy_to_clipboard(row, 2))

            # 复制密码
            if col == 3:
                copy_password_action = menu.addAction('复制密码')
                copy_password_action.triggered.connect(lambda: self.copy_to_clipboard(row, 3))

            # 显示菜单
            menu.exec_(self.password_table.viewport().mapToGlobal(pos))

    def copy_to_clipboard(self, row, col):
        # 获取单元格内容
        item = self.password_table.item(row, col)
        if item:
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text())
            QMessageBox.information(self, '复制成功', f'已复制到剪贴板：{item.text()}')

def create_database():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  website TEXT NOT NULL,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  notes TEXT)''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    app = QApplication(sys.argv)
    manager = PasswordManager()
    manager.show()
    sys.exit(app.exec_())