import sys
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton

class Button(QWidget):
    def __init__(self):
        super(Button,self).__init__()
        self.button = QPushButton('Start',self)
        self.button.clicked.connect(self.change_text)

    def change_text(self):
        print('change text')
        self.button.setText('Stop')
        self.button.clicked.disconnect(self.change_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    button = Button()
    button.show()
    sys.exit(app.exec_())