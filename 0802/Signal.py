import sys
from PyQt5.QtWidgets import QApplication,QWidget,QLabel
from PyQt5.QtCore import pyqtSignal

class Signal(QWidget):
    mySignal = pyqtSignal()

    def __init__(self):
        super(Signal,self).__init__()
        self.label = QLabel('Hello World', self)
        self.mySignal.connect(self.changeText)

    def changeText(self):
        if self.label.text() == 'Hello World':
            self.label.setText('Hello PyQt5')
        else:
            self.label.setText('Hello World')

    def mousePressEvent(self, QMouseEvent):
        self.mySignal.emit()

if __name__ == '__main__':
    q_application = QApplication(sys.argv)
    signal = Signal()
    signal.show()
    sys.exit(q_application.exec_())

