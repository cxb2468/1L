import sys
import pymysql
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QLineEdit, QPushButton, QTableWidget, QVBoxLayout, QWidget, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("数据库操作示例")
        self.setGeometry(100, 100, 800, 600)

        # 数据库配置
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'school1',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.table_name = 'users'

        # 初始化UI
        self.init_ui()

        # 初始化数据库连接
        self.connection = self.create_connection()
        self.load_data()

    def init_ui(self):
        # 创建主窗口的UI组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建布局
        self.layout = QVBoxLayout()

        # 创建输入框和标签
        self.name_label = QLabel("姓名:")
        self.name_edit = QLineEdit()
        self.username_label = QLabel("账号:")
        self.username_edit = QLineEdit()
        self.password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        # 创建按钮
        self.insert_btn = QPushButton("新增")
        self.del_btn = QPushButton("删除")
        self.select_btn = QPushButton("查询")
        self.update_btn = QPushButton("更新")

        # 创建表格
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(['姓名', '账号', '密码'])

        # 创建结果显示标签
        self.result_label = QLabel()

        # 将组件添加到布局中
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.insert_btn)
        self.layout.addWidget(self.del_btn)
        self.layout.addWidget(self.select_btn)
        self.layout.addWidget(self.update_btn)
        self.layout.addWidget(self.data_table)
        self.layout.addWidget(self.result_label)

        # 设置主窗口的布局
        self.central_widget.setLayout(self.layout)

        # 连接按钮事件
        self.insert_btn.clicked.connect(self.insert_data)
        self.del_btn.clicked.connect(self.delete_data)
        self.select_btn.clicked.connect(self.select_data)
        self.update_btn.clicked.connect(self.update_data)

        # 为表格添加行点击事件
        self.data_table.itemClicked.connect(self.on_row_clicked)

    def on_row_clicked(self, item):
        """处理表格行点击事件"""
        selected_row = item.row()
        name_item = self.data_table.item(selected_row, 0)
        username_item = self.data_table.item(selected_row, 1)
        password_item = self.data_table.item(selected_row, 2)

        if name_item and username_item and password_item:
            self.name_edit.setText(name_item.text())
            self.username_edit.setText(username_item.text())
            self.password_edit.setText(password_item.text())

    def create_connection(self):
        """创建数据库连接"""
        try:
            return pymysql.connect(**self.db_config)
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "连接错误", f"数据库连接失败: {str(e)}")
            sys.exit(1)

    def closeEvent(self, event):
        """窗口关闭时断开数据库连接"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
        event.accept()

    def clear_input(self):
        """清空输入框"""
        self.name_edit.clear()
        self.username_edit.clear()
        self.password_edit.clear()

    def load_data(self):
        """加载数据到表格"""
        try:
            self.connection.ping(reconnect=True)
            with self.connection.cursor() as cursor:
                sql = f"SELECT name, username, password FROM {self.table_name}"
                cursor.execute(sql)
                results = cursor.fetchall()

                self.data_table.setRowCount(len(results))

                for i, row in enumerate(results):
                    for j, key in enumerate(['name', 'username', 'password']):
                        item = QTableWidgetItem(str(row[key]))
                        self.data_table.setItem(i, j, item)

                self.result_label.setText("数据加载成功！")
        except Exception as e:
            self.result_label.setText(f"运行错误: {str(e)}")
            print(e)

    def execute_query(self, sql, params=None):
        """执行SQL查询"""
        try:
            self.connection.ping(reconnect=True)
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                self.connection.commit()
                return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            self.result_label.setText(f"数据库错误: {str(e)}")
            print(e)
            return []

    def insert_data(self):
        """插入数据"""
        name = self.name_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not all([name, username, password]):
            QMessageBox.warning(self, "输入错误", "所有字段都不能为空")
            return

        sql = f"INSERT INTO {self.table_name} (name, username, password) VALUES (%s, %s, %s)"
        self.execute_query(sql, (name, username, password))
        self.load_data()
        self.clear_input()
        self.result_label.setText("新增数据成功！")

    def delete_data(self):
        """删除数据"""
        # 获取表格中选中的行
        selected_items = self.data_table.selectedItems()
        if selected_items:
            # 如果有选中的行，获取该行的账号
            selected_row = selected_items[0].row()
            username_item = self.data_table.item(selected_row, 1)  # 假设账号在第二列（索引为1）
            if username_item:
                username = username_item.text()
            else:
                QMessageBox.warning(self, "输入错误", "请选择有效的账号行")
                return
        else:
            # 如果没有选中的行，检查输入框中的账号
            username = self.username_edit.text()
            if not username:
                QMessageBox.warning(self, "输入错误", "请输入要删除的账号")
                return

        sql = f"DELETE FROM {self.table_name} WHERE username = %s"
        affected_rows = self.execute_query(sql, (username,))

        if affected_rows == 0:
            QMessageBox.information(self, "提示", "未找到对应账号")
        else:
            self.load_data()
            self.clear_input()
            self.result_label.setText("删除数据成功！")

    def select_data(self):
        """查询数据"""
        username = self.username_edit.text()
        if not username:
            self.load_data()
            self.result_label.setText("请输入账号查询！")
            return

        sql = f"SELECT name, username, password FROM {self.table_name} WHERE username = %s"
        results = self.execute_query(sql, (username,))

        self.data_table.setRowCount(len(results))

        if not results:
            QMessageBox.information(self, "提示", "没有符合条件的记录")
            return

        for i, row in enumerate(results):
            for j, key in enumerate(['name', 'username', 'password']):
                item = QTableWidgetItem(str(row[key]))
                self.data_table.setItem(i, j, item)

        self.result_label.setText("查询成功！")

    def update_data(self):
        """更新数据"""
        new_name = self.name_edit.text().strip()  # 移除前后空白
        username = self.username_edit.text().strip()
        new_password = self.password_edit.text().strip()

        if not all([new_name, username, new_password]):
            QMessageBox.warning(self, "输入错误", "所有字段都不能为空")
            return

        # 构建更新SQL语句
        sql = f"UPDATE {self.table_name} SET name = %s, password = %s WHERE username = %s"
        
        # 执行更新操作
        affected_rows = self.execute_query(sql, (new_name, new_password, username))

        if affected_rows == 0:
            QMessageBox.information(self, "提示", "未找到对应账号或更新失败")
        else:
            self.load_data()  # 重新加载数据以反映更新结果
            self.clear_input()  # 清空输入框
            self.result_label.setText("修改数据成功！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())