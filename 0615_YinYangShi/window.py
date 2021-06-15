from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2,time,random,os, datetime

import action
import chushihua
import sys




class Main_Win(QWidget):
    def __init__(self):
        super(Main_Win,self).__init__()
        self.Main_WinUI()
        self.cs = chushihua.chushihua()


    def Main_WinUI(self):
        self.setWindowTitle('阴阳师')
        self.resize(500,700)

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        newLeft = (screen.width() - size.width()) // 2
        newTop = (screen.height() - size.height()) // 2
        self.move(newLeft, newTop)

        self.setFixedSize(500,800)
        palette = QPalette()
        pix = QPixmap(os.getcwd() + "\\png2\\background.jpg")

        pix = pix.scaled(480, 780)
        palette.setBrush(QPalette.Background, QBrush(pix))
        self.setPalette(palette)
        self.setWindowOpacity(1)
        self.setToolTip('软件请勿由于违法！！！')
        self.setWindowIcon(QIcon(os.getcwd() + "\\png2\\favicon(1).ico"))
        QToolTip.setFont(QFont('Times',10,QFont.Black))


        self.Main_WinLayout()
        self.show()
    def Main_WinLayout(self):

        self.group = QGroupBox(self)
        self.group.setTitle('参数设置区:')
        self.group.setGeometry(10,10,485,200)

        self.layout = QGridLayout()
        self.button_one = QPushButton('御魂（单刷）',self)
        self.layout.addWidget(self.button_one, 0, 0)
        self.button_one.clicked.connect(self.dialoginfo)

        self.button_two = QPushButton('御魂（司机）', self)
        self.layout.addWidget(self.button_two, 0, 1)
        self.button_two.clicked.connect(self.dialoginfo_two)

        self.button_three = QPushButton('御魂（打手）', self)
        self.layout.addWidget(self.button_three, 1, 0)
        self.button_three.clicked.connect(self.dialoginfo_three)

        self.button_four = QPushButton('退出程序！', self)
        self.layout.addWidget(self.button_four, 1, 1)
        self.button_four.clicked.connect(self.dialoginfo_four)

        self.group.setLayout(self.layout)

        self.group_two = QGroupBox(self)
        self.group_two.setTitle('输出日志')
        self.group_two.setGeometry(10, 200, 485, 600)
        self.textedit_one = QTextEdit()
        self.textedit_one.setHtml('<font color=red>程序开始时间:<\\font>')##00FA9A
        self.textedit_one.moveCursor(QTextCursor.End)
        self.textedit_one.insertPlainText(str(datetime.datetime.now()) +"\n")
        self.textedit_one.moveCursor(QTextCursor.End)
        self.textedit_one.insertPlainText("使用方法:软件只能在模拟器打开，并将其拖到左上角\n模拟器的分辨率为:宽 = 1200,高 = 700,DPI = 240，不按规定使用，可能会引起错误异常闪退或者识别不了截屏！")

        self.layout_two = QGridLayout()
        self.textedit_one.setReadOnly(True)
        self.layout_two.addWidget(self.textedit_one)
        self.group_two.setLayout(self.layout_two)



    def dialoginfo(self):
        self.True_False = True
        self.True_False2 = False
        self.True_False3 = False
        reply=QMessageBox.question(win, '温馨提示！', '开始执行！', QMessageBox.Ok)
        action.alarm(1)
        self.cs.yuhun()
    def dialoginfo_two(self):
        self.True_False = False
        self.True_False2 = True
        self.True_False3 = False
        reply=QMessageBox.question(win, '温馨提示！', '开始执行！', QMessageBox.Ok)
        action.alarm(1)
        self.cs.yuhun2()
    def dialoginfo_three(self):
        self.True_False = False
        self.True_False2 = False
        self.True_False3 = True
        reply=QMessageBox.question(win, '温馨提示！', '开始执行！', QMessageBox.Ok)
        action.alarm(1)
        self.cs.yuhun3()
    def dialoginfo_four(self):
        sys.exit()
    def closeEvent(self, event):
        reply=QMessageBox.question(self,'Message','确定要退出吗?',QMessageBox.Yes,QMessageBox.No)
        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            reply = QMessageBox.question(win, '温馨提示！', '请想清楚！', QMessageBox.Ok)
            event.ignore()



if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = Main_Win()
    sys.exit(app.exec_())
