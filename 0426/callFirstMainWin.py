import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QMainWindow
from firstMainWin import *

class  MyMainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_pushButton_start_clicked(self):
        print('收益_min:',self.doubleSpinBox_min.text())
        print('收益_max',self.doubleSpinBox_max.text())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())


