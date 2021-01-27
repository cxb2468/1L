import sys
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow
from cal import Ui_MainWindow

from functools import partial

class myWindow(QWidget,Ui_MainWindow):
    def __init__(self):
        super(myWindow,self).__init__()
        self.setupUi(self)

    #定义 按键 事件

    def backspace(self):
        self.lineEdit_input.backspace()


    #0-9
    def bt1(self):
        self.lineEdit_input.insert("1")
    def bt2(self):
        self.lineEdit_input.insert("2")
    def bt3(self):
        self.lineEdit_input.insert("3")
    def bt4(self):
        self.lineEdit_input.insert("4")
    def bt5(self):
        self.lineEdit_input.insert("5")
    def bt6(self):
        self.lineEdit_input.insert("6")
    def bt7(self):
        self.lineEdit_input.insert("7")
    def bt8(self):
        self.lineEdit_input.insert("8")
    def bt9(self):
        self.lineEdit_input.insert("9")
    def bt0(self):
        self.lineEdit_input.insert("0")

    #运算符 +-*/
    def btAdd(self):
        self.lineEdit_input.insert("+")
    def btMin(self):
        self.lineEdit_input.insert("-")
    def btMul(self):
        self.lineEdit_input.insert("*")
    def btDivid(self):
        self.lineEdit_input.insert("/")

    #按键 =
    def btEqual(self):
        text  =  self.lineEdit_input.text()
        self.textBrowser.append('%s= %.2f' % (text,eval(text)))
        self.CE()

    #按键 .
    def btPoint(self):
        self.lineEdit_input.insert(".")
    #按键CE
    def CE(self):
         self.lineEdit_input.clear()

    #按键 清除缓存
    def QCHC(self):
        self.textBrowser.clear()


if __name__  == '__main__':

    app = QApplication(sys.argv)
    cal = myWindow()

    cal.pushButton_CE.clicked.connect(lambda:cal.backspace())
    #0-9
    cal.pushButton_0.clicked.connect(lambda:cal.bt0())
    cal.pushButton_1.clicked.connect(lambda:cal.bt1())
    cal.pushButton_2.clicked.connect(lambda:cal.bt2())
    cal.pushButton_3.clicked.connect(lambda:cal.bt3())
    cal.pushButton_4.clicked.connect(lambda:cal.bt4())
    cal.pushButton_5.clicked.connect(lambda:cal.bt5())
    cal.pushButton_6.clicked.connect(lambda:cal.bt6())
    cal.pushButton_7.clicked.connect(lambda:cal.bt7())
    cal.pushButton_8.clicked.connect(lambda:cal.bt8())
    cal.pushButton_9.clicked.connect(lambda:cal.bt9())

    # +-*/
    cal.pushButton_add.clicked.connect(lambda:cal.btAdd())
    cal.pushButton_minus.clicked.connect(lambda:cal.btMin())
    cal.pushButton_mul.clicked.connect(lambda:cal.btMul())
    cal.pushButton_divide.clicked.connect(lambda:cal.btDivid())

    # =
    cal.pushButton_equal.clicked.connect(lambda:cal.btEqual())
    #.
    cal.pushButton_point.clicked.connect(lambda:cal.btPoint())
    # 清空缓存

    cal.pushButton_QCHC.clicked.connect(lambda:cal.QCHC())

    cal.show()
    sys.exit(app.exec_())








