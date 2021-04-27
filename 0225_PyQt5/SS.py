from PyQt5.QtWidgets import QPushButton,QApplication,QWidget
from PyQt5.QtWidgets import  QMessageBox
import sys

app = QApplication([])
w = QWidget()

def showMsg():
    QMessageBox.information(w,"信息提示框","OK,弹出测试信息")

btn = QPushButton("测试点击按钮",w)
btn.clicked.connect(showMsg)
w.show()
sys.exit(app.exec_())
