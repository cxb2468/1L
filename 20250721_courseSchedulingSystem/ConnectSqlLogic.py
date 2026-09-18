#from ConnectSql import Ui_MainWindow
import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
import pymysql

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # 定义表名
        self.table_name = 'your_table'  # 替换为你的表名

        # 设置数据库连接
        self.connection = pymysql.connect(
            host='localhost',  # 你的 MySQL 服务器主机名
            user='root',  # 你的数据库用户名
            password='root',  # 你的数据库密码
            database='school1',  # 你的数据库名
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # 初始化表格视图
        self.init_table_view()