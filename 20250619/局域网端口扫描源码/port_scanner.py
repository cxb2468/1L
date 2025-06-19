# port_scanner.py
import socket
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal


class PortScanThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, ip, port_start, port_end):
        super().__init__()
        self.ip = ip
        self.port_start = port_start
        self.port_end = port_end
        self._running = True

    def run(self):
        for port in range(self.port_start, self.port_end + 1):
            if not self._running:
                break
            status = self.scan_port(self.ip, port)
            self.output_signal.emit(f"{port}: {status}")

    def scan_port(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((ip, port))
            s.close()
            return "✅ 开放"
        except:
            return "❌ 关闭"

    def stop(self):
        self._running = False


def scan_ports(ip):
    dialog = QDialog()
    dialog.setWindowTitle(f"端口扫描 - {ip}")
    dialog.resize(600, 500)

    layout = QVBoxLayout()

    input_layout = QHBoxLayout()
    input_label = QLabel("端口范围：")
    port_input = QLineEdit("1-1024")
    input_layout.addWidget(input_label)
    input_layout.addWidget(port_input)

    output = QTextEdit()
    output.setReadOnly(True)

    button_layout = QHBoxLayout()
    start_btn = QPushButton("开始扫描")
    stop_btn = QPushButton("停止")
    close_btn = QPushButton("关闭")

    button_layout.addWidget(start_btn)
    button_layout.addWidget(stop_btn)
    button_layout.addWidget(close_btn)

    layout.addLayout(input_layout)
    layout.addWidget(output)
    layout.addLayout(button_layout)
    dialog.setLayout(layout)

    thread = None

    def start_scan():
        nonlocal thread
        text = port_input.text().strip()
        try:
            p1, p2 = map(int, text.split("-"))
            if p1 < 1 or p2 > 65535 or p1 > p2:
                output.append("❌ 端口范围必须在 1~65535 且格式正确")
                return
        except:
            output.append("❌ 端口格式错误，应为如 20-80")
            return

        output.clear()
        output.append(f"开始扫描 {ip} 的端口 {p1}-{p2} ...")

        thread = PortScanThread(ip, p1, p2)
        thread.output_signal.connect(lambda msg: output.append(msg))
        thread.start()

    def stop_scan():
        if thread:
            thread.stop()
            output.append("✅ 扫描已手动中止。")

    start_btn.clicked.connect(start_scan)
    stop_btn.clicked.connect(stop_scan)
    close_btn.clicked.connect(dialog.close)

    dialog.exec_()
