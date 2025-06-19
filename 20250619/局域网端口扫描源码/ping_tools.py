# ping_tools.py
import platform
import subprocess
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal


def ping_once(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, "1", ip]

    startupinfo = None
    if platform.system().lower() == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        output = result.stdout or result.stderr or "未获取到输出"
    except Exception as e:
        output = f"Ping 失败：{e}"

    QMessageBox.information(None, "Ping 结果", output)


class PingLoopThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self._running = True

    def run(self):
        param = "-n" if platform.system().lower() == "windows" else "-c"

        startupinfo = None
        if platform.system().lower() == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        while self._running:
            try:
                result = subprocess.run(
                    ["ping", param, "1", self.ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    startupinfo=startupinfo
                )
                out = result.stdout or result.stderr
                self.output_signal.emit(out.strip())
            except Exception as e:
                self.output_signal.emit(f"错误：{e}")
            self.msleep(1500)

    def stop(self):
        self._running = False


def ping_loop(ip):
    dialog = QDialog()
    dialog.setWindowTitle(f"持续 Ping：{ip}")
    dialog.resize(500, 400)

    layout = QVBoxLayout()
    output_box = QTextEdit()
    output_box.setReadOnly(True)
    layout.addWidget(output_box)

    stop_button = QPushButton("停止")
    layout.addWidget(stop_button)

    thread = PingLoopThread(ip)
    thread.output_signal.connect(lambda text: output_box.append(text))
    stop_button.clicked.connect(lambda: (thread.stop(), dialog.close()))

    dialog.setLayout(layout)
    thread.start()
    dialog.exec_()
    thread.stop()
