# main.py
import sys
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QFileDialog, QHeaderView,
    QMenu, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import scanner
import utils
import ping_tools
import port_scanner
import pyperclip

# ========== ✅ 兼容 PyInstaller 路径的资源加载函数 ==========
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ScanThread(QThread):
    update_progress = pyqtSignal(int)
    result_signal = pyqtSignal(object)  # 支持 (list, float)

    def __init__(self, ip_range):
        super().__init__()
        self.ip_range = ip_range

    def run(self):
        start_time = time.time()
        results = scanner.scan_ip_range(self.ip_range, self.update_progress)
        used_time = round(time.time() - start_time, 2)
        self.result_signal.emit((results, used_time))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("局域网设备扫描工具")
        self.setWindowIcon(QIcon(resource_path("mylogo.ico")))  # ✅ 图标路径修复
        self.setFixedSize(850, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #fdfdfd;
                font-family: '微软雅黑';
                font-size: 12px;
            }
            QPushButton {
                background-color: #e8e8e8;
                border: 1px solid #bbb;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #d0eaff;
            }
            QTableWidget {
                border: 1px solid #ccc;
            }
        """)

        layout = QVBoxLayout()

        # 顶部：本机IP + 扫描范围输入框
        local_ip = utils.get_local_ip()
        self.ip_label = QLabel(f"本机 IP：{local_ip}")
        self.range_input = QLineEdit(utils.get_default_ip_range(local_ip))
        self.range_input.setPlaceholderText("请输入扫描范围，如 192.168.0.1-254")
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.ip_label)
        top_layout.addWidget(QLabel("扫描范围："))
        top_layout.addWidget(self.range_input)
        layout.addLayout(top_layout)

        # 表格
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["IP 地址", "主机名", "MAC 地址", "厂商", "状态", "图标"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        layout.addWidget(self.table)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.scan_btn)

        self.export_btn = QPushButton("导出 CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)

        self.about_btn = QPushButton("关于")
        self.about_btn.clicked.connect(self.show_about_dialog)
        btn_layout.addWidget(self.about_btn)

        layout.addLayout(btn_layout)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setFixedHeight(18)
        layout.addWidget(self.progress)

        # 状态栏
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_scan(self):
        ip_range = self.range_input.text().strip()
        if not utils.validate_ip_range(ip_range):
            QMessageBox.warning(self, "输入错误", "请输入合法的 IP 范围，如 192.168.1.1-254")
            return

        self.table.setRowCount(0)
        self.progress.setValue(0)
        self.status_label.setText("正在扫描中...")
        self.scan_thread = ScanThread(ip_range)
        self.scan_thread.update_progress.connect(self.progress.setValue)
        self.scan_thread.result_signal.connect(self.show_result)
        self.scan_thread.start()

    def show_result(self, result_tuple):
        results, used_time = result_tuple
        self.table.setRowCount(len(results))
        for i, row in enumerate(results):
            for j, item in enumerate(row):
                cell = QTableWidgetItem(item)
                cell.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, cell)

        self.status_label.setText(f"扫描完成：共 {len(results)} 台在线设备，用时 {used_time} 秒")

    def open_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if item:
            row = item.row()
            ip = self.table.item(row, 0).text()
            hostname = self.table.item(row, 1).text()
            mac = self.table.item(row, 2).text()

            menu = QMenu()
            copy_ip = menu.addAction("复制 IP")
            copy_host = menu.addAction("复制主机名")
            copy_mac = menu.addAction("复制 MAC")
            menu.addSeparator()
            ping_once = menu.addAction("单次 Ping")
            ping_loop = menu.addAction("持续 Ping")
            port_scan = menu.addAction("端口扫描")

            action = menu.exec_(QCursor.pos())
            if action == copy_ip:
                pyperclip.copy(ip)
            elif action == copy_host:
                pyperclip.copy(hostname)
            elif action == copy_mac:
                pyperclip.copy(mac)
            elif action == ping_once:
                ping_tools.ping_once(ip)
            elif action == ping_loop:
                ping_tools.ping_loop(ip)
            elif action == port_scan:
                port_scanner.scan_ports(ip)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出CSV", "result.csv", "CSV 文件 (*.csv)")
        if path:
            with open(path, "w", encoding="utf-8", newline="") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["IP 地址", "主机名", "MAC 地址", "厂商", "状态", "图标"])
                for row in range(self.table.rowCount()):
                    writer.writerow([
                        self.table.item(row, 0).text(),
                        self.table.item(row, 1).text(),
                        self.table.item(row, 2).text(),
                        self.table.item(row, 3).text(),
                        self.table.item(row, 4).text(),
                        self.table.item(row, 5).text()
                    ])

    def show_about_dialog(self):
        QMessageBox.information(self, "关于本软件",
            "【局域网设备扫描工具】\n\n"
            "📡 功能介绍：\n"
            " - 扫描局域网内设备：IP、MAC、主机名、厂商名、在线状态\n"
            " - 支持自定义 IP 范围、右键操作（Ping、端口扫描）、导出结果\n"
            " - 自动识别设备类型并显示图标（📱🖨️👨‍💻）\n\n"
            "🧩 使用说明：\n"
            " 1. 输入 IP 范围（如 192.168.1.1-254）\n"
            " 2. 点击“开始扫描”\n"
            " 3. 在表格中右键点击设备可查看/操作\n\n"
            "👨‍💻 作者：黄明博-网络中心\n"
            "📅 版本：v1.0\n"
            "© 2025 All Rights Reserved."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
