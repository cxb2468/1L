import sys
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton
from PyQt5.QtCore import QCoreApplication


class close(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        btn = QPushButton("Close",self)
        btn.clicked.connect(QCoreApplication.instance().quit)

        btn.resize(btn.sizeHint())
        btn.move(50,50)

        self.setGeometry(300,300,250,150)
        self.setWindowTitle("Close")
        self.show()


if __name__ =="__main__":
    app = QApplication(sys.argv)
    c = close()
    sys.exit(app.exec_())
