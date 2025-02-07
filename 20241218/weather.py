import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QDockWidget, QTreeWidgetItem, QLabel, QPushButton, \
    QTreeWidget, QWidget, QSystemTrayIcon, QMenu, QAction, QMessageBox, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
import requests
import json
import parsel


class RoundedWindow(QMainWindow):
    def __init__(self, main_widget=None, data=None):
        super().__init__()
        ####  基础设置
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无框
        # self.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明
        # self.setGeometry(600, 900, 900, 900)       # 设置几何
        self.resize(1000, 800)  # 设置几何尺寸
        self.setWindowTitle("设置标题")  # 设置标题
        ####  基础变量设置
        if main_widget is None:
            self.main_widget = QWidget(self)
        else:
            self.main_widget = main_widget  # 设置主区域控件,若是未传控件则新建一个
        self.icon_pic_path = r"favicon.ico"
        self.data = data
        ####  设置左侧边栏(停靠)
        self.left_dock = QDockWidget('目录栏', self)  # 设置停靠小部件
        self.tree_widget = QTreeWidget()  # 设置树型小部件
        self.left_dock.setWidget(self.tree_widget)  # 将树型小部件内嵌在停靠小部件上
        self.left_dock.setFloating(False)  # 设置停靠小部件不浮动
        self.tree_widget.setHeaderHidden(True)  # 设置树型隐藏表头,不去掉会有1
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)  # 添加停靠小部件(左侧) RightDockWidgetArea就是右侧
        # self.rootItem = QTreeWidgetItem()                     #创建树型部件的项对象,例如叫根节点
        # self.rootItem.setText(0, "根节点")                    # 给根节点设置标题
        # self.tree_widget.addTopLevelItem(self.rootItem)       # 树型部件增加根节点
        # self.childItem1 = QTreeWidgetItem()
        # self.childItem1.setText(0, "子节点1-key")             # 设置子节点名称,0显示名称,1不显示名称
        # self.childItem1.setCheckState(0, Qt.Unchecked)       # 设置复选框未选择
        # self.childItem1.setIcon(0, QIcon(self.icon_pic_path))        # 设置图标
        # self.rootItem.addChild(self.childItem1)
        # self.childItem2 = QTreeWidgetItem()
        # self.childItem2.setText(0, "子节点2-key")
        # self.childItem2.setText(1, "子节点2-value")
        # self.rootItem.addChild(self.childItem2)
        # QTreeWidget绑定信号
        # self.tree_widget.itemClicked.connect(self.on_treeWidget_itemClicked)
        self.handleTreeData()  # 构建树型部件数据
        res = self.tree_widget.itemClicked.connect(self.on_item_clicked)  # 树部件每一项点击事件

        #### 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)  # 创建系统图标对象
        self.tray_icon.setIcon(QIcon(self.icon_pic_path))  # 系统图标对象添加图标
        self.tray_icon.activated.connect(self.handleTrayIconActivated)  ## 处理托盘图标激活功能
        self.tray_menu = QMenu(self)  # 创建系统托盘图标,鼠标右键菜单对象,菜单对象
        exit_action = QAction("退出", self)  # 创建动作对象,取名'退出',没有任何功能
        exit_action.triggered.connect(QApplication.instance().quit)  # 将'退出'动作对象与真正退出功能绑定,即给动作添加退出功能
        self.tray_menu.addAction(exit_action)  # 菜单对象具有'退出'动作
        self.tray_icon.setContextMenu(self.tray_menu)  # 将系统图标对象与菜单对象绑定

        #### 创建主区域
        main_widget = QWidget(self)  # 创建主控件对象
        main__layout = QHBoxLayout()  # 创建布局对象
        main_widget.setLayout(main__layout)  # 将布局对象放入主控件对象中
        main__layout.addWidget(self.main_widget)  # 布局对象添加新的控件
        self.setCentralWidget(main_widget)  # 将主控件对象放置主区域
        # 主区域自定义区域

    ####  处理托盘图标激活
    def handleTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()  # 点击托盘图标恢复窗口显示

    ####  处理树型部件数据
    # 需要自己定义
    def handleTreeData(self):
        for first_value in self.data:
            root_name = ''
            if isinstance(first_value, dict):
                for key, value in first_value.items():
                    if isinstance(value, str):
                        root_name = value
                        break
                self.rootItem = QTreeWidgetItem()
                self.rootItem.setText(0, root_name)
                self.tree_widget.addTopLevelItem(self.rootItem)
                for key, value in first_value.items():
                    if isinstance(key, str):
                        self.childvalue_1 = QTreeWidgetItem()
                        self.childvalue_1.setText(0, key)
                        self.rootItem.addChild(self.childvalue_1)
                        if isinstance(value, str):
                            self.childvalue_2 = QTreeWidgetItem()
                            self.childvalue_2.setText(0, value)
                            self.childvalue_1.addChild(self.childvalue_2)
                        elif isinstance(value, dict) or isinstance(value, list):
                            for first_value in value:
                                if isinstance(first_value, dict):
                                    for key, value in first_value.items():
                                        if isinstance(value, str):
                                            root_name = value
                                            break
                                    for key, value in first_value.items():
                                        self.childvalue_2 = QTreeWidgetItem()
                                        self.childvalue_2.setText(0, root_name)
                                        self.childvalue_1.addChild(self.childvalue_2)
                                        break
                                    for key, value in first_value.items():
                                        self.childvalue_3 = QTreeWidgetItem()
                                        self.childvalue_3.setText(0, key)
                                        self.childvalue_2.addChild(self.childvalue_3)
                                        if isinstance(value, str):
                                            self.childvalue_4 = QTreeWidgetItem()
                                            self.childvalue_4.setText(0, value)
                                            self.childvalue_3.addChild(self.childvalue_4)
                                        elif isinstance(value, dict) or isinstance(value, list):
                                            for value_2 in value:
                                                if isinstance(value_2, dict):
                                                    for key, value in value_2.items():
                                                        if isinstance(value, str):
                                                            root_name = value
                                                            break
                                                    for key, value in value_2.items():
                                                        self.childvalue_4 = QTreeWidgetItem()
                                                        self.childvalue_4.setText(0, root_name)
                                                        self.childvalue_3.addChild(self.childvalue_4)
                                                        if isinstance(value_2, dict):
                                                            for key, value in value_2.items():
                                                                self.childvalue_5 = QTreeWidgetItem()
                                                                self.childvalue_5.setText(0, key)
                                                                self.childvalue_4.addChild(self.childvalue_5)
                                                                self.childvalue_6 = QTreeWidgetItem()
                                                                self.childvalue_6.setText(0, value)
                                                                self.childvalue_5.addChild(self.childvalue_6)
                                                            break
                                                else:
                                                    self.childvalue_4 = QTreeWidgetItem()
                                                    self.childvalue_4.setText(0, str(value_2))
                                                    self.childvalue_3.addChild(self.childvalue_4)
                                        else:
                                            self.childvalue_4 = QTreeWidgetItem()
                                            self.childvalue_4.setText(0, str(value))
                                            self.childvalue_3.addChild(self.childvalue_4)
                                else:
                                    self.childvalue_2 = QTreeWidgetItem()
                                    self.childvalue_2.setText(0, str(first_value))
                                    self.childvalue_1.addChild(self.childvalue_2)

            if not isinstance(self.data, list):
                if isinstance(self.data[first_value], str):
                    self.rootItem = QTreeWidgetItem()
                    self.rootItem.setText(0, first_value)
                    self.tree_widget.addTopLevelItem(self.rootItem)
                    self.childvalue_1 = QTreeWidgetItem()
                    self.childvalue_1.setText(0, self.data[first_value])
                    self.rootItem.addChild(self.childvalue_1)
                if isinstance(self.data[first_value], list):
                    for first_value_1 in self.data[first_value]:
                        if isinstance(first_value_1, dict):
                            self.rootItem = QTreeWidgetItem()
                            self.rootItem.setText(0, str(first_value))
                            self.tree_widget.addTopLevelItem(self.rootItem)
                            for key, value in first_value_1.items():
                                if isinstance(key, str):
                                    self.childvalue_1 = QTreeWidgetItem()
                                    self.childvalue_1.setText(0, key)
                                    self.rootItem.addChild(self.childvalue_1)
                                    if isinstance(value, str):
                                        self.childvalue_2 = QTreeWidgetItem()
                                        self.childvalue_2.setText(0, value)
                                        self.childvalue_1.addChild(self.childvalue_2)
                                    elif isinstance(value, dict) or isinstance(value, list):
                                        for first_value in value:
                                            if isinstance(first_value, dict):
                                                for key, value in first_value.items():
                                                    if isinstance(value, str):
                                                        root_name = value
                                                        break
                                                for key, value in first_value.items():
                                                    self.childvalue_2 = QTreeWidgetItem()
                                                    self.childvalue_2.setText(0, root_name)
                                                    self.childvalue_1.addChild(self.childvalue_2)
                                                    break
                                                for key, value in first_value.items():
                                                    self.childvalue_3 = QTreeWidgetItem()
                                                    self.childvalue_3.setText(0, key)
                                                    self.childvalue_2.addChild(self.childvalue_3)
                                                    if isinstance(value, str):
                                                        self.childvalue_4 = QTreeWidgetItem()
                                                        self.childvalue_4.setText(0, value)
                                                        self.childvalue_3.addChild(self.childvalue_4)
                                                    elif isinstance(value, dict) or isinstance(value, list):
                                                        for value_2 in value:
                                                            if isinstance(value_2, dict):
                                                                for key, value in value_2.items():
                                                                    if isinstance(value, str):
                                                                        root_name = value
                                                                        break
                                                                for key, value in value_2.items():
                                                                    self.childvalue_4 = QTreeWidgetItem()
                                                                    self.childvalue_4.setText(0, root_name)
                                                                    self.childvalue_3.addChild(self.childvalue_4)
                                                                    if isinstance(value_2, dict):
                                                                        for key, value in value_2.items():
                                                                            self.childvalue_5 = QTreeWidgetItem()
                                                                            self.childvalue_5.setText(0, key)
                                                                            self.childvalue_4.addChild(
                                                                                self.childvalue_5)
                                                                            self.childvalue_6 = QTreeWidgetItem()
                                                                            self.childvalue_6.setText(0, value)
                                                                            self.childvalue_5.addChild(
                                                                                self.childvalue_6)
                                                                        break
                                                            else:
                                                                self.childvalue_4 = QTreeWidgetItem()
                                                                self.childvalue_4.setText(0, str(value_2))
                                                                self.childvalue_3.addChild(self.childvalue_4)
                                                    else:
                                                        self.childvalue_4 = QTreeWidgetItem()
                                                        self.childvalue_4.setText(0, str(value))
                                                        self.childvalue_3.addChild(self.childvalue_4)
                                            else:
                                                self.childvalue_2 = QTreeWidgetItem()
                                                self.childvalue_2.setText(0, str(first_value))
                                                self.childvalue_1.addChild(self.childvalue_2)

    ####  树部件每一项点击事件
    # 需要自己定义
    def on_item_clicked(self, item, column):
        city_name = item.text(column)
        # 设置字体
        font = QFont()
        font.setFamily("Arial")  # 设置字体家族
        font.setPointSize(28)  # 设置字体大小
        self.main_widget.setFont(font)

        # 设置文本居中
        self.main_widget.setAlignment(Qt.AlignCenter)
        self.main_widget.setText(city_name)


if __name__ == '__main__':
    ###### 测试数据

    # 假设JSON数据存储在文件"data.json"中
    json_file_path = r'location.json'
    # 读取文件内容
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_string = file.read()
    # 将JSON字符串转换为Python对象
    data = json.loads(json_string)

    ###### Qt开始
    app = QApplication(sys.argv)  # 创建应用
    # 文本控件
    # main_widget = QTextEdit() #是否需要创建主区域控件,若要请将main_text填入RoundedWindow()括号内
    # 图片控件
    main_widget = QLabel()
    # main_widget.setPixmap(QPixmap(r'python\小说封面制作脚本\pic\笔名固定模版.png')) # 创建一个 QLabel 控件 设置 QLabel 控件的 pixmap，加载图片

    w = RoundedWindow(main_widget=main_widget, data=data)  # 创建自定义窗口
    w.show()  # 展示窗口
    # 调试：检查系统托盘是否可用
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "错误", "系统托盘不可用！")
        sys.exit(1)

    # 调试：检查图标是否加载成功
    if not w.tray_icon.isSystemTrayAvailable():
        QMessageBox.critical(None, "错误", "无法加载系统托盘图标！")
        sys.exit(1)

    w.tray_icon.show()  # 运行就展示图标
    app.exec_()  # 循环展示