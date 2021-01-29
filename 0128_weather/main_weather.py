import sys
from PyQt5.QtWidgets import  QApplication,QMainWindow
from weather import Ui_Form
import requests


class MainWindow(QMainWindow):
    def __init__(self,parent = None):
        super(MainWindow,self).__init__(parent)
        self.ui =Ui_Form()
        self.ui.setupUi(self)

    def query(self):
        print("queryWeather ")
        cityName = self.ui.comboBox_w.currentText()
        cityCode = self.transCityName(cityName)

        rep = requests.get("http://www.weather.com.cn/data/sk/"+cityCode+".html")
        rep.encoding = "utf-8"
        print(rep.json())

        msg1 = "城市： "+ rep.json()["weatherinfo"]["city"]+"\n"
        # msg = "： " + rep.json()["weatherinfo"][""] + "\n"
        msg2 = "风向： " + rep.json()["weatherinfo"]["WD"] + "\n"
        msg3 = "温度： " + rep.json()["weatherinfo"]["temp"] + "\n"
        msg4 = "风力： " + rep.json()["weatherinfo"]["WS"] + "\n"
        msg5 = "湿度： " + rep.json()["weatherinfo"]["SD"] + "\n"
        result = msg1 + msg2 +msg3+msg4+msg5
        self.ui.textEdit_result.setText(result)

    def transCityName(self,cityName):
        cityCode = ""
        if cityName == "北京":
            cityCode = "101010100"
        elif cityName == "广州":
            cityCode = "101030100"
        elif cityName == "上海":
            cityCode = "101020100"

        return  cityCode

    def clear(self):
        print("clear")
        self.ui.textEdit_result.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
