import sys
from PyQt5.QtWidgets  import QApplication,QLabel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = QLabel('<font color="red">Hello</font>  <h1>World</h1>')

    label.show()
    sys.exit(app.exec_())