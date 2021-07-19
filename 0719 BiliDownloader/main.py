
import sys
from lxml import html

from Ui_MainWindow import Ui_MainWindow

etree = html.etree
import os
import re

import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QCoreApplication, QThreadPool, QRunnable, QObject
import requests
import json

import random
import webbrowser
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QFileDialog, QMessageBox, QTableWidgetItem, QProgressBar
from PyQt5 import QtWidgets


def random_user():
    user1 = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    user2 = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"
    user3 = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"
    user4 = "Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1"
    user5 = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"
    user6 = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)"
    user7 = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"
    user8 = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)"
    user = [user1, user2, user3, user4, user5, user6, user7, user8]
    user = random.choice(user)
    return user


class Tasks(QObject):
    updata_data = pyqtSignal(list)
    updata_data2 = pyqtSignal(str, int)


class BackendThread(QRunnable):
    def __init__(self, url, video_name, count):
        super().__init__()
        self.signal = Tasks()

        self.url = url
        self.video_name = video_name
        self.count = count

    def down_file(self, url, filename, file_row, count):  # 这个函数不知用协程会不会更快些
        header = {"User-Agent": random_user(), "referer": "https://message.bilibili.com/"}
        file_data = requests.get(url, headers=header, stream=True)
        filesize = int(file_data.headers['Content-Length'])

        offset = 0
        fileobj = open(filename, 'wb')
        if file_data.status_code == 200:

            for chunk in file_data.iter_content(chunk_size=204800):
                if not chunk:
                    break

                fileobj.seek(offset)

                fileobj.write(chunk)

                offset += len(chunk)
                proess = (offset / filesize) * 100

                self.signal.updata_data.emit([int(proess), file_row, count])

            fileobj.close()

    def run(self):

        self.signal.updata_data.emit([0, 1, self.count])
        self.signal.updata_data.emit([0, 2, self.count])
        header = {"User-Agent": random_user(), "referer": "https://message.bilibili.com/"}
        resonpe = requests.get(self.url, headers=header)

        json_data = re.findall(r'<script>window.__playinfo__=(.*?)</script>', resonpe.text)[0]
        json_data = json.loads(json_data)
        audio_url = json_data["data"]["dash"]["audio"][0]["backupUrl"][0]
        video_url = json_data["data"]["dash"]["video"][0]["backupUrl"][0]
        video_bakname = self.video_name + 'bak.mp4'
        audio_bakname = self.video_name + 'bak.mp3'
        video_fulname = self.video_name + '.mp4'

        self.down_file(video_url, video_bakname, 1, self.count)
        self.down_file(audio_url, audio_bakname, 2, self.count)
        self.signal.updata_data2.emit('开始合并', self.count)

        word = r'ffmpeg -i ' + video_bakname + ' -i ' + audio_bakname + ' -c:v copy -c:a aac -strict experimental  ' + video_fulname
        subprocess.call(word, shell=True)
        self.signal.updata_data2.emit('合并成功', self.count)
        os.remove(video_bakname)
        os.remove(audio_bakname)


class firstfrom(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.page_find)
        self.ui.pushButton_5.clicked.connect(self.change_dir)
        self.ui.pushButton_4.clicked.connect(QCoreApplication.instance().quit)
        self.ui.pushButton_2.clicked.connect(self.start_find)
        self.ui.pushButton_3.clicked.connect(self.start_down)
        self.pool = QThreadPool()
        self.pool.globalInstance()
        self.pool.setMaxThreadCount(int(self.ui.comboBox.currentText()))
        self.ui.checkBox.clicked.connect(self.check)
        self.ui.pushButton_6.clicked.connect(self.opendir)

    def opendir(self):
        if not os.path.exists(self.ui.label_5.text()):
            os.mkdir(self.ui.label_5.text())
        if self.ui.label_5.text() == './B站下载/':
            os.startfile(os.getcwd() + '/B站下载/')
        else:
            os.startfile(str(self.ui.label_5.text()))

    def check(self):
        if self.ui.tableWidget.rowCount() != 0:
            for i in range(0, self.ui.tableWidget.rowCount()):
                self.ui.tableWidget.item(i, 0).setCheckState(self.ui.checkBox.checkState())

    def start_down(self):  # 开始下载的函数，用了线程池。可以控制同时下载几个
        self.pool.setMaxThreadCount(int(self.ui.comboBox.currentText()))

        if self.ui.tableWidget.rowCount() == 0:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '请先搜索歌曲！')
            msg_box.exec_()
        else:
            if not os.path.exists(self.ui.label_5.text()):
                os.mkdir(self.ui.label_5.text())
            row = self.ui.tableWidget.rowCount()

            for num in range(0, row):
                if self.ui.tableWidget.item(num, 0).checkState() == 2:
                    down_url = self.ui.lineEdit_2.text().split('?')[0] + '?p=' + str(num + 1)
                    print(down_url)
                    viedio_name = self.ui.label_5.text() + '/' + self.ui.tableWidget.item(num, 0).text()
                    self.backend = BackendThread(down_url, viedio_name, num)
                    self.backend.signal.updata_data.connect(self.text_write)
                    self.backend.signal.updata_data2.connect(self.text_write2)
                    self.pool.start(self.backend)
                    QApplication.processEvents()

    def text_write2(self, word, cont):  # 用一个字符串跟行数来表示音视频的合并状态
        new_item1 = QTableWidgetItem(word)
        new_item1.setTextAlignment(QtCore.Qt.AlignCenter)

        self.ui.tableWidget.setItem(cont, 3, QTableWidgetItem(new_item1))

    def text_write(self, word):  # 用一个列表来接收信息显示进度条状态，1值进度条值，2进度条的列数，3进度条的行
        if word[0] == 0:

            banber = QProgressBar(self)
            self.ui.tableWidget.setCellWidget(word[2], word[1], banber)

        else:

            self.ui.tableWidget.cellWidget(word[2], word[1]).setValue(word[0])

    def start_find(self):  # 根据链接搜索
        if self.ui.lineEdit_2.text() == '':
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '请先输入要解析的地址')
            msg_box.exec_()
        else:
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setColumnCount(4)

            self.ui.tableWidget.setColumnWidth(0, 250)
            self.ui.tableWidget.setColumnWidth(1, 250)
            self.ui.tableWidget.setColumnWidth(2, 250)
            self.ui.tableWidget.setColumnWidth(3, 250)

            self.ui.tableWidget.setHorizontalHeaderLabels(['视频名', '视频下载状态', '音频下载状态', '音视合并状态'])
            page_url = self.ui.lineEdit_2.text().split('?')[0]

            header = {"User-Agent": random_user(), "referer": "https://message.bilibili.com/"}
            try:
                reponse = requests.get(page_url, headers=header)
                if reponse.status_code == 200:

                    json_data = re.findall(r'"no_cache":false,"pages":(.*?),"subtitle"', reponse.text)[0]
                    json_data = json.loads(json_data)
                    self.ui.tableWidget.setRowCount(len(json_data))
                    for i in range(len(json_data)):
                        # page = json_data[i]["page"]
                        title1 = json_data[i]["part"]
                        pattern = re.compile(r"[\/\\\:\*\?\"\<\>\|\&\ \/]")
                        title = re.sub(pattern, "", title1)
                        new_item1 = QTableWidgetItem(title)
                        new_item1.setTextAlignment(QtCore.Qt.AlignCenter)

                        self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(new_item1))
                        self.ui.tableWidget.item(i, 0).setCheckState(0)
                    QApplication.processEvents()
            except:
                msg_box = QMessageBox(QMessageBox.Warning, '警告', '请输入正确的网址！')
                msg_box.exec_()

    def page_find(self):  # 调用浏览器打开B站的关键词搜索结果网页
        if self.ui.lineEdit.text() != '':
            url = 'https://search.bilibili.com/all?keyword=' + self.ui.lineEdit.text()
        else:
            url = 'https://www.bilibili.com/'
        webbrowser.open(url, new=0, autoraise=True)

    def change_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, '选择文件夹', '/')
        if dir_ != '':
            self.ui.label_5.setText(dir_)
        else:
            self.ui.label_5.setText('./B站下载/')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = firstfrom()
    screen = QDesktopWidget().screenGeometry()
    size = w.geometry()
    w.setWindowTitle('B站下载器')
    left = (screen.width() - size.width()) / 2
    hight = (screen.height() - size.height()) / 2
    w.move(left, hight)
    w.show()
    sys.exit(app.exec_())
