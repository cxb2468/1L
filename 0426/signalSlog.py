# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'signalSlog.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(617, 511)
        self.pushButton_close = QtWidgets.QPushButton(Form)
        self.pushButton_close.setGeometry(QtCore.QRect(230, 220, 75, 23))
        self.pushButton_close.setObjectName("pushButton_close")

        self.retranslateUi(Form)
        self.pushButton_close.clicked.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_close.setText(_translate("Form", "关闭窗口"))