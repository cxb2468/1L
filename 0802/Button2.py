import sys
from PyQt5.QtWidgets import  QApplication,QWidget,QPushButton

class Button2(QWidget):
    def __init__(self):
        super(Button2,self).__init__()
        self.resize(300,300)
        self.setWindowTitle('Button2')
        self.button = QPushButton('start',self)
        self.button.clicked.connect(self.changeText)
        self.button.clicked.connect(self.changeSize)
        self.button.clicked.connect(self.changeTitle)

    def changeText(self):
        print('change text')
        self.button.setText('stop')
        self.button.clicked.disconnect(self.changeText)

    def changeSize(self):
        print('change size')
        self.resize(500,500)
        self.button.clicked.disconnect(self.changeSize)

    def changeTitle(self):
        print("change title")
        self.setWindowTitle('windown title change')
        self.button.clicked.disconnect(self.changeTitle)

if __name__ == '__main__':
    q_application = QApplication(sys.argv)
    button_ = Button2()
    button_.show()
    sys.exit(q_application.exec_())

    # def __init__(self):
    #     super(Button2,self).__init__()
    #     self.button = QPushButton('start',self)
    #     self.button.pressed.connect(self.button.released)
    #     self.button.released.connect(self.changeText)
    #
    # def changeText(self):
    #     if self.button.text() == 'start':
    #         self.button.setText('stop')
    #     else:
    #         self.button.setText('start')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    button2 = Button2()
    button2.show()
    sys.exit(app.exec_())

