import sys
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow
import equation
import math
from functools import partial


def jie(ui):
    a = ui.lineEdit_a.text()
    b = ui.lineEdit_b.text()
    c = ui.lineEdit_c.text()
    print(a+" "+b+" "+c)
    a = int(a)
    b = int(b)
    c = int(c)
    sanJiao = int(b*b - 4*a*c)


    if (a.strip() == '' or b.strip() == '' or c.strip() == ''  ):
        print("请填入abc的值，没有请填0")

    elif a==0:
        print("a=0 不是二次方程")

    elif sanJiao < 0:
        x1 = "无实数根"
        ui.lineEdit_x1.setText(str(x1))
        x2 = "无实数根"
        ui.lineEdit_x2.setText(str(x2))
    else:
        x1 = (-b + math.sqrt(b*b - 4*a*c)) / (2*a)
        x2 = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
        ui.lineEdit_x1.setText(str(x1))
        ui.lineEdit_x2.setText(str(x2))
        print(str(x1) +" "+str(x2))



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
    ui = equation.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.pushButton_jie.clicked.connect(partial(jie,ui))
    sys.exit(app.exec_())






