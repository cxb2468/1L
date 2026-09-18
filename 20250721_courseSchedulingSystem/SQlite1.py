import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *


# 初始化
def initializeModel(model):
    model.setTable('people')
    # 当字段变化时会触发一些事件
    model.setEditStrategy(QSqlTableModel.OnFieldChange)
    # 将整个数据装载到model中
    model.select()
    # 设置字段头
    model.setHeaderData(0, Qt.Horizontal, 'ID')
    model.setHeaderData(1, Qt.Horizontal, '姓名')
    model.setHeaderData(2, Qt.Horizontal, '地址')


# 创建视图
def createView(title, model):
    view = QTableView()
    view.setModel(model)
    view.setWindowTitle(title)
    return view


def findrow(i):
    # 当前选中的行
    delrow = i.row()
    print('del row=%s' % str(delrow))


def addrow():
    # 不是在QTableView上添加，而是在模型上添加,会自动将数据保存到数据库中！
    # 参数一：数据库共有几行数据  参数二：添加几行
    ret = model.insertRows(model.rowCount(), 1)  # 返回是否插入
    print('数据库共有%d行数据' % model.rowCount())
    print('insertRow=%s' % str(ret))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('./db/muttonDB.db')
    model = QSqlTableModel()  # MVC模式中的模型
    delrow = -1
    # 初始化将数据装载到模型当中
    initializeModel(model)
    view = createView("展示数据", model)
    view.clicked.connect(findrow)

    dlg = QDialog()
    layout = QVBoxLayout()
    layout.addWidget(view)
    addBtn = QPushButton('添加一行')
    addBtn.clicked.connect(addrow)

    delBtn = QPushButton('删除一行')
    delBtn.clicked.connect(lambda: model.removeRow(view.currentIndex().row()))

    layout.addWidget(view)
    layout.addWidget(addBtn)
    layout.addWidget(delBtn)
    dlg.setLayout(layout)
    dlg.setWindowTitle("Database Demo")
    dlg.resize(500, 400)
    dlg.show()
    sys.exit(app.exec())
