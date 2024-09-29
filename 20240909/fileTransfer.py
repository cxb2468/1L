# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QRadioButton, QMainWindow, QLabel, QComboBox, QLineEdit, QPushButton, \
    QMessageBox, QToolButton, QFileDialog, QDialog
from PyQt5.QtCore import QDir, Qt, QThread, pyqtSignal
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QFont
import sys
import os
import random
import netifaces
from flask import Flask, send_from_directory, abort
from flask import make_response
from concurrent.futures import ThreadPoolExecutor
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from ftplib import FTP
from urllib.parse import urlparse


class HelpWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("帮助")
        self.setFixedSize(300, 280)
        self.center()
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.label = QLabel(self)
        self.label.setText("1、选择文件传输协议；2、输入端口号（建议10000~60000，一般默认即可）； \
                            3、选择文件所在目录；4、选择要分享的文件；5、点击启动按钮，\
                           若防火墙弹出警示点击允许访问即可；6、将生成的链接复制发送给接收方， \
                           接收方通过浏览器访问即可下载。若通过FTP协议分享还可通过FTP客户端软件  \
                            或本程序的“接收FTP文件”按钮下载。注意：传输完成后请及时关闭程序， \
                            以免造成数据泄露和网络安全隐患。")
        self.label.setGeometry(10, 10, 280, 260)
        self.label.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.label.setFont(font)

    def center(self):
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)


class DownloadThread(QThread):
    finished = pyqtSignal(bool)
    ftp = FTP()

    def __init__(self, ftp_url):
        super().__init__()
        self.ftp_url = ftp_url

    def run(self):
        parsed_url = urlparse(self.ftp_url)
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        filename = parsed_url.path.rsplit('/', 1)[-1]
        if len(filename) == 0:
            downloadfile = False
        else:
            downloadfile = True
        try:
            self.ftp.connect(host, port)
            self.ftp.encoding = 'utf-8'
            self.ftp.login(user=username, passwd=password)

            current_dir = os.getcwd()
            current_dir = current_dir.replace("\\", "/")
            random_int = random.randint(100, 999)
            mulu = "接收文件_" + str(random_int)
            LocalDir = current_dir + "/" + mulu
            if not os.path.exists(LocalDir):
                os.makedirs(LocalDir)
            if downloadfile:  # 下载一个文件
                Local = os.path.join(LocalDir, filename)
                self.DownLoadFile(Local, filename)
            else:  # 下载整个目录
                self.DownLoadFileTree(LocalDir, "/")
            self.ftp.quit()
            self.finished.emit(True)
        except Exception as e:
            self.finished.emit(False)

    def DownLoadFile(self, LocalFile, RemoteFile):  # 下载单个文件
        with open(LocalFile, 'wb') as file_handler:
            self.ftp.retrbinary('RETR ' + RemoteFile, file_handler.write)
        file_handler.close()
        return True

    def DownLoadFileTree(self, LocalDir, RemoteDir):  # 下载整个目录下的文件
        print("远程文件夹remoteDir:", RemoteDir)
        if not os.path.exists(LocalDir):
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print("远程文件目录：", RemoteNames)
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            # print("正在下载", self.ftp.nlst(file))
            try:
                self.ftp.cwd(file)
                self.ftp.cwd("..")
                if not os.path.exists(Local):
                    os.makedirs(Local)
                self.DownLoadFileTree(Local, file)
            except:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return


class FTPWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("下载FTP文件")
        self.setFixedSize(400, 150)

        self.label_ftp_url = QLabel("FTP链接:", self)
        self.label_ftp_url.setGeometry(20, 20, 80, 30)

        self.textbox_ftp_url = QLineEdit(self)
        self.textbox_ftp_url.setGeometry(100, 20, 280, 30)

        self.button_download = QPushButton("下载", self)
        self.button_download.setGeometry(160, 65, 80, 30)
        self.button_download.clicked.connect(self.download_ftp_file)

        self.label_ftp_info = QLabel("输入包含文件名的链接下载指定文件；\n输入不包含文件名只到端口号的链接下载整个目录。", self)
        self.label_ftp_info.setGeometry(20, 110, 380, 40)

    def download_ftp_file(self):
        ftp_url = self.textbox_ftp_url.text()
        if ftp_url == "":
            return
        self.button_download.setEnabled(False)
        self.thread = DownloadThread(ftp_url)
        self.thread.finished.connect(self.show_message_box)
        self.thread.start()

    def show_message_box(self, success):
        if success:
            QMessageBox.information(self, "提示", "文件下载成功！", QMessageBox.Ok)
        else:
            QMessageBox.critical(self, "错误", "文件下载失败！", QMessageBox.Ok)
        self.button_download.setEnabled(True)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件分享")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setMaximumSize(self.size())
        self.setFixedSize(400, 300)

        self.tcp_label = QLabel('选择传输方式:', self)
        self.tcp_label.move(20, 10)
        self.http_button = QRadioButton('HTTP', self)
        self.http_button.setChecked(True)
        self.http_button.move(150, 10)
        self.http_button.toggled.connect(self.onProtocolChanged)
        self.ftp_button = QRadioButton('FTP', self)
        self.ftp_button.move(250, 10)
        self.ftp_button.toggled.connect(self.onProtocolChanged)

        self.ip_label = QLabel('当前IP地址:', self)
        self.ip_label.move(20, 40)
        self.ip_text = QLabel(self.get_wired_ip(), self)
        self.ip_text.setGeometry(120, 43, 250, 25)

        self.port_label = QLabel('端 口 :', self)
        self.port_label.move(20, 75)

        self.textbox = QLineEdit(self)
        self.textbox.setGeometry(80, 75, 300, 30)
        self.textbox.setValidator(QtGui.QIntValidator(10000, 65500))
        self.textbox.setText(str(random.randint(10000, 65500)))

        self.folder_label = QLabel('文件夹:', self)
        self.folder_label.setGeometry(20, 115, 50, 30)

        self.textfol = QLineEdit(self)
        self.textfol.setGeometry(80, 115, 220, 30)
        self.textfol.setText(QDir.currentPath())
        self.textfol.setReadOnly(True)

        self.folder_button = QPushButton('选择文件夹', self)
        self.folder_button.setGeometry(300, 115, 80, 30)
        self.folder_button.clicked.connect(self.onFolderClicked)

        self.file_label = QLabel('文 件 :', self)
        self.file_label.setGeometry(20, 155, 50, 30)

        self.combobox = QComboBox(self)
        self.combobox.setGeometry(80, 155, 300, 30)

        self.updateFileList()

        self.button = QPushButton(self)
        self.button.setText("启  动")
        self.button.setGeometry(20, 195, 360, 30)
        self.button.clicked.connect(self.show_selection)

        self.textboxa = QLineEdit(self)
        self.textboxa.setGeometry(20, 235, 360, 30)
        self.textboxa.mousePressEvent = self.select_text

        self.hidden_button = QPushButton("接收\nFTP\n文件", self)
        self.hidden_button.setVisible(False)
        self.hidden_button.setGeometry(320, 10, 60, 55)
        self.hidden_button.clicked.connect(self.show_ftp_window)

        self.labela = QLabel(self)
        self.labela.setText("52pojie")
        self.labela.setGeometry(300, 280, 360, 20)

        self.labelb = QPushButton(self)
        self.labelb.setText("？")
        self.labelb.setToolTip("帮助")
        self.labelb.setGeometry(10, self.height() - 30, 30, 30)
        self.labelb.clicked.connect(self.open_help_window)

        self.help_window = HelpWindow()

        self.thread_pool = ThreadPoolExecutor(max_workers=5)

    def open_help_window(self):
        self.help_window.show()

    def select_text(self, event):
        self.textboxa.selectAll()
        self.textboxa.setFocus()

    def show_ftp_window(self):
        ftp_window = FTPWindow(self)
        ftp_window.exec_()

    def onProtocolChanged(self):
        if self.ftp_button.isChecked():
            self.hidden_button.setVisible(True)
        else:
            self.hidden_button.setVisible(False)

    def onFolderClicked(self):
        m = QFileDialog.getExistingDirectory(self, "选取文件夹", QDir.currentPath())
        self.textfol.setText(m)
        self.updateFileList()

    def updateFileList(self):
        folder_path = self.textfol.text()
        file_list = QDir(folder_path).entryList(QDir.Files)
        self.combobox.clear()
        self.combobox.addItems(file_list)

    def get_wired_ip(self):
        try:
            default_gateway = netifaces.gateways()['default']
            if default_gateway and netifaces.AF_INET in default_gateway:
                routingNicName = default_gateway[netifaces.AF_INET][1]
                for interface in netifaces.interfaces():
                    if interface == routingNicName:
                        routingIPAddr = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
                        if routingIPAddr:
                            return routingIPAddr[0]['addr']
        except (KeyError, IndexError):
            pass
        return "未找到物理网卡IP"

    def start_flask_server(self):
        app = Flask(__name__)

        @app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            file_path = os.path.join(self.textfol.text(), filename)
            if not os.path.exists(file_path):
                abort(404)
            # return send_from_directory(self.textfol.text(), filename, as_attachment=True, conditional=True)
            response = make_response(
                send_from_directory(self.textfol.text(), filename.encode('utf-8').decode('utf-8'), as_attachment=True,
                                    conditional=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(
                filename.encode().decode('latin-1'))
            return response

        port = int(self.textbox.text())
        self.textbox.setText(str(random.randint(10000, 65500)))
        app.run(host='0.0.0.0', port=port, threaded=True)

    def start_ftp_server(self):
        authorizer = DummyAuthorizer()
        authorizer.add_user('a', 'a', self.textfol.text(), perm='elradfmwM')

        class CustomFTPHandler(FTPHandler):
            def on_file_received(self, file):
                pass

            def on_file_deleted(self, file):
                pass

            def on_rename(self, old_file, new_file):
                pass

        handler = CustomFTPHandler
        handler.authorizer = authorizer

        address = ('0.0.0.0', int(self.textbox.text()))

        server = ThreadedFTPServer(address, handler)
        self.thread_pool.submit(server.serve_forever)
        self.textbox.setText(str(random.randint(10000, 65500)))

    def show_selection(self):
        ip_address = self.get_wired_ip()
        port_text = self.textbox.text()
        if int(port_text) < 10000:
            QMessageBox.critical(self, "警告", "请勿使用10000以下端口号!", QMessageBox.Ok)
            self.textbox.setText(str(random.randint(10000, 65500)))
            return
        selected_file = self.combobox.currentText()
        if self.http_button.isChecked():
            self.thread_pool.submit(self.start_flask_server)
            self.textboxa.setText("http://" + ip_address + ":" + port_text + "/download/" + selected_file)
        elif self.ftp_button.isChecked():
            self.thread_pool.submit(self.start_ftp_server)
            self.textboxa.setText("ftp://a:a@" + ip_address + ":" + port_text + "/" + selected_file)
        else:
            QMessageBox.warning(self, "警告", "请选择传输方式！", QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())