
from PyQt5.QtWidgets import  QApplication,QMainWindow,QMessageBox
from PyQt5.QtCore import Qt
from guess import Ui_Form
import random,math,sys



class myMain (QMainWindow,Ui_Form):
    #生产随机数的右界
    num = [i* 100 for i in range(1,20)]

    def __init__(self, parent=None):
        super(myMain, self).__init__(parent)
        self.setupUi(self)


        self.guessNum()
        # self.randomNum()
        self.intiUi()





    def guessNum(self):
        text = self.lineEdit_num.text()
        self.guessNum = float(text)


    def intiUi(self):
        self.label_1.setText("数值范围是：1-1000")

        self.pushButton_confirm.clicked.connect(self.guess)
        self.pushButton_exit.clicked.connect(app.quit)
        self.pushButton_restart.clicked.connect(self.reset)

    def guess(self):
        text = self.lineEdit_num.text()

        try:
            text = float(text)
        except:
            self.label.setText("   输入不合法")

            # self.label_1.setText("数值范围：{}-{}".format(self.left,self.right))
            self.lineEdit_num.clear()
            text = ""

        if text:
            num = math.floor(text)
            if self.guessNum == num:
                self.label.setText("猜中了 ！！！")
                # QMessageBox.question(self,"猜中了:{}!!!".format(self.guessNum),QMessageBox.Yes)
                # self.reset()

            elif self.guessNum >num:
                # if num >self.left:
                #     self.left = num
                #
                # # self.label_1.setText("数值范围：{}-{}".format(self.left, self.right))
                self.label.setText("猜大了")

            elif self.guessNum < num:
                # if num < self.right:
                #     self.right = num
                #
                # # self.label_1.setText("数值范围：{}-{}".format(self.left, self.right))
                self.label.setText("猜小了")

            self.lineEdit_num.clear()

    def reset(self):
        self.guessRange=None
        self.guessNum = None
        self.left = None
        self.right = None
        # self.randomNum()
        self.label_1.setText("")
        self.intiUi()


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter:
            self.guess()
        elif e.key() == Qt.Key_Escape:
            app.quit()
        elif e.key() == Qt.Key_R:
            self.reset()






if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = myMain()
    main.show()
    sys.exit(app.exec_())


