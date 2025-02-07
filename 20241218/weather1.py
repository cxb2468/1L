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

    ####  处理托盘图标激活
    def handleTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showNormal()  # 点击托盘图标恢复窗口显示

    ####  处理树型部件数据
    def handleTreeData(self):
        def add_items(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    child = QTreeWidgetItem(parent)
                    child.setText(0, key)
                    add_items(child, value)
            elif isinstance(data, list):
                for item in data:
                    add_items(parent, item)

        for province in self.data:
            if isinstance(province, dict):
                for province_name, cities in province.items():
                    root_item = QTreeWidgetItem(self.tree_widget)
                    root_item.setText(0, province_name)
                    add_items(root_item, cities)

    ####  树部件每一项点击事件
    def on_item_clicked(self, item, column):
        city_name = item.text(column)
        # 获取当前节点的所有父节点
        parent_names = []
        while item.parent():
            item = item.parent()
            parent_names.append(item.text(0))
        parent_names.reverse()

        # 构建完整的路径
        full_path = " -> ".join(parent_names + [city_name])

        # 设置字体
        font = QFont()
        font.setFamily("Arial")  # 设置字体家族
        font.setPointSize(28)  # 设置字体大小
        self.main_widget.setFont(font)

        # 设置文本居中
        self.main_widget.setAlignment(Qt.AlignCenter)
        self.main_widget.setText(full_path)


if __name__ == '__main__':
    ###### 测试数据
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
