import sys
import math
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.num = ''

    def init_ui(self):
        self.setWindowTitle("计算器")
        self.setWindowIcon(QIcon('笑脸.png'))
        self.setFixedSize(328, 400)
        self.setStyleSheet('background-color: white;')

        data = {
            0: ['%', 'CE', 'C', '<-'],
            1: ['1/x', 'x^2', '2√x', '÷'],
            2: ['7', '8', '9', '×'],
            3: ['4', '5', '6', '-'],
            4: ['1', '2', '3', '+'],
            5: ['±', '0', '.', '='],
        }

        layout = QVBoxLayout()

        self.text_count = QLabel('')
        self.text_count.setStyleSheet('font-family: SimHei;')
        layout.addWidget(self.text_count)

        self.text_reult = QLabel('0')
        self.text_reult.setAlignment(Qt.AlignRight)
        self.text_reult.setStyleSheet('font-size: 25px;font-family: SimHei;')
        layout.addWidget(self.text_reult)

        grid = QGridLayout()

        for line_number, line_data in data.items():
            for col_number, number in enumerate(line_data):
                self.btn = QPushButton(number)
                if number == '=':
                    self.btn.setStyleSheet('''
                                    width: 80px;
                                    height: 40px;
                                    background-color: red;
                                    font-family: SimHei;
                                    ''')
                elif number.isdigit() or number == '±' or number == '.':
                    self.btn.setStyleSheet('''
                                    width: 80px;
                                    height: 40px;
                                    background-color: #f0c9cf;
                                    font-family: SimHei;
                                    ''')
                else:
                    self.btn.setStyleSheet('''
                                    width: 80px;
                                    height: 40px;
                                    background-color: #63bbd0;
                                    font-family: SimHei;
                                    ''')
                self.btn.clicked.connect(self.Result)
                grid.addWidget(self.btn, line_number, col_number)

        layout.addLayout(grid)
        self.setLayout(layout)

    def Result(self):
        text = self.sender().text()
        if text.isdigit() or text == '.' or text in '+-×÷':
            self.num += text
            self.text_count.setText(self.num)
        elif text == '=':
            if '×' in self.num:
                self.num = self.num.replace('×', '*')
            elif '÷' in self.num:
                self.num = self.num.replace('÷', '/')
            self.text_reult.setText(str(eval(self.num)))
            self.num = str(eval(self.num))
        elif text == 'C':
            self.num = ''
            self.text_count.setText(self.num)
            self.text_reult.setText('0')
        elif text == '<-':
            self.num = self.num[:-1]
            self.text_count.setText(self.num)
        elif text == 'x^2':
            self.text_reult.setText(str(eval(self.num) * eval(self.num)))
            self.num = str(eval(self.num) * eval(self.num))
        elif text == '%':
            self.text_reult.setText(str(eval(self.num) / 100))
            self.num = str(eval(self.num) / 100)
        elif text == '1/x':
            self.text_reult.setText(str(1 / eval(self.num)))
            self.num = str(1 / eval(self.num))
        elif text == '2√x':
            self.text_reult.setText(str(math.sqrt(eval(self.num))))
            self.num = str(math.sqrt(eval(self.num)))
        elif text == '±':
            self.text_reult.setText(str(-eval(self.num)))
            self.num = str(-eval(self.num))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    app.exec()

