import sys
from PyQt5.QtWidgets import QApplication,QWidget,QToolTip,QPushButton
from PyQt5.QtGui import QFont

class Prompt(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        QToolTip.setFont(QFont("SansSerif",10))

        self.setToolTip("This is a <b>QWidget</b>  widget")

        btn = QPushButton("Button",self)
        btn.setToolTip("This is a <b>QPushButton</b>  widget")
        btn.resize(btn.sizeHint())
        btn.move(50,50)

        self.setGeometry(300,300,300,300)
        self.setWindowTitle("tooltips")
        self.show()

if __name__  == "__main__":
    app = QApplication(sys.argv)
    p = Prompt()
    sys.exit(app.exec_())
