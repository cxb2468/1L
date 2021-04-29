import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from signalSlog import Ui_Form



class Main(QMainWindow,Ui_Form):
    def __init__(self,parent = None):
        super(Main,self).__init__(parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
