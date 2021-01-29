import sys
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QMessageBox
import equation
import math

from functools import partial



def jie(ui):
    a = ui.lineEdit_a.text()
    b = ui.lineEdit_b.text()
    c = ui.lineEdit_c.text()
    if (a.strip()=="" or b.strip()=="" or c.strip()==""):
        print("请填入abc的值，没有请填0")
        text = "请填入abc的值，没有请填0"
        qw = QMessageBox()
        QMessageBox.information(qw, "消息框", text, QMessageBox.Yes)
        qw.setText(text)



    a = float(a)
    print(a)
    b = float(b)
    c = float(c)
    sanJiao = float(b*b - 4*a*c)
    print(sanJiao)

    if bool(int(a) == 0) :
         print("a=0 不是二次方程")
         # pyautogui.alert(text="a=0 不是二次方程", title="消息框")
         text = "a=0 不是二次方程"
         qw = QMessageBox()
         QMessageBox.information(qw,"消息框",text,QMessageBox.Yes)
         qw.setText(text)

    elif bool(int(sanJiao) < 0):
        x1 = "无实数根"
        x2 = "无实数根"
        print(x1)
        print(x2)
        ui.lineEdit_x1.setText(x1)
        ui.lineEdit_x2.setText(x2)
    else:
        sanJiao = math.sqrt(sanJiao)
        x1 =((-b) + sanJiao)/ (2*a)
        x2 =((-b) - sanJiao)/ (2*a)
        x1=round(x1,8)
        x2=round(x2,8)
        ui.lineEdit_x1.setText(str(x1))
        ui.lineEdit_x2.setText(str(x2))
        print(str(x1) +" "+str(x2))

def AC():
    ui.lineEdit_a.setText("")
    ui.lineEdit_b.setText("")
    ui.lineEdit_c.setText("")
    ui.lineEdit_x1.setText("")
    ui.lineEdit_x2.setText("")
    print("AC 成功!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()

    ui = equation.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.pushButton_jie.clicked.connect(partial(jie,ui))
    ui.pushButton_AC.clicked.connect(partial(AC))
    sys.exit(app.exec_())






