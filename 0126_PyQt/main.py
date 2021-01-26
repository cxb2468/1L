import sys
from PyQt5.QtWidgets import QApplication,QMainWindow

import my
import conversion
from functools import partial
def click_success():
    print("点击成功！！！")


def convert(ui):
    input = ui.lineEdit_USD.text()
    result = float(input) * 6.7
    ui.lineEdit_CNY.setText(str(result))
    print(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    # ui = my.Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    # ui.pushButton.clicked.connect(click_success)
    # sys.exit(app.exec_())
    ui = conversion.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.pushButton.clicked.connect(partial(convert,ui))


    sys.exit(app.exec_())

