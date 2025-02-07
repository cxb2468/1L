import os
import sys
import pandas as pd

import OpenGL as gl

from PyQt5 import QtWidgets, Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QMessageBox, QFileDialog, QTableWidgetItem

# 添加缺失的导入
from Ui_gps import Ui_gps
from Worker import Worker


# 添加缺失的坐标转换函数定义或导入
def wgs84_to_gcj02(lng, lat):
    # 实现 WGS84 到 GCJ02 的转换逻辑
    pass

def wgs84_to_bd09(lng, lat):
    # 实现 WGS84 到 BD09 的转换逻辑
    pass

def gcj02_to_bd09(lng, lat):
    # 实现 GCJ02 到 BD09 的转换逻辑
    pass

def gcj02_to_wgs84(lng, lat):
    # 实现 GCJ02 到 WGS84 的转换逻辑
    pass

def bd09_to_wgs84(lng, lat):
    # 实现 BD09 到 WGS84 的转换逻辑
    pass

def bd09_to_gcj02(lng, lat):
    # 实现 BD09 到 GCJ02 的转换逻辑
    pass


class GPS(Ui_gps, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        # 更改objectName名称
        self.setObjectName("GPS")

        # 将PushButton1-6与坐标转换函数关联
        functions = [wgs84_to_gcj02, wgs84_to_bd09, gcj02_to_bd09, gcj02_to_wgs84, bd09_to_wgs84, bd09_to_gcj02]
        for i in range(6):
            button = getattr(self, f"zuobiao_{i + 1}")
            button.clicked.connect(lambda _, func=functions[i]: self.do_convert(func))
        # 点击导出
        self.zuobiao_7.clicked.connect(self.export_table_data)
        # 选择导入文件
        self.pushButton_2.clicked.connect(self.selectFile)
        # 执行导入程序
        self.pushButton.clicked.connect(self.update_coordinates)
        self.conn = None
        self.cur = None
        self.worker = None  # 初始化worker线程

    """=============================如下坐标转换==================================="""

    def do_convert(self, convert_func):
        # 获取用户选择的文件路径
        filePath, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if filePath:
            # 获取文件扩展名
            ext = os.path.splitext(filePath)[1]
            # 判断是否为Excel文件
            if ext in [".xlsx", ".xls"]:
                # 读取 Excel 文件
                df = pd.read_excel(filePath)
                # 处理数据
                rows = []
                for i, row in df.iterrows():
                    lng, lat = row['经度'], row['纬度']
                    result_lng, result_lat = convert_func(lng, lat)
                    rows.append([i + 2, lng, lat, result_lng, result_lat])

                # 在 tableWidget 中显示转换结果
                self.tableWidget.setRowCount(len(rows))
                self.tableWidget.setColumnCount(5)
                for i, row in enumerate(rows):
                    for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        if j == 0:
                            item.setFlags(item.flags() & (~Qt.ItemIsEnabled))
                        self.tableWidget.setItem(i, j, item)
            else:
                # 否则弹出警告窗口，并清空QLineEdit
                QMessageBox.warning(self, "友情提示：", "请选择正确的Excel文件！")

    def export_table_data(self):
        # 检查 TableWidget 是否为空
        if self.tableWidget.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, '无数据导出', '请先进行坐标转换！')
        else:
            # 弹出提示窗口
            self.progress_dialog = QMessageBox(self)
            self.progress_dialog.setWindowTitle('正在导出')
            self.progress_dialog.setText('正在导出，请稍后...')
            self.progress_dialog.show()
            try:
                # 创建一个空的 DataFrame 对象
                data_frame = pd.DataFrame(columns=[self.tableWidget.horizontalHeaderItem(j).text() for j in
                                                   range(self.tableWidget.columnCount())])
                # 将每一行的数据添加到 DataFrame 中
                for i in range(self.tableWidget.rowCount()):
                    row_data = [
                        self.tableWidget.item(i, j).text() if self.tableWidget.item(i, j) is not None else ''
                        for j in range(self.tableWidget.columnCount())]
                    data_frame.loc[len(data_frame)] = row_data

                # 将 DataFrame 导出到 Excel 文件中
                writer = pd.ExcelWriter('坐标转换完成.xlsx', engine='openpyxl')
                data_frame.to_excel(writer, index=False)
                writer.close()
                # 隐藏进度对话框并弹出提示窗口
                self.progress_dialog.hide()
                QMessageBox.information(self, '导出成功', f'文件已保存至 {os.path.abspath("坐标转换完成.xlsx")}')
            except Exception as e:
                # 隐藏进度对话框并弹出错误窗口
                self.progress_dialog.hide()
                QMessageBox.critical(self, '导出失败', f'导出文件时发生错误：{e}')

    """=============================如下坐标更新==================================="""

    def selectFile(self):
        """
        打开文件对话框以选择需要验证的数据文件。
        """
        # 使用QFileDialog获取文件路径
        filePath, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if filePath:
            # 获取文件扩展名
            ext = os.path.splitext(filePath)[1]
            # 判断是否为Excel文件
            if ext in [".xlsx", ".xls"]:
                # 如果成功选择Excel文件，则将其路径显示在QLineEdit中
                self.lineEdit.setText(filePath)
            else:
                # 否则弹出警告窗口，并清空QLineEdit
                QMessageBox.warning(self, "友情提示：", "请选择正确的Excel文件！")
                self.lineEdit.clear()
        else:
            # 如果没有选择任何文件，则清空QLineEdit
            self.lineEdit.clear()

    def update_coordinates(self):
        conn = gl.get_value("current_connection")
        file_path = self.lineEdit.text()
        # 获取是否使用高德GPS
        use_gaode_gps = self.radioButton.isChecked()
        if file_path and conn:
            if self.worker is not None and self.worker.isRunning():
                QMessageBox.warning(self, "友情提示：", "当前有正在执行的任务，请等待完成后再执行新任务。")
                return
            self.worker = Worker(file_path, conn, use_gaode_gps)
            self.worker.progress_updated.connect(self.progressBar.setValue)
            self.worker.message_updated.connect(self.log_message)
            self.worker.operation_complete.connect(self.final_message)
            self.worker.start()
        else:
            QMessageBox.warning(self, "友情提示：", "请选择文件并确保数据库连接正常后再进行操作！")

    def log_message(self, message):
        self.textEdit.append(message)
        QCoreApplication.processEvents()

    def final_message(self, message):
        QMessageBox.information(self, "操作完成", message)

def main():
    app = QApplication(sys.argv)
    window = GPS()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
