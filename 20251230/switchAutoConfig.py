import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLabel, QComboBox, QLineEdit, QTextEdit, QPushButton,
                             QScrollArea, QListWidget, QListWidgetItem, QDialog, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QMenu, QAction, QCheckBox, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator

class EditableTableWidget(QTableWidget):
    editRequested = pyqtSignal(int)  # 行号信号
    deleteRequested = pyqtSignal(int)  # 删除信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            row = self.rowAt(event.pos().y())
            if row >= 0:
                self.editRequested.emit(row)
        super().mouseDoubleClickEvent(event)

    def show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row >= 0:
            menu = QMenu()
            edit_action = QAction("编辑", self)
            edit_action.triggered.connect(lambda: self.editRequested.emit(row))
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self.deleteRequested.emit(row))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            menu.exec_(self.viewport().mapToGlobal(pos))

class SwitchConfigGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("交换机配置生成工具 v1.4")
        self.setGeometry(100, 100, 1200, 800)

        # 主布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        # 左侧配置区域
        self.config_area = QWidget()
        self.config_layout = QVBoxLayout(self.config_area)
        self.config_layout.setContentsMargins(5, 5, 5, 5)

        # 右侧预览区域
        self.preview_area = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_area)
        self.preview_layout.setContentsMargins(5, 5, 5, 5)

        # 添加左右区域到主布局
        self.main_layout.addWidget(self.config_area, 70)
        self.main_layout.addWidget(self.preview_area, 30)

        # 初始化UI组件
        self.init_tabs()
        self.init_preview()

        # 存储配置数据
        self.vlan_configs = []
        self.port_configs = []
        self.static_routes = []
        self.dhcp_pools = []
        self.ip_bindings = []
        self.combo_configs = []
        self.isolation_configs = []
        self.console_config = None

    def init_tabs(self):
        """初始化配置选项卡"""
        self.tab_widget = QTabWidget()
        self.config_layout.addWidget(self.tab_widget)

        # 基本配置选项卡
        self.basic_tab = QWidget()
        self.init_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "交换机基本配置")

        # 高级配置选项卡
        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "交换机高级配置")

        # 命令查询选项卡
        self.command_tab = QWidget()
        self.init_command_tab()
        self.tab_widget.addTab(self.command_tab, "配置命令查询")

    def init_basic_tab(self):
        """初始化基本配置选项卡"""
        layout = QVBoxLayout(self.basic_tab)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 1. 设备厂商选择
        vendor_group = QGroupBox("设备厂商选择")
        vendor_layout = QHBoxLayout()
        self.vendor_combo = QComboBox()
        self.vendor_combo.addItems(["华为", "华三", "思科", "锐捷"])
        vendor_layout.addWidget(QLabel("选择厂商:"))
        vendor_layout.addWidget(self.vendor_combo)
        vendor_group.setLayout(vendor_layout)
        scroll_layout.addWidget(vendor_group)

        # 2. 设备命名
        name_group = QGroupBox("设备命名")
        name_layout = QHBoxLayout()
        self.device_name = QLineEdit()
        self.device_name.setPlaceholderText("输入设备名称")
        name_layout.addWidget(QLabel("设备名称:"))
        name_layout.addWidget(self.device_name)

        # 添加关闭信息中心选项
        self.disable_info_center = QCheckBox("关闭信息中心提示")
        name_layout.addWidget(self.disable_info_center)
        name_group.setLayout(name_layout)
        scroll_layout.addWidget(name_group)

        # 3. VLAN配置
        vlan_group = QGroupBox("VLAN配置")
        vlan_layout = QVBoxLayout()

        # 批量创建VLAN
        batch_vlan_layout = QHBoxLayout()
        self.batch_vlan_input = QLineEdit()
        self.batch_vlan_input.setPlaceholderText("例如: 10 20 30 或 10 to 20")
        batch_vlan_layout.addWidget(QLabel("批量创建VLAN:"))
        batch_vlan_layout.addWidget(self.batch_vlan_input)
        vlan_layout.addLayout(batch_vlan_layout)

        # 添加VLAN按钮
        self.add_vlan_btn = QPushButton("添加VLAN配置")
        self.add_vlan_btn.clicked.connect(self.show_vlan_config_dialog)
        vlan_layout.addWidget(self.add_vlan_btn)

        # VLAN配置表格
        self.vlan_table = EditableTableWidget()
        self.vlan_table.setColumnCount(5)
        self.vlan_table.setHorizontalHeaderLabels(["VLAN ID", "VLAN名称", "描述", "IP地址", "子网掩码"])
        self.vlan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vlan_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vlan_table.editRequested.connect(self.edit_vlan_config)
        self.vlan_table.deleteRequested.connect(self.delete_vlan_config)
        vlan_layout.addWidget(QLabel("VLAN配置列表:"))
        vlan_layout.addWidget(self.vlan_table)

        vlan_group.setLayout(vlan_layout)
        scroll_layout.addWidget(vlan_group)

        # 4. 端口配置
        port_group = QGroupBox("端口配置")
        port_layout = QVBoxLayout()

        # 端口模式选择
        mode_layout = QHBoxLayout()
        self.port_mode_combo = QComboBox()
        self.port_mode_combo.addItems(["access", "trunk"])
        self.port_mode_combo.currentTextChanged.connect(self.update_port_mode_ui)
        mode_layout.addWidget(QLabel("端口模式:"))
        mode_layout.addWidget(self.port_mode_combo)
        port_layout.addLayout(mode_layout)

        # 端口类型和范围 - 优化后的形式
        port_type_layout = QHBoxLayout()

        # 端口类型选择
        self.port_type_combo = QComboBox()
        self.port_type_combo.addItems(["GigabitEthernet", "Ethernet", "XGigabitEthernet", "FastEthernet"])
        self.port_type_combo.setCurrentText("GigabitEthernet")

        # 端口范围输入
        self.port_range_edit = QLineEdit()
        self.port_range_edit.setPlaceholderText("例如: 0/0/1-24 或 0/0/1,3,5")

        port_type_layout.addWidget(QLabel("端口类型:"))
        port_type_layout.addWidget(self.port_type_combo)
        port_type_layout.addWidget(QLabel("端口范围:"))
        port_type_layout.addWidget(self.port_range_edit)
        port_layout.addLayout(port_type_layout)

        # VLAN配置
        self.vlan_config_layout = QHBoxLayout()
        self.access_vlan_combo = QComboBox()
        self.access_vlan_combo.setEnabled(False)
        self.trunk_vlans_edit = QLineEdit()
        self.trunk_vlans_edit.setPlaceholderText("例如: 10,20,30 或 all")
        self.trunk_vlans_edit.setEnabled(False)

        self.vlan_config_layout.addWidget(QLabel("Access VLAN:"))
        self.vlan_config_layout.addWidget(self.access_vlan_combo)
        self.vlan_config_layout.addWidget(QLabel("Trunk VLANs:"))
        self.vlan_config_layout.addWidget(self.trunk_vlans_edit)
        port_layout.addLayout(self.vlan_config_layout)

        # 添加端口按钮
        self.add_port_btn = QPushButton("添加端口配置")
        self.add_port_btn.clicked.connect(self.add_port_config)
        port_layout.addWidget(self.add_port_btn)

        # 端口配置表格
        self.port_table = EditableTableWidget()
        self.port_table.setColumnCount(4)
        self.port_table.setHorizontalHeaderLabels(["端口类型", "端口范围", "模式", "VLAN配置"])
        self.port_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.port_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.port_table.editRequested.connect(self.edit_port_config)
        self.port_table.deleteRequested.connect(self.delete_port_config)
        port_layout.addWidget(QLabel("端口配置列表:"))
        port_layout.addWidget(self.port_table)

        port_group.setLayout(port_layout)
        scroll_layout.addWidget(port_group)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 生成配置按钮
        self.generate_btn = QPushButton("生成配置")
        self.generate_btn.clicked.connect(self.generate_config)
        button_layout.addWidget(self.generate_btn)

        # 清除所有配置按钮
        self.clear_all_btn = QPushButton("清除所有配置")
        self.clear_all_btn.clicked.connect(self.clear_all_configs)
        button_layout.addWidget(self.clear_all_btn)

        scroll_layout.addLayout(button_layout)

        # 设置滚动区域内容
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def init_advanced_tab(self):
        """初始化高级配置选项卡"""
        layout = QVBoxLayout(self.advanced_tab)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 1. 光电复用配置
        combo_group = QGroupBox("光电复用配置")
        combo_layout = QVBoxLayout()

        # 光电复用选项
        self.combo_enable = QCheckBox("启用光电复用(Combo)")
        self.combo_enable.stateChanged.connect(self.update_combo_ui)
        combo_layout.addWidget(self.combo_enable)

        # 光电选择
        combo_mode_layout = QHBoxLayout()
        combo_mode_layout.addWidget(QLabel("选择光电模式:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["电口(网线)", "光口(光纤)"])
        self.combo_mode.setEnabled(False)
        combo_mode_layout.addWidget(self.combo_mode)
        combo_layout.addLayout(combo_mode_layout)

        # 接口范围
        combo_port_layout = QHBoxLayout()
        combo_port_layout.addWidget(QLabel("接口范围:"))
        self.combo_port_range = QLineEdit()
        self.combo_port_range.setPlaceholderText("例如: 0/0/1-4,0/0/10")
        self.combo_port_range.setEnabled(False)
        combo_port_layout.addWidget(self.combo_port_range)
        combo_layout.addLayout(combo_port_layout)

        # 添加配置按钮
        self.add_combo_btn = QPushButton("添加光电复用配置")
        self.add_combo_btn.setEnabled(False)
        self.add_combo_btn.clicked.connect(self.add_combo_config)
        combo_layout.addWidget(self.add_combo_btn)

        # 光电复用配置表格
        self.combo_table = EditableTableWidget()
        self.combo_table.setColumnCount(3)
        self.combo_table.setHorizontalHeaderLabels(["接口范围", "模式", "状态"])
        self.combo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.combo_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.combo_table.editRequested.connect(self.edit_combo_config)
        self.combo_table.deleteRequested.connect(self.delete_combo_config)
        combo_layout.addWidget(QLabel("光电复用配置列表:"))
        combo_layout.addWidget(self.combo_table)

        combo_group.setLayout(combo_layout)
        scroll_layout.addWidget(combo_group)

        # 2. 端口隔离配置
        isolation_group = QGroupBox("端口隔离配置")
        isolation_layout = QVBoxLayout()

        # 隔离组编号
        isolation_id_layout = QHBoxLayout()
        isolation_id_layout.addWidget(QLabel("隔离组编号:"))
        self.isolation_id = QLineEdit()
        self.isolation_id.setPlaceholderText("例如: 1")
        isolation_id_layout.addWidget(self.isolation_id)
        isolation_layout.addLayout(isolation_id_layout)

        # 隔离模式
        isolation_mode_layout = QHBoxLayout()
        isolation_mode_layout.addWidget(QLabel("隔离模式:"))
        self.isolation_mode = QComboBox()
        self.isolation_mode.addItems(["二层隔离", "二三层隔离"])
        isolation_mode_layout.addWidget(self.isolation_mode)
        isolation_layout.addLayout(isolation_mode_layout)

        # 隔离端口范围
        isolation_port_layout = QHBoxLayout()
        isolation_port_layout.addWidget(QLabel("隔离端口范围:"))
        self.isolation_port_range = QLineEdit()
        self.isolation_port_range.setPlaceholderText("例如: 0/0/1-10,0/0/20")
        isolation_port_layout.addWidget(self.isolation_port_range)
        isolation_layout.addLayout(isolation_port_layout)

        # 添加隔离配置按钮
        self.add_isolation_btn = QPushButton("添加端口隔离配置")
        self.add_isolation_btn.clicked.connect(self.add_isolation_config)
        isolation_layout.addWidget(self.add_isolation_btn)

        # 端口隔离配置表格
        self.isolation_table = EditableTableWidget()
        self.isolation_table.setColumnCount(3)
        self.isolation_table.setHorizontalHeaderLabels(["隔离组", "模式", "端口范围"])
        self.isolation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.isolation_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.isolation_table.editRequested.connect(self.edit_isolation_config)
        self.isolation_table.deleteRequested.connect(self.delete_isolation_config)
        isolation_layout.addWidget(QLabel("端口隔离配置列表:"))
        isolation_layout.addWidget(self.isolation_table)

        isolation_group.setLayout(isolation_layout)
        scroll_layout.addWidget(isolation_group)

        # 3. Console密码配置
        console_group = QGroupBox("Console密码配置")
        console_layout = QVBoxLayout()

        # 启用Console密码
        self.console_enable = QCheckBox("启用Console密码")
        self.console_enable.stateChanged.connect(self.update_console_ui)
        console_layout.addWidget(self.console_enable)

        # 认证模式
        console_auth_layout = QHBoxLayout()
        console_auth_layout.addWidget(QLabel("认证模式:"))
        self.console_auth_mode = QComboBox()
        self.console_auth_mode.addItems(["仅密码", "用户名+密码"])
        self.console_auth_mode.setEnabled(False)
        console_auth_layout.addWidget(self.console_auth_mode)
        console_layout.addLayout(console_auth_layout)

        # 用户名
        console_user_layout = QHBoxLayout()
        console_user_layout.addWidget(QLabel("用户名:"))
        self.console_username = QLineEdit()
        self.console_username.setPlaceholderText("输入用户名")
        self.console_username.setEnabled(False)
        console_user_layout.addWidget(self.console_username)
        console_layout.addLayout(console_user_layout)

        # 密码
        console_pass_layout = QHBoxLayout()
        console_pass_layout.addWidget(QLabel("密码:"))
        self.console_password = QLineEdit()
        self.console_password.setPlaceholderText("输入密码")
        self.console_password.setEchoMode(QLineEdit.Password)
        self.console_password.setEnabled(False)
        console_pass_layout.addWidget(self.console_password)
        console_layout.addLayout(console_pass_layout)

        # 确认密码
        console_confirm_layout = QHBoxLayout()
        console_confirm_layout.addWidget(QLabel("确认密码:"))
        self.console_confirm = QLineEdit()
        self.console_confirm.setPlaceholderText("再次输入密码")
        self.console_confirm.setEchoMode(QLineEdit.Password)
        self.console_confirm.setEnabled(False)
        console_confirm_layout.addWidget(self.console_confirm)
        console_layout.addLayout(console_confirm_layout)

        # 添加Console配置按钮
        self.add_console_btn = QPushButton("添加Console密码配置")
        self.add_console_btn.setEnabled(False)
        self.add_console_btn.clicked.connect(self.add_console_config)
        console_layout.addWidget(self.add_console_btn)

        console_group.setLayout(console_layout)
        scroll_layout.addWidget(console_group)

        # 4. 静态路由配置
        route_group = QGroupBox("静态路由配置")
        route_layout = QVBoxLayout()

        # 静态路由表单
        route_form_layout = QHBoxLayout()

        # 目标网络
        route_form_layout.addWidget(QLabel("目标网络:"))
        self.dest_network = QLineEdit()
        self.dest_network.setPlaceholderText("例如: 192.168.1.0")
        route_form_layout.addWidget(self.dest_network)

        # 子网掩码
        route_form_layout.addWidget(QLabel("子网掩码:"))
        self.dest_mask = QLineEdit()
        self.dest_mask.setPlaceholderText("例如: 255.255.255.0")
        route_form_layout.addWidget(self.dest_mask)

        # 下一跳
        route_form_layout.addWidget(QLabel("下一跳:"))
        self.next_hop = QLineEdit()
        self.next_hop.setPlaceholderText("例如: 192.168.1.1")
        route_form_layout.addWidget(self.next_hop)

        # 优先级
        route_form_layout.addWidget(QLabel("优先级:"))
        self.route_priority = QLineEdit()
        self.route_priority.setPlaceholderText("可选，默认60")
        self.route_priority.setValidator(QIntValidator(1, 255))
        route_form_layout.addWidget(self.route_priority)

        route_layout.addLayout(route_form_layout)

        # 添加路由按钮
        self.add_route_btn = QPushButton("添加静态路由")
        self.add_route_btn.clicked.connect(self.add_static_route)
        route_layout.addWidget(self.add_route_btn)

        # 路由配置表格
        self.route_table = EditableTableWidget()
        self.route_table.setColumnCount(4)
        self.route_table.setHorizontalHeaderLabels(["目标网络", "子网掩码", "下一跳", "优先级"])
        self.route_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.route_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.route_table.editRequested.connect(self.edit_static_route)
        self.route_table.deleteRequested.connect(self.delete_static_route)
        route_layout.addWidget(QLabel("静态路由列表:"))
        route_layout.addWidget(self.route_table)

        route_group.setLayout(route_layout)
        scroll_layout.addWidget(route_group)

        # 5. DHCP配置
        dhcp_group = QGroupBox("DHCP配置")
        dhcp_layout = QVBoxLayout()

        # DHCP表单
        dhcp_form_layout = QGridLayout()

        # Pool名称
        dhcp_form_layout.addWidget(QLabel("Pool名称:"), 0, 0)
        self.dhcp_pool_name = QLineEdit()
        self.dhcp_pool_name.setPlaceholderText("例如: VLAN10_POOL")
        dhcp_form_layout.addWidget(self.dhcp_pool_name, 0, 1)

        # 网关
        dhcp_form_layout.addWidget(QLabel("网关:"), 1, 0)
        self.dhcp_gateway = QLineEdit()
        self.dhcp_gateway.setPlaceholderText("例如: 192.168.1.1")
        dhcp_form_layout.addWidget(self.dhcp_gateway, 1, 1)

        # 网段
        dhcp_form_layout.addWidget(QLabel("网段:"), 2, 0)
        self.dhcp_network = QLineEdit()
        self.dhcp_network.setPlaceholderText("例如: 192.168.1.0")
        dhcp_form_layout.addWidget(self.dhcp_network, 2, 1)

        # 掩码
        dhcp_form_layout.addWidget(QLabel("掩码:"), 3, 0)
        self.dhcp_mask = QLineEdit()
        self.dhcp_mask.setPlaceholderText("例如: 255.255.255.0")
        dhcp_form_layout.addWidget(self.dhcp_mask, 3, 1)

        # DNS1
        dhcp_form_layout.addWidget(QLabel("DNS1:"), 0, 2)
        self.dhcp_dns1 = QLineEdit()
        self.dhcp_dns1.setPlaceholderText("例如: 8.8.8.8")
        dhcp_form_layout.addWidget(self.dhcp_dns1, 0, 3)

        # DNS2
        dhcp_form_layout.addWidget(QLabel("DNS2:"), 1, 2)
        self.dhcp_dns2 = QLineEdit()
        self.dhcp_dns2.setPlaceholderText("例如: 8.8.4.4")
        dhcp_form_layout.addWidget(self.dhcp_dns2, 1, 3)

        # 地址池范围
        dhcp_form_layout.addWidget(QLabel("地址池范围:"), 2, 2)
        self.dhcp_range_start = QLineEdit()
        self.dhcp_range_start.setPlaceholderText("起始IP")
        dhcp_form_layout.addWidget(self.dhcp_range_start, 2, 3)

        dhcp_form_layout.addWidget(QLabel("到"), 3, 2)
        self.dhcp_range_end = QLineEdit()
        self.dhcp_range_end.setPlaceholderText("结束IP")
        dhcp_form_layout.addWidget(self.dhcp_range_end, 3, 3)

        # 接口调用
        dhcp_form_layout.addWidget(QLabel("接口调用:"), 4, 0)
        self.dhcp_interface_type = QComboBox()
        self.dhcp_interface_type.addItems(["VLAN接口", "物理接口"])
        dhcp_form_layout.addWidget(self.dhcp_interface_type, 4, 1)

        self.dhcp_interface_id = QLineEdit()
        self.dhcp_interface_id.setPlaceholderText("例如: 10 或 GigabitEthernet0/0/1")
        dhcp_form_layout.addWidget(self.dhcp_interface_id, 4, 2, 1, 2)

        dhcp_layout.addLayout(dhcp_form_layout)

        # 添加DHCP按钮
        self.add_dhcp_btn = QPushButton("添加DHCP Pool")
        self.add_dhcp_btn.clicked.connect(self.add_dhcp_pool)
        dhcp_layout.addWidget(self.add_dhcp_btn)

        # DHCP配置表格
        self.dhcp_table = EditableTableWidget()
        self.dhcp_table.setColumnCount(8)
        self.dhcp_table.setHorizontalHeaderLabels(["Pool名称", "网关", "网段", "掩码", "DNS1", "DNS2", "地址池范围", "接口调用"])
        self.dhcp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dhcp_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dhcp_table.editRequested.connect(self.edit_dhcp_pool)
        self.dhcp_table.deleteRequested.connect(self.delete_dhcp_pool)
        dhcp_layout.addWidget(QLabel("DHCP Pool列表:"))
        dhcp_layout.addWidget(self.dhcp_table)

        dhcp_group.setLayout(dhcp_layout)
        scroll_layout.addWidget(dhcp_group)

        # 6. IP端口绑定
        binding_group = QGroupBox("IP端口绑定")
        binding_layout = QVBoxLayout()

        # 绑定表单
        binding_form_layout = QHBoxLayout()

        # 接口选择
        binding_form_layout.addWidget(QLabel("接口:"))
        self.binding_interface = QComboBox()
        self.binding_interface.addItems(["GigabitEthernet", "Ethernet", "XGigabitEthernet", "FastEthernet"])
        binding_form_layout.addWidget(self.binding_interface)

        self.binding_interface_id = QLineEdit()
        self.binding_interface_id.setPlaceholderText("例如: 0/0/1")
        binding_form_layout.addWidget(self.binding_interface_id)

        # IP地址
        binding_form_layout.addWidget(QLabel("IP地址:"))
        self.binding_ip = QLineEdit()
        self.binding_ip.setPlaceholderText("例如: 192.168.1.100")
        binding_form_layout.addWidget(self.binding_ip)

        # MAC地址
        binding_form_layout.addWidget(QLabel("MAC地址:"))
        self.binding_mac = QLineEdit()
        self.binding_mac.setPlaceholderText("例如: 00-11-22-33-44-55")
        binding_form_layout.addWidget(self.binding_mac)

        binding_layout.addLayout(binding_form_layout)

        # 添加绑定按钮
        self.add_binding_btn = QPushButton("添加IP绑定")
        self.add_binding_btn.clicked.connect(self.add_ip_binding)
        binding_layout.addWidget(self.add_binding_btn)

        # 绑定配置表格
        self.binding_table = EditableTableWidget()
        self.binding_table.setColumnCount(3)
        self.binding_table.setHorizontalHeaderLabels(["接口", "IP地址", "MAC地址"])
        self.binding_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.binding_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.binding_table.editRequested.connect(self.edit_ip_binding)
        self.binding_table.deleteRequested.connect(self.delete_ip_binding)
        binding_layout.addWidget(QLabel("IP绑定列表:"))
        binding_layout.addWidget(self.binding_table)

        binding_group.setLayout(binding_layout)
        scroll_layout.addWidget(binding_group)

        # 设置滚动区域内容
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def update_combo_ui(self, state):
        """更新光电复用UI状态"""
        enabled = state == Qt.Checked
        self.combo_mode.setEnabled(enabled)
        self.combo_port_range.setEnabled(enabled)
        self.add_combo_btn.setEnabled(enabled)

    def update_console_ui(self, state):
        """更新Console密码UI状态"""
        enabled = state == Qt.Checked
        self.console_auth_mode.setEnabled(enabled)
        self.console_password.setEnabled(enabled)
        self.console_confirm.setEnabled(enabled)
        self.add_console_btn.setEnabled(enabled)

        # 根据认证模式更新用户名输入框状态
        if enabled:
            self.console_auth_mode.currentTextChanged.connect(self.update_console_auth_ui)
            self.update_console_auth_ui(self.console_auth_mode.currentText())

    def update_console_auth_ui(self, mode):
        """根据Console认证模式更新UI"""
        self.console_username.setEnabled(mode == "用户名+密码")

    def add_combo_config(self):
        """添加光电复用配置"""
        mode = self.combo_mode.currentText()
        port_range = self.combo_port_range.text().strip()

        if not port_range:
            QMessageBox.warning(self, "警告", "请输入接口范围!")
            return

        config = {
            "port_range": port_range,
            "mode": mode,
            "status": "已启用"
        }

        self.combo_configs.append(config)
        self.update_combo_table()

        # 清空输入框
        self.combo_port_range.clear()

    def edit_combo_config(self, row):
        """编辑光电复用配置"""
        if 0 <= row < len(self.combo_configs):
            config = self.combo_configs[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑光电复用配置")
            dialog.setFixedSize(400, 200)
            layout = QVBoxLayout(dialog)

            # 接口范围
            port_range_layout = QHBoxLayout()
            port_range_layout.addWidget(QLabel("接口范围:"))
            port_range_input = QLineEdit(config["port_range"])
            port_range_layout.addWidget(port_range_input)
            layout.addLayout(port_range_layout)

            # 光电模式
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("光电模式:"))
            mode_combo = QComboBox()
            mode_combo.addItems(["电口(网线)", "光口(光纤)"])
            mode_combo.setCurrentText(config["mode"])
            mode_layout.addWidget(mode_combo)
            layout.addLayout(mode_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_combo_config(
                row, port_range_input.text(), mode_combo.currentText(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_combo_config(self, row, port_range, mode, dialog):
        """保存光电复用配置修改"""
        if not port_range:
            QMessageBox.warning(self, "警告", "请输入接口范围!")
            return

        if 0 <= row < len(self.combo_configs):
            self.combo_configs[row]["port_range"] = port_range.strip()
            self.combo_configs[row]["mode"] = mode
            self.update_combo_table()
            dialog.close()

    def delete_combo_config(self, row):
        """删除光电复用配置"""
        if 0 <= row < len(self.combo_configs):
            self.combo_configs.pop(row)
            self.update_combo_table()

    def update_combo_table(self):
        """更新光电复用表格显示"""
        self.combo_table.setRowCount(len(self.combo_configs))
        for row, config in enumerate(self.combo_configs):
            self.combo_table.setItem(row, 0, QTableWidgetItem(config["port_range"]))
            self.combo_table.setItem(row, 1, QTableWidgetItem(config["mode"]))
            self.combo_table.setItem(row, 2, QTableWidgetItem(config["status"]))

    def add_isolation_config(self):
        """添加端口隔离配置"""
        isolation_id = self.isolation_id.text().strip()
        mode = self.isolation_mode.currentText()
        port_range = self.isolation_port_range.text().strip()

        if not all([isolation_id, port_range]):
            QMessageBox.warning(self, "警告", "请输入隔离组编号和端口范围!")
            return

        config = {
            "isolation_id": isolation_id,
            "mode": mode,
            "port_range": port_range
        }

        self.isolation_configs.append(config)
        self.update_isolation_table()

        # 清空输入框
        self.isolation_id.clear()
        self.isolation_port_range.clear()

    def edit_isolation_config(self, row):
        """编辑端口隔离配置"""
        if 0 <= row < len(self.isolation_configs):
            config = self.isolation_configs[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑端口隔离配置")
            dialog.setFixedSize(400, 200)
            layout = QVBoxLayout(dialog)

            # 隔离组编号
            id_layout = QHBoxLayout()
            id_layout.addWidget(QLabel("隔离组编号:"))
            id_input = QLineEdit(config["isolation_id"])
            id_layout.addWidget(id_input)
            layout.addLayout(id_layout)

            # 隔离模式
            mode_layout = QHBoxLayout()
            mode_layout.addWidget(QLabel("隔离模式:"))
            mode_combo = QComboBox()
            mode_combo.addItems(["二层隔离", "二三层隔离"])
            mode_combo.setCurrentText(config["mode"])
            mode_layout.addWidget(mode_combo)
            layout.addLayout(mode_layout)

            # 端口范围
            port_layout = QHBoxLayout()
            port_layout.addWidget(QLabel("端口范围:"))
            port_input = QLineEdit(config["port_range"])
            port_layout.addWidget(port_input)
            layout.addLayout(port_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_isolation_config(
                row, id_input.text(), mode_combo.currentText(), port_input.text(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_isolation_config(self, row, isolation_id, mode, port_range, dialog):
        """保存端口隔离配置修改"""
        if not all([isolation_id, port_range]):
            QMessageBox.warning(self, "警告", "请输入隔离组编号和端口范围!")
            return

        if 0 <= row < len(self.isolation_configs):
            self.isolation_configs[row]["isolation_id"] = isolation_id.strip()
            self.isolation_configs[row]["mode"] = mode
            self.isolation_configs[row]["port_range"] = port_range.strip()
            self.update_isolation_table()
            dialog.close()

    def delete_isolation_config(self, row):
        """删除端口隔离配置"""
        if 0 <= row < len(self.isolation_configs):
            self.isolation_configs.pop(row)
            self.update_isolation_table()

    def update_isolation_table(self):
        """更新端口隔离表格显示"""
        self.isolation_table.setRowCount(len(self.isolation_configs))
        for row, config in enumerate(self.isolation_configs):
            self.isolation_table.setItem(row, 0, QTableWidgetItem(config["isolation_id"]))
            self.isolation_table.setItem(row, 1, QTableWidgetItem(config["mode"]))
            self.isolation_table.setItem(row, 2, QTableWidgetItem(config["port_range"]))

    def add_console_config(self):
        """添加Console密码配置"""
        auth_mode = self.console_auth_mode.currentText()
        username = self.console_username.text().strip() if auth_mode == "用户名+密码" else ""
        password = self.console_password.text().strip()
        confirm = self.console_confirm.text().strip()

        if not password:
            QMessageBox.warning(self, "警告", "请输入密码!")
            return

        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致!")
            return

        if auth_mode == "用户名+密码" and not username:
            QMessageBox.warning(self, "警告", "请输入用户名!")
            return

        config = {
            "auth_mode": auth_mode,
            "username": username,
            "password": password
        }

        self.console_config = config  # 只保存一个Console配置

        # 显示成功消息
        QMessageBox.information(self, "成功", "Console密码配置已添加!")

        # 清空输入框
        self.console_username.clear()
        self.console_password.clear()
        self.console_confirm.clear()

    def add_static_route(self):
        """添加静态路由配置"""
        dest_network = self.dest_network.text().strip()
        dest_mask = self.dest_mask.text().strip()
        next_hop = self.next_hop.text().strip()
        priority = self.route_priority.text().strip() or "60"

        if not all([dest_network, dest_mask, next_hop]):
            QMessageBox.warning(self, "警告", "请填写完整的目标网络、子网掩码和下一跳!")
            return

        route = {
            "dest_network": dest_network,
            "dest_mask": dest_mask,
            "next_hop": next_hop,
            "priority": priority
        }

        self.static_routes.append(route)
        self.update_route_table()

        # 清空输入框
        self.dest_network.clear()
        self.dest_mask.clear()
        self.next_hop.clear()
        self.route_priority.clear()

    def edit_static_route(self, row):
        """编辑静态路由配置"""
        if 0 <= row < len(self.static_routes):
            route = self.static_routes[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑静态路由")
            dialog.setFixedSize(400, 200)
            layout = QVBoxLayout(dialog)

            # 目标网络
            dest_network_layout = QHBoxLayout()
            dest_network_layout.addWidget(QLabel("目标网络:"))
            dest_network_input = QLineEdit(route["dest_network"])
            dest_network_layout.addWidget(dest_network_input)
            layout.addLayout(dest_network_layout)

            # 子网掩码
            dest_mask_layout = QHBoxLayout()
            dest_mask_layout.addWidget(QLabel("子网掩码:"))
            dest_mask_input = QLineEdit(route["dest_mask"])
            dest_mask_layout.addWidget(dest_mask_input)
            layout.addLayout(dest_mask_layout)

            # 下一跳
            next_hop_layout = QHBoxLayout()
            next_hop_layout.addWidget(QLabel("下一跳:"))
            next_hop_input = QLineEdit(route["next_hop"])
            next_hop_layout.addWidget(next_hop_input)
            layout.addLayout(next_hop_layout)

            # 优先级
            priority_layout = QHBoxLayout()
            priority_layout.addWidget(QLabel("优先级:"))
            priority_input = QLineEdit(route["priority"])
            priority_input.setValidator(QIntValidator(1, 255))
            priority_layout.addWidget(priority_input)
            layout.addLayout(priority_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_static_route(
                row, dest_network_input.text(), dest_mask_input.text(),
                next_hop_input.text(), priority_input.text(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_static_route(self, row, dest_network, dest_mask, next_hop, priority, dialog):
        """保存静态路由修改"""
        if not all([dest_network, dest_mask, next_hop]):
            QMessageBox.warning(self, "警告", "请填写完整的目标网络、子网掩码和下一跳!")
            return

        if 0 <= row < len(self.static_routes):
            self.static_routes[row]["dest_network"] = dest_network.strip()
            self.static_routes[row]["dest_mask"] = dest_mask.strip()
            self.static_routes[row]["next_hop"] = next_hop.strip()
            self.static_routes[row]["priority"] = priority.strip() or "60"
            self.update_route_table()
            dialog.close()

    def delete_static_route(self, row):
        """删除静态路由配置"""
        if 0 <= row < len(self.static_routes):
            self.static_routes.pop(row)
            self.update_route_table()

    def update_route_table(self):
        """更新静态路由表格显示"""
        self.route_table.setRowCount(len(self.static_routes))
        for row, route in enumerate(self.static_routes):
            self.route_table.setItem(row, 0, QTableWidgetItem(route["dest_network"]))
            self.route_table.setItem(row, 1, QTableWidgetItem(route["dest_mask"]))
            self.route_table.setItem(row, 2, QTableWidgetItem(route["next_hop"]))
            self.route_table.setItem(row, 3, QTableWidgetItem(route["priority"]))

    def add_dhcp_pool(self):
        """添加DHCP Pool配置"""
        pool_name = self.dhcp_pool_name.text().strip()
        gateway = self.dhcp_gateway.text().strip()
        network = self.dhcp_network.text().strip()
        mask = self.dhcp_mask.text().strip()
        dns1 = self.dhcp_dns1.text().strip()
        dns2 = self.dhcp_dns2.text().strip()
        range_start = self.dhcp_range_start.text().strip()
        range_end = self.dhcp_range_end.text().strip()
        interface_type = self.dhcp_interface_type.currentText()
        interface_id = self.dhcp_interface_id.text().strip()

        if not all([pool_name, gateway, network, mask, range_start, range_end, interface_id]):
            QMessageBox.warning(self, "警告", "请填写完整的Pool名称、网关、网段、掩码、地址池范围和接口!")
            return

        pool = {
            "pool_name": pool_name,
            "gateway": gateway,
            "network": network,
            "mask": mask,
            "dns1": dns1,
            "dns2": dns2,
            "range_start": range_start,
            "range_end": range_end,
            "interface_type": interface_type,
            "interface_id": interface_id
        }

        self.dhcp_pools.append(pool)
        self.update_dhcp_table()

        # 清空输入框
        self.dhcp_pool_name.clear()
        self.dhcp_gateway.clear()
        self.dhcp_network.clear()
        self.dhcp_mask.clear()
        self.dhcp_dns1.clear()
        self.dhcp_dns2.clear()
        self.dhcp_range_start.clear()
        self.dhcp_range_end.clear()
        self.dhcp_interface_id.clear()

    def edit_dhcp_pool(self, row):
        """编辑DHCP Pool配置"""
        if 0 <= row < len(self.dhcp_pools):
            pool = self.dhcp_pools[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑DHCP Pool")
            dialog.setFixedSize(500, 300)
            layout = QVBoxLayout(dialog)

            # Pool名称
            pool_name_layout = QHBoxLayout()
            pool_name_layout.addWidget(QLabel("Pool名称:"))
            pool_name_input = QLineEdit(pool["pool_name"])
            pool_name_layout.addWidget(pool_name_input)
            layout.addLayout(pool_name_layout)

            # 网关
            gateway_layout = QHBoxLayout()
            gateway_layout.addWidget(QLabel("网关:"))
            gateway_input = QLineEdit(pool["gateway"])
            gateway_layout.addWidget(gateway_input)
            layout.addLayout(gateway_layout)

            # 网段和掩码
            network_layout = QHBoxLayout()
            network_layout.addWidget(QLabel("网段:"))
            network_input = QLineEdit(pool["network"])
            network_layout.addWidget(network_input)

            network_layout.addWidget(QLabel("掩码:"))
            mask_input = QLineEdit(pool["mask"])
            network_layout.addWidget(mask_input)
            layout.addLayout(network_layout)

            # DNS1和DNS2
            dns_layout = QHBoxLayout()
            dns_layout.addWidget(QLabel("DNS1:"))
            dns1_input = QLineEdit(pool["dns1"])
            dns_layout.addWidget(dns1_input)

            dns_layout.addWidget(QLabel("DNS2:"))
            dns2_input = QLineEdit(pool["dns2"])
            dns_layout.addWidget(dns2_input)
            layout.addLayout(dns_layout)

            # 地址池范围
            range_layout = QHBoxLayout()
            range_layout.addWidget(QLabel("地址池范围:"))
            range_start_input = QLineEdit(pool["range_start"])
            range_layout.addWidget(range_start_input)

            range_layout.addWidget(QLabel("到"))
            range_end_input = QLineEdit(pool["range_end"])
            range_layout.addWidget(range_end_input)
            layout.addLayout(range_layout)

            # 接口调用
            interface_layout = QHBoxLayout()
            interface_layout.addWidget(QLabel("接口调用:"))
            interface_type_combo = QComboBox()
            interface_type_combo.addItems(["VLAN接口", "物理接口"])
            interface_type_combo.setCurrentText(pool["interface_type"])
            interface_layout.addWidget(interface_type_combo)

            interface_id_input = QLineEdit(pool["interface_id"])
            interface_layout.addWidget(interface_id_input)
            layout.addLayout(interface_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_dhcp_pool(
                row, pool_name_input.text(), gateway_input.text(),
                network_input.text(), mask_input.text(), dns1_input.text(),
                dns2_input.text(), range_start_input.text(), range_end_input.text(),
                interface_type_combo.currentText(), interface_id_input.text(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_dhcp_pool(self, row, pool_name, gateway, network, mask, dns1, dns2,
                      range_start, range_end, interface_type, interface_id, dialog):
        """保存DHCP Pool修改"""
        if not all([pool_name, gateway, network, mask, range_start, range_end, interface_id]):
            QMessageBox.warning(self, "警告", "请填写完整的Pool名称、网关、网段、掩码、地址池范围和接口!")
            return

        if 0 <= row < len(self.dhcp_pools):
            self.dhcp_pools[row]["pool_name"] = pool_name.strip()
            self.dhcp_pools[row]["gateway"] = gateway.strip()
            self.dhcp_pools[row]["network"] = network.strip()
            self.dhcp_pools[row]["mask"] = mask.strip()
            self.dhcp_pools[row]["dns1"] = dns1.strip()
            self.dhcp_pools[row]["dns2"] = dns2.strip()
            self.dhcp_pools[row]["range_start"] = range_start.strip()
            self.dhcp_pools[row]["range_end"] = range_end.strip()
            self.dhcp_pools[row]["interface_type"] = interface_type
            self.dhcp_pools[row]["interface_id"] = interface_id.strip()
            self.update_dhcp_table()
            dialog.close()

    def delete_dhcp_pool(self, row):
        """删除DHCP Pool配置"""
        if 0 <= row < len(self.dhcp_pools):
            self.dhcp_pools.pop(row)
            self.update_dhcp_table()

    def update_dhcp_table(self):
        """更新DHCP Pool表格显示"""
        self.dhcp_table.setRowCount(len(self.dhcp_pools))
        for row, pool in enumerate(self.dhcp_pools):
            self.dhcp_table.setItem(row, 0, QTableWidgetItem(pool["pool_name"]))
            self.dhcp_table.setItem(row, 1, QTableWidgetItem(pool["gateway"]))
            self.dhcp_table.setItem(row, 2, QTableWidgetItem(pool["network"]))
            self.dhcp_table.setItem(row, 3, QTableWidgetItem(pool["mask"]))
            self.dhcp_table.setItem(row, 4, QTableWidgetItem(pool["dns1"]))
            self.dhcp_table.setItem(row, 5, QTableWidgetItem(pool["dns2"]))
            self.dhcp_table.setItem(row, 6, QTableWidgetItem(f"{pool['range_start']}-{pool['range_end']}"))

            interface_text = f"{pool['interface_type'][0]}{pool['interface_id']}"
            self.dhcp_table.setItem(row, 7, QTableWidgetItem(interface_text))

    def add_ip_binding(self):
        """添加IP端口绑定配置"""
        interface_type = self.binding_interface.currentText()
        interface_id = self.binding_interface_id.text().strip()
        ip = self.binding_ip.text().strip()
        mac = self.binding_mac.text().strip()

        if not all([interface_id, ip, mac]):
            QMessageBox.warning(self, "警告", "请填写完整的接口、IP地址和MAC地址!")
            return

        binding = {
            "interface": f"{interface_type}{interface_id}",
            "ip": ip,
            "mac": mac
        }

        self.ip_bindings.append(binding)
        self.update_binding_table()

        # 清空输入框
        self.binding_interface_id.clear()
        self.binding_ip.clear()
        self.binding_mac.clear()

    def edit_ip_binding(self, row):
        """编辑IP端口绑定配置"""
        if 0 <= row < len(self.ip_bindings):
            binding = self.ip_bindings[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑IP绑定")
            dialog.setFixedSize(400, 200)
            layout = QVBoxLayout(dialog)

            # 解析接口类型和ID
            interface = binding["interface"]
            interface_type = ""
            interface_id = ""

            for port_type in ["GigabitEthernet", "Ethernet", "XGigabitEthernet", "FastEthernet"]:
                if interface.startswith(port_type):
                    interface_type = port_type
                    interface_id = interface[len(port_type):]
                    break

            # 接口
            interface_layout = QHBoxLayout()
            interface_layout.addWidget(QLabel("接口类型:"))
            interface_combo = QComboBox()
            interface_combo.addItems(["GigabitEthernet", "Ethernet", "XGigabitEthernet", "FastEthernet"])
            interface_combo.setCurrentText(interface_type)
            interface_layout.addWidget(interface_combo)

            interface_layout.addWidget(QLabel("接口ID:"))
            interface_id_input = QLineEdit(interface_id)
            interface_layout.addWidget(interface_id_input)
            layout.addLayout(interface_layout)

            # IP地址
            ip_layout = QHBoxLayout()
            ip_layout.addWidget(QLabel("IP地址:"))
            ip_input = QLineEdit(binding["ip"])
            ip_layout.addWidget(ip_input)
            layout.addLayout(ip_layout)

            # MAC地址
            mac_layout = QHBoxLayout()
            mac_layout.addWidget(QLabel("MAC地址:"))
            mac_input = QLineEdit(binding["mac"])
            mac_layout.addWidget(mac_input)
            layout.addLayout(mac_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_ip_binding(
                row, interface_combo.currentText(), interface_id_input.text(),
                ip_input.text(), mac_input.text(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_ip_binding(self, row, interface_type, interface_id, ip, mac, dialog):
        """保存IP绑定修改"""
        if not all([interface_id, ip, mac]):
            QMessageBox.warning(self, "警告", "请填写完整的接口、IP地址和MAC地址!")
            return

        if 0 <= row < len(self.ip_bindings):
            self.ip_bindings[row]["interface"] = f"{interface_type}{interface_id}"
            self.ip_bindings[row]["ip"] = ip.strip()
            self.ip_bindings[row]["mac"] = mac.strip()
            self.update_binding_table()
            dialog.close()

    def delete_ip_binding(self, row):
        """删除IP端口绑定配置"""
        if 0 <= row < len(self.ip_bindings):
            self.ip_bindings.pop(row)
            self.update_binding_table()

    def update_binding_table(self):
        """更新IP绑定表格显示"""
        self.binding_table.setRowCount(len(self.ip_bindings))
        for row, binding in enumerate(self.ip_bindings):
            self.binding_table.setItem(row, 0, QTableWidgetItem(binding["interface"]))
            self.binding_table.setItem(row, 1, QTableWidgetItem(binding["ip"]))
            self.binding_table.setItem(row, 2, QTableWidgetItem(binding["mac"]))

    def show_vlan_config_dialog(self):
        """显示VLAN配置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加VLAN配置")
        dialog.setFixedSize(400, 300)
        layout = QVBoxLayout(dialog)

        # VLAN ID
        vlan_id_layout = QHBoxLayout()
        vlan_id_layout.addWidget(QLabel("VLAN ID:"))
        self.vlan_id_input = QLineEdit()
        vlan_id_layout.addWidget(self.vlan_id_input)
        layout.addLayout(vlan_id_layout)

        # VLAN名称
        vlan_name_layout = QHBoxLayout()
        vlan_name_layout.addWidget(QLabel("VLAN名称:"))
        self.vlan_name_input = QLineEdit()
        vlan_name_layout.addWidget(self.vlan_name_input)
        layout.addLayout(vlan_name_layout)

        # VLAN描述
        vlan_desc_layout = QHBoxLayout()
        vlan_desc_layout.addWidget(QLabel("VLAN描述:"))
        self.vlan_desc_input = QLineEdit()
        vlan_desc_layout.addWidget(self.vlan_desc_input)
        layout.addLayout(vlan_desc_layout)

        # VLAN IP
        vlan_ip_layout = QHBoxLayout()
        vlan_ip_layout.addWidget(QLabel("VLAN IP:"))
        self.vlan_ip_input = QLineEdit()
        vlan_ip_layout.addWidget(self.vlan_ip_input)
        layout.addLayout(vlan_ip_layout)

        # VLAN掩码
        vlan_mask_layout = QHBoxLayout()
        vlan_mask_layout.addWidget(QLabel("VLAN掩码:"))
        self.vlan_mask_input = QLineEdit()
        vlan_mask_layout.addWidget(self.vlan_mask_input)
        layout.addLayout(vlan_mask_layout)

        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(lambda: self.add_vlan_config(dialog))
        layout.addWidget(add_btn)

        dialog.exec_()

    def add_vlan_config(self, dialog):
        """添加VLAN配置"""
        vlan_id = self.vlan_id_input.text().strip()
        vlan_name = self.vlan_name_input.text().strip()
        vlan_desc = self.vlan_desc_input.text().strip()
        vlan_ip = self.vlan_ip_input.text().strip()
        vlan_mask = self.vlan_mask_input.text().strip()

        if not vlan_id:
            QMessageBox.warning(self, "警告", "请输入VLAN ID!")
            return

        config = {
            "id": vlan_id,
            "name": vlan_name,
            "desc": vlan_desc,
            "ip": vlan_ip,
            "mask": vlan_mask
        }

        self.vlan_configs.append(config)
        self.update_vlan_table()
        self.update_port_mode_ui(self.port_mode_combo.currentText())

        # 清空输入框
        self.vlan_id_input.clear()
        self.vlan_name_input.clear()
        self.vlan_desc_input.clear()
        self.vlan_ip_input.clear()
        self.vlan_mask_input.clear()

        dialog.close()

    def edit_vlan_config(self, row):
        """编辑VLAN配置"""
        if 0 <= row < len(self.vlan_configs):
            config = self.vlan_configs[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑VLAN配置")
            dialog.setFixedSize(400, 300)
            layout = QVBoxLayout(dialog)

            # VLAN ID
            vlan_id_layout = QHBoxLayout()
            vlan_id_layout.addWidget(QLabel("VLAN ID:"))
            vlan_id_input = QLineEdit(config["id"])
            vlan_id_input.setEnabled(False)  # 不允许修改VLAN ID
            vlan_id_layout.addWidget(vlan_id_input)
            layout.addLayout(vlan_id_layout)

            # VLAN名称
            vlan_name_layout = QHBoxLayout()
            vlan_name_layout.addWidget(QLabel("VLAN名称:"))
            vlan_name_input = QLineEdit(config["name"])
            vlan_name_layout.addWidget(vlan_name_input)
            layout.addLayout(vlan_name_layout)

            # VLAN描述
            vlan_desc_layout = QHBoxLayout()
            vlan_desc_layout.addWidget(QLabel("VLAN描述:"))
            vlan_desc_input = QLineEdit(config["desc"])
            vlan_desc_layout.addWidget(vlan_desc_input)
            layout.addLayout(vlan_desc_layout)

            # VLAN IP
            vlan_ip_layout = QHBoxLayout()
            vlan_ip_layout.addWidget(QLabel("VLAN IP:"))
            vlan_ip_input = QLineEdit(config["ip"])
            vlan_ip_layout.addWidget(vlan_ip_input)
            layout.addLayout(vlan_ip_layout)

            # VLAN掩码
            vlan_mask_layout = QHBoxLayout()
            vlan_mask_layout.addWidget(QLabel("VLAN掩码:"))
            vlan_mask_input = QLineEdit(config["mask"])
            vlan_mask_layout.addWidget(vlan_mask_input)
            layout.addLayout(vlan_mask_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_vlan_config(
                row, vlan_name_input.text(), vlan_desc_input.text(),
                vlan_ip_input.text(), vlan_mask_input.text(), dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def save_vlan_config(self, row, name, desc, ip, mask, dialog):
        """保存VLAN配置修改"""
        if 0 <= row < len(self.vlan_configs):
            self.vlan_configs[row]["name"] = name.strip()
            self.vlan_configs[row]["desc"] = desc.strip()
            self.vlan_configs[row]["ip"] = ip.strip()
            self.vlan_configs[row]["mask"] = mask.strip()
            self.update_vlan_table()
            self.update_port_mode_ui(self.port_mode_combo.currentText())
            dialog.close()

    def delete_vlan_config(self, row):
        """删除VLAN配置"""
        if 0 <= row < len(self.vlan_configs):
            self.vlan_configs.pop(row)
            self.update_vlan_table()
            self.update_port_mode_ui(self.port_mode_combo.currentText())

    def update_vlan_table(self):
        """更新VLAN表格显示"""
        self.vlan_table.setRowCount(len(self.vlan_configs))
        for row, config in enumerate(self.vlan_configs):
            self.vlan_table.setItem(row, 0, QTableWidgetItem(config["id"]))
            self.vlan_table.setItem(row, 1, QTableWidgetItem(config["name"]))
            self.vlan_table.setItem(row, 2, QTableWidgetItem(config["desc"]))
            self.vlan_table.setItem(row, 3, QTableWidgetItem(config["ip"]))
            self.vlan_table.setItem(row, 4, QTableWidgetItem(config["mask"]))

    def update_port_mode_ui(self, mode):
        """根据端口模式更新UI"""
        self.access_vlan_combo.setEnabled(mode == "access")
        self.trunk_vlans_edit.setEnabled(mode == "trunk")

        # 更新Access VLAN下拉框
        if mode == "access":
            self.access_vlan_combo.clear()
            for vlan in self.vlan_configs:
                self.access_vlan_combo.addItem(vlan["id"])
            if self.vlan_configs:
                self.access_vlan_combo.setCurrentIndex(0)

    def add_port_config(self):
        """添加端口配置"""
        mode = self.port_mode_combo.currentText()
        port_type = self.port_type_combo.currentText()
        port_range = self.port_range_edit.text().strip()

        if not port_range:
            return

        # 验证VLAN配置
        if mode == "access":
            if not self.access_vlan_combo.currentText():
                return
            vlan_config = f"VLAN {self.access_vlan_combo.currentText()}"
            vlan = self.access_vlan_combo.currentText()
        else:  # trunk
            trunk_vlans = self.trunk_vlans_edit.text().strip()
            if not trunk_vlans:
                return
            if trunk_vlans.lower() != "all":
                # 验证VLAN是否已创建
                existing_vlans = {vlan["id"] for vlan in self.vlan_configs}
                input_vlans = set(re.split(r"[,\s]+", trunk_vlans))
                if not input_vlans.issubset(existing_vlans):
                    return
            vlan_config = f"允许VLAN {trunk_vlans}"
            vlan = trunk_vlans

        config = {
            "type": port_type,
            "range": port_range,
            "mode": mode,
            "vlan_config": vlan_config,
            "raw": {
                "mode": mode,
                "type": port_type,
                "range": port_range,
                "vlan": vlan
            }
        }

        self.port_configs.append(config)
        self.update_port_table()

    def edit_port_config(self, row):
        """编辑端口配置"""
        if 0 <= row < len(self.port_configs):
            config = self.port_configs[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("编辑端口配置")
            dialog.setFixedSize(400, 250)
            layout = QVBoxLayout(dialog)

            # 端口类型
            port_type_layout = QHBoxLayout()
            port_type_layout.addWidget(QLabel("端口类型:"))
            port_type_combo = QComboBox()
            port_type_combo.addItems(["GigabitEthernet", "Ethernet", "XGigabitEthernet", "FastEthernet"])
            port_type_combo.setCurrentText(config["raw"]["type"])
            port_type_layout.addWidget(port_type_combo)
            layout.addLayout(port_type_layout)

            # 端口范围
            port_range_layout = QHBoxLayout()
            port_range_layout.addWidget(QLabel("端口范围:"))
            port_range_edit = QLineEdit(config["raw"]["range"])
            port_range_layout.addWidget(port_range_edit)
            layout.addLayout(port_range_layout)

            # 端口模式
            port_mode_layout = QHBoxLayout()
            port_mode_layout.addWidget(QLabel("端口模式:"))
            port_mode_combo = QComboBox()
            port_mode_combo.addItems(["access", "trunk"])
            port_mode_combo.setCurrentText(config["raw"]["mode"])
            port_mode_combo.currentTextChanged.connect(lambda mode: self.update_port_edit_ui(
                mode, vlan_combo, vlan_edit))
            port_mode_layout.addWidget(port_mode_combo)
            layout.addLayout(port_mode_layout)

            # VLAN配置
            vlan_config_layout = QHBoxLayout()
            vlan_combo = QComboBox()
            vlan_combo.addItems([vlan["id"] for vlan in self.vlan_configs])
            vlan_edit = QLineEdit()

            if config["raw"]["mode"] == "access":
                vlan_combo.setCurrentText(config["raw"]["vlan"])
                vlan_combo.setEnabled(True)
                vlan_edit.setEnabled(False)
            else:
                vlan_edit.setText(config["raw"]["vlan"])
                vlan_edit.setEnabled(True)
                vlan_combo.setEnabled(False)

            vlan_config_layout.addWidget(QLabel("Access VLAN:"))
            vlan_config_layout.addWidget(vlan_combo)
            vlan_config_layout.addWidget(QLabel("Trunk VLANs:"))
            vlan_config_layout.addWidget(vlan_edit)
            layout.addLayout(vlan_config_layout)

            # 保存按钮
            save_btn = QPushButton("保存")
            save_btn.clicked.connect(lambda: self.save_port_config(
                row, port_type_combo.currentText(), port_range_edit.text(),
                port_mode_combo.currentText(), vlan_combo.currentText() if port_mode_combo.currentText() == "access" else vlan_edit.text(),
                dialog
            ))
            layout.addWidget(save_btn)

            dialog.exec_()

    def update_port_edit_ui(self, mode, vlan_combo, vlan_edit):
        """更新端口编辑UI"""
        vlan_combo.setEnabled(mode == "access")
        vlan_edit.setEnabled(mode == "trunk")
        if mode == "access":
            vlan_combo.clear()
            for vlan in self.vlan_configs:
                vlan_combo.addItem(vlan["id"])
            if self.vlan_configs:
                vlan_combo.setCurrentIndex(0)

    def save_port_config(self, row, port_type, port_range, mode, vlan, dialog):
        """保存端口配置修改"""
        if not port_range:
            return

        if mode == "access":
            vlan_config = f"VLAN {vlan}"
        else:  # trunk
            vlan_config = f"允许VLAN {vlan}"

        if 0 <= row < len(self.port_configs):
            self.port_configs[row]["type"] = port_type
            self.port_configs[row]["range"] = port_range
            self.port_configs[row]["mode"] = mode
            self.port_configs[row]["vlan_config"] = vlan_config
            self.port_configs[row]["raw"]["type"] = port_type
            self.port_configs[row]["raw"]["range"] = port_range
            self.port_configs[row]["raw"]["mode"] = mode
            self.port_configs[row]["raw"]["vlan"] = vlan
            self.update_port_table()
            dialog.close()

    def delete_port_config(self, row):
        """删除端口配置"""
        if 0 <= row < len(self.port_configs):
            self.port_configs.pop(row)
            self.update_port_table()

    def update_port_table(self):
        """更新端口表格显示"""
        self.port_table.setRowCount(len(self.port_configs))
        for row, config in enumerate(self.port_configs):
            self.port_table.setItem(row, 0, QTableWidgetItem(config["type"]))
            self.port_table.setItem(row, 1, QTableWidgetItem(config["range"]))
            self.port_table.setItem(row, 2, QTableWidgetItem(config["mode"].upper()))
            self.port_table.setItem(row, 3, QTableWidgetItem(config["vlan_config"]))

    def clear_all_configs(self):
        """清除所有配置"""
        self.vlan_configs = []
        self.port_configs = []
        self.static_routes = []
        self.dhcp_pools = []
        self.ip_bindings = []
        self.combo_configs = []
        self.isolation_configs = []
        self.console_config = None

        self.update_vlan_table()
        self.update_port_table()
        self.update_route_table()
        self.update_dhcp_table()
        self.update_binding_table()
        self.update_combo_table()
        self.update_isolation_table()

        self.device_name.clear()
        self.batch_vlan_input.clear()
        self.port_range_edit.clear()
        self.access_vlan_combo.clear()
        self.trunk_vlans_edit.clear()
        self.preview_terminal.clear()

        # 清空高级配置的输入框
        self.dest_network.clear()
        self.dest_mask.clear()
        self.next_hop.clear()
        self.route_priority.clear()

        self.dhcp_pool_name.clear()
        self.dhcp_gateway.clear()
        self.dhcp_network.clear()
        self.dhcp_mask.clear()
        self.dhcp_dns1.clear()
        self.dhcp_dns2.clear()
        self.dhcp_range_start.clear()
        self.dhcp_range_end.clear()
        self.dhcp_interface_id.clear()

        self.binding_interface_id.clear()
        self.binding_ip.clear()
        self.binding_mac.clear()

        # 清空光电复用配置
        self.combo_enable.setChecked(False)
        self.combo_mode.setCurrentIndex(0)
        self.combo_port_range.clear()

        # 清空端口隔离配置
        self.isolation_id.clear()
        self.isolation_mode.setCurrentIndex(0)
        self.isolation_port_range.clear()

        # 清空Console密码配置
        self.console_enable.setChecked(False)
        self.console_auth_mode.setCurrentIndex(0)
        self.console_username.clear()
        self.console_password.clear()
        self.console_confirm.clear()

    def init_command_tab(self):
        """初始化命令查询选项卡"""
        layout = QVBoxLayout(self.command_tab)

        # 使用QTextEdit显示命令表格
        self.command_view = QTextEdit()
        self.command_view.setReadOnly(True)
        self.command_view.setFont(QFont("Courier New", 10))

        # 加载命令数据
        commands = self.load_command_data()
        self.command_view.setHtml(commands)

        layout.addWidget(self.command_view)

    def load_command_data(self):
        """加载命令数据"""
        return """
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 30px;
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
    }
    h2 {
        color: #2980b9;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 30px;
        box-shadow: 0 2px 3px rgba(0,0,0,0.1);
    }
    th {
        background-color: #3498db;
        color: white;
        padding: 12px;
        text-align: left;
    }
    td {
        padding: 10px;
        border: 1px solid #ddd;
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    tr:hover {
        background-color: #e6f7ff;
    }
    b {
        color: #2c3e50;
    }
</style>

<h1 style="text-align: center;">网络设备命令大全（华为/H3C/思科/锐捷）</h1>

<h2>基础操作命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>命令补全</b></td>
    <td>Tab键</td>
    <td>Tab键</td>
    <td>Tab键</td>
    <td>Tab键</td>
</tr>
<tr>
    <td><b>查看当前配置</b></td>
    <td>display current-configuration</td>
    <td>display current-configuration</td>
    <td>show running-config</td>
    <td>show running-config</td>
</tr>
<tr>
    <td><b>查看已保存配置</b></td>
    <td>display saved-configuration</td>
    <td>display saved-configuration</td>
    <td>show startup-config</td>
    <td>show startup-config</td>
</tr>
<tr>
    <td><b>进入配置模式</b></td>
    <td>system-view</td>
    <td>system-view</td>
    <td>enable → config terminal</td>
    <td>enable → config terminal</td>
</tr>
<tr>
    <td><b>退出当前视图</b></td>
    <td>quit</td>
    <td>quit</td>
    <td>exit</td>
    <td>exit</td>
</tr>
<tr>
    <td><b>返回用户视图</b></td>
    <td>return</td>
    <td>return</td>
    <td>end</td>
    <td>end</td>
</tr>
<tr>
    <td><b>取消配置</b></td>
    <td>undo</td>
    <td>undo</td>
    <td>no</td>
    <td>no</td>
</tr>
<tr>
    <td><b>保存配置</b></td>
    <td>save</td>
    <td>save</td>
    <td>write</td>
    <td>write</td>
</tr>
<tr>
    <td><b>重启设备</b></td>
    <td>reboot</td>
    <td>reboot</td>
    <td>reload</td>
    <td>reload</td>
</tr>
</table>

<h2>端口配置命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>批量进入端口</b></td>
    <td>port-group group-member g0/0/1 to g0/0/24</td>
    <td>int range g1/0/1-24</td>
    <td>int range g0/1-24</td>
    <td>int range g0/1-24</td>
</tr>
<tr>
    <td><b>关闭端口</b></td>
    <td>shutdown</td>
    <td>shutdown</td>
    <td>shutdown</td>
    <td>shutdown</td>
</tr>
<tr>
    <td><b>开启端口</b></td>
    <td>undo shutdown</td>
    <td>undo shutdown</td>
    <td>no shutdown</td>
    <td>no shutdown</td>
</tr>
<tr>
    <td><b>端口描述</b></td>
    <td>description XXX</td>
    <td>description XXX</td>
    <td>description XXX</td>
    <td>description XXX</td>
</tr>
<tr>
    <td><b>配置双工模式</b></td>
    <td>duplex {half|full|auto}</td>
    <td>duplex {half|full|auto}</td>
    <td>duplex {half|full|auto}</td>
    <td>duplex {half|full|auto}</td>
</tr>
<tr>
    <td><b>配置端口速率</b></td>
    <td>speed {10|100|1000}</td>
    <td>speed {10|100|1000}</td>
    <td>speed {10|100|1000}</td>
    <td>speed {10|100|1000}</td>
</tr>
</table>

<h2>VLAN配置命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>创建VLAN</b></td>
    <td>vlan 10</td>
    <td>vlan 10</td>
    <td>vlan 10</td>
    <td>vlan 10</td>
</tr>
<tr>
    <td><b>批量创建VLAN</b></td>
    <td>vlan batch 2 5 8 to 18</td>
    <td>vlan 2 5 8 to 18</td>
    <td>vlan 2,5,8-18</td>
    <td>vlan range 2,5,8-18</td>
</tr>
<tr>
    <td><b>删除VLAN</b></td>
    <td>undo vlan 10</td>
    <td>undo vlan 10</td>
    <td>no vlan 10</td>
    <td>no vlan 10</td>
</tr>
<tr>
    <td><b>进入VLAN接口</b></td>
    <td>interface vlanif 10</td>
    <td>interface vlan 10</td>
    <td>interface vlan 10</td>
    <td>interface vlan 10</td>
</tr>
<tr>
    <td><b>配置Access端口</b></td>
    <td>port link-type access<br>port default vlan 10</td>
    <td>port link-type access<br>port access vlan 10</td>
    <td>switchport mode access<br>switchport access vlan 10</td>
    <td>switchport mode access<br>switchport access vlan 10</td>
</tr>
<tr>
    <td><b>配置Trunk端口</b></td>
    <td>port link-type trunk<br>port trunk allow-pass vlan 10</td>
    <td>port link-type trunk<br>port trunk permit vlan 10</td>
    <td>switchport mode trunk<br>switchport trunk allowed vlan 10</td>
    <td>switchport mode trunk<br>switchport trunk allowed vlan 10</td>
</tr>
</table>

<h2>路由配置命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>配置静态路由</b></td>
    <td>ip route-static 192.168.1.0 24 10.1.1.1</td>
    <td>ip route-static 192.168.1.0 24 10.1.1.1</td>
    <td>ip route 192.168.1.0 255.255.255.0 10.1.1.1</td>
    <td>ip route 192.168.1.0 255.255.255.0 10.1.1.1</td>
</tr>
<tr>
    <td><b>配置默认路由</b></td>
    <td>ip route-static 0.0.0.0 0 192.168.1.1</td>
    <td>ip route-static 0.0.0.0 0 192.168.1.1</td>
    <td>ip route 0.0.0.0 0.0.0.0 192.168.1.1</td>
    <td>ip route 0.0.0.0 0.0.0.0 192.168.1.1</td>
</tr>
<tr>
    <td><b>查看路由表</b></td>
    <td>display ip routing-table</td>
    <td>display ip routing-table</td>
    <td>show ip route</td>
    <td>show ip route</td>
</tr>
</table>

<h2>安全与ACL配置</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>创建ACL</b></td>
    <td>acl [number]</td>
    <td>acl [number]</td>
    <td>access-list [number]</td>
    <td>access-list [number]</td>
</tr>
<tr>
    <td><b>应用ACL</b></td>
    <td>traffic-filter inbound acl [number]</td>
    <td>packet-filter [number] inbound</td>
    <td>ip access-group [number] in</td>
    <td>ip access-group [number] in</td>
</tr>
<tr>
    <td><b>查看ACL</b></td>
    <td>display acl all</td>
    <td>display acl all</td>
    <td>show access-lists</td>
    <td>show access-lists</td>
</tr>
</table>

<h2>设备管理命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>恢复出厂设置</b></td>
    <td>reset saved-configuration → reboot</td>
    <td>reset saved-configuration → reboot</td>
    <td>erase startup-config → reload</td>
    <td>delete config.text → reload</td>
</tr>
<tr>
    <td><b>查看设备信息</b></td>
    <td>display version</td>
    <td>display version</td>
    <td>show version</td>
    <td>show version</td>
</tr>
<tr>
    <td><b>查看接口状态</b></td>
    <td>display interface brief</td>
    <td>display interface brief</td>
    <td>show ip interface brief</td>
    <td>show ip interface brief</td>
</tr>
<tr>
    <td><b>查看ARP表</b></td>
    <td>display arp</td>
    <td>display arp</td>
    <td>show arp</td>
    <td>show arp</td>
</tr>
<tr>
    <td><b>查看MAC表</b></td>
    <td>display mac-address</td>
    <td>display mac-address</td>
    <td>show mac address-table</td>
    <td>show mac address-table</td>
</tr>
</table>

<h2>高级功能</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>端口聚合</b></td>
    <td>interface eth-trunk 1</td>
    <td>interface Bridge-Aggregation 1</td>
    <td>interface port-channel 1</td>
    <td>interface aggregatePort 1</td>
</tr>
<tr>
    <td><b>STP配置</b></td>
    <td>stp enable<br>stp mode rstp</td>
    <td>stp enable<br>stp mode rstp</td>
    <td>spanning-tree<br>spanning-tree mode rapid-pvst</td>
    <td>spanning-tree<br>spanning-tree mode rstp</td>
</tr>
<tr>
    <td><b>DHCP配置</b></td>
    <td>dhcp enable<br>ip pool [name]</td>
    <td>dhcp enable<br>dhcp server ip-pool [name]</td>
    <td>service dhcp<br>ip dhcp pool [name]</td>
    <td>service dhcp<br>ip dhcp pool [name]</td>
</tr>
<tr>
    <td><b>NAT配置</b></td>
    <td>nat outbound [acl-number]</td>
    <td>nat outbound [acl-number]</td>
    <td>ip nat inside/outside</td>
    <td>ip nat inside/outside</td>
</tr>
</table>

<h2>光电口配置</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>切换光口</b></td>
    <td>combo-port fiber</td>
    <td>combo enable fiber</td>
    <td>medium-type fiber</td>
    <td>medium-type fiber</td>
</tr>
<tr>
    <td><b>切换电口</b></td>
    <td>combo-port copper</td>
    <td>combo enable copper</td>
    <td>medium-type copper</td>
    <td>medium-type copper</td>
</tr>
<tr>
    <td><b>POE控制</b></td>
    <td>poe enable/undo poe enable</td>
    <td>poe enable/undo poe enable</td>
    <td>poe enable/no poe enable</td>
    <td>poe enable/no poe enable</td>
</tr>
</table>

<h2>端口隔离配置</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>二层隔离</b></td>
    <td>port-isolate mode l2<br>port-isolate enable</td>
    <td>port-isolate mode l2<br>port-isolate enable</td>
    <td>switchport protected</td>
    <td>switchport protected</td>
</tr>
<tr>
    <td><b>二三层隔离</b></td>
    <td>port-isolate mode all<br>port-isolate enable</td>
    <td>port-isolate mode all<br>port-isolate enable</td>
    <td>switchport protected</td>
    <td>switchport protected</td>
</tr>
</table>

<h2>Console配置</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>仅密码认证</b></td>
    <td>user-interface con 0<br>authentication-mode password<br>set authentication password cipher xxx</td>
    <td>user-interface con 0<br>authentication-mode password<br>set authentication password cipher xxx</td>
    <td>line con 0<br>password xxx<br>login</td>
    <td>line con 0<br>password xxx<br>login</td>
</tr>
<tr>
    <td><b>用户名+密码认证</b></td>
    <td>user-interface con 0<br>authentication-mode scheme<br>local-user admin password cipher xxx<br>local-user admin service-type terminal</td>
    <td>user-interface con 0<br>authentication-mode scheme<br>local-user admin password cipher xxx<br>local-user admin service-type terminal</td>
    <td>line con 0<br>login local<br>username admin password xxx</td>
    <td>line con 0<br>login local<br>username admin password xxx</td>
</tr>
</table>

<h2>巡检维护命令</h2>

<table>
<tr>
    <th>说明</th>
    <th>华为</th>
    <th>H3C</th>
    <th>思科</th>
    <th>锐捷</th>
</tr>
<tr>
    <td><b>查看CPU使用率</b></td>
    <td>display cpu-usage</td>
    <td>display cpu</td>
    <td>show processes cpu</td>
    <td>show cpu</td>
</tr>
<tr>
    <td><b>查看内存使用率</b></td>
    <td>display memory-usage</td>
    <td>display memory</td>
    <td>show processes memory</td>
    <td>show memory</td>
</tr>
<tr>
    <td><b>查看设备温度</b></td>
    <td>display environment</td>
    <td>display environment</td>
    <td>show environment</td>
    <td>show temperature</td>
</tr>
<tr>
    <td><b>查看日志</b></td>
    <td>display logbuffer</td>
    <td>display logbuffer</td>
    <td>show logging</td>
    <td>show logging</td>
</tr>
<tr>
    <td><b>查看接口统计</b></td>
    <td>display interface [interface] counters</td>
    <td>display interface [interface] counters</td>
    <td>show interface [interface]</td>
    <td>show interface [interface]</td>
</tr>
</table>
"""

    def init_preview(self):
        """初始化预览区域"""
        # 预览标题
        preview_title = QLabel("配置命令预览")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.preview_layout.addWidget(preview_title)

        # 终端风格预览区域
        self.preview_terminal = QTextEdit()
        self.preview_terminal.setReadOnly(True)
        self.preview_terminal.setFont(QFont("Courier New", 10))
        self.preview_terminal.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: #00FF00;
                border: 1px solid #333;
                padding: 5px;
            }
        """)

        # 按钮布局
        btn_layout = QHBoxLayout()

        # 添加复制按钮
        copy_btn = QPushButton("复制配置")
        copy_btn.clicked.connect(self.copy_config)
        btn_layout.addWidget(copy_btn)

        # 添加导出按钮
        export_btn = QPushButton("导出配置")
        export_btn.clicked.connect(self.export_config)
        btn_layout.addWidget(export_btn)

        # 添加清空按钮
        clear_btn = QPushButton("清空预览")
        clear_btn.clicked.connect(self.clear_preview)
        btn_layout.addWidget(clear_btn)

        self.preview_layout.addWidget(self.preview_terminal)
        self.preview_layout.addLayout(btn_layout)

    def generate_config(self):
        """生成配置命令"""
        vendor = self.vendor_combo.currentText()
        device_name = self.device_name.text().strip()
        batch_vlan = self.batch_vlan_input.text().strip()

        config_lines = []

        # 添加关闭信息中心配置
        if self.disable_info_center.isChecked():
            if vendor in ["华为", "华三"]:
                config_lines.append("undo info-center enable")
            elif vendor == "思科":
                config_lines.append("no logging console")
                config_lines.append("no logging monitor")
            elif vendor == "锐捷":
                config_lines.append("no logging console")

        # 添加设备名称配置
        if device_name:
            if vendor in ["华为", "华三"]:
                config_lines.append(f"sysname {device_name}")
            elif vendor in ["思科", "锐捷"]:
                config_lines.append(f"hostname {device_name}")

        # 添加批量VLAN创建
        if batch_vlan:
            if "to" in batch_vlan:
                start, end = batch_vlan.split("to")
                start = start.strip()
                end = end.strip()
                if vendor == "华为":
                    config_lines.append(f"vlan batch {start} to {end}")
                elif vendor == "华三":
                    config_lines.append(f"vlan {start} to {end}")
                elif vendor == "思科":
                    config_lines.append(f"vlan {start}-{end}")
                elif vendor == "锐捷":
                    config_lines.append(f"vlan range {start}-{end}")
            else:
                if vendor == "华为":
                    config_lines.append(f"vlan batch {batch_vlan}")
                elif vendor == "华三":
                    config_lines.append(f"vlan {batch_vlan}")
                elif vendor == "思科":
                    config_lines.append(f"vlan {batch_vlan.replace(' ', ',')}")
                elif vendor == "锐捷":
                    config_lines.append(f"vlan range {batch_vlan.replace(' ', ',')}")

        # 添加VLAN配置
        for vlan in self.vlan_configs:
            if vendor == "华为":
                config_lines.append(f"vlan {vlan['id']}")
                if vlan['name']:
                    config_lines.append(f" description {vlan['name']}")
                if vlan['desc']:
                    config_lines.append(f" description {vlan['desc']}")
                if vlan['ip'] and vlan['mask']:
                    config_lines.append(f"interface Vlanif{vlan['id']}")
                    config_lines.append(f" ip address {vlan['ip']} {vlan['mask']}")
                    config_lines.append(" quit")
            elif vendor == "华三":
                config_lines.append(f"vlan {vlan['id']}")
                if vlan['name']:
                    config_lines.append(f" name {vlan['name']}")
                if vlan['desc']:
                    config_lines.append(f" description {vlan['desc']}")
                if vlan['ip'] and vlan['mask']:
                    config_lines.append(f"interface Vlan-interface{vlan['id']}")
                    config_lines.append(f" ip address {vlan['ip']} {vlan['mask']}")
                    config_lines.append(" quit")
            elif vendor == "思科":
                config_lines.append(f"vlan {vlan['id']}")
                if vlan['name']:
                    config_lines.append(f" name {vlan['name']}")
                if vlan['ip'] and vlan['mask']:
                    config_lines.append(f"interface vlan {vlan['id']}")
                    config_lines.append(f" ip address {vlan['ip']} {vlan['mask']}")
                    config_lines.append(" exit")
            elif vendor == "锐捷":
                config_lines.append(f"vlan {vlan['id']}")
                if vlan['name']:
                    config_lines.append(f" name {vlan['name']}")
                if vlan['ip'] and vlan['mask']:
                    config_lines.append(f"interface vlan {vlan['id']}")
                    config_lines.append(f" ip address {vlan['ip']} {vlan['mask']}")
                    config_lines.append(" exit")

        # 添加端口配置
        for port in self.port_configs:
            port_type = port["raw"]["type"]
            port_range = port["raw"]["range"]

            if vendor == "华为":
                if port["raw"]["mode"] == "access":
                    config_lines.append(f"interface {port_type} {port_range}")
                    config_lines.append(" port link-type access")
                    config_lines.append(f" port default vlan {port['raw']['vlan']}")
                    config_lines.append(" quit")
                else:  # trunk
                    config_lines.append(f"interface {port_type} {port_range}")
                    config_lines.append(" port link-type trunk")
                    if port['raw']['vlan'].lower() == "all":
                        config_lines.append(" port trunk allow-pass vlan all")
                    else:
                        config_lines.append(f" port trunk allow-pass vlan {port['raw']['vlan']}")
                    config_lines.append(" quit")
            elif vendor == "华三":
                if port["raw"]["mode"] == "access":
                    config_lines.append(f"interface {port_type} {port_range}")
                    config_lines.append(" port link-type access")
                    config_lines.append(f" port access vlan {port['raw']['vlan']}")
                    config_lines.append(" quit")
                else:  # trunk
                    config_lines.append(f"interface {port_type} {port_range}")
                    config_lines.append(" port link-type trunk")
                    if port['raw']['vlan'].lower() == "all":
                        config_lines.append(" port trunk permit vlan all")
                    else:
                        config_lines.append(f" port trunk permit vlan {port['raw']['vlan']}")
                    config_lines.append(" quit")
            elif vendor == "思科":
                if port["raw"]["mode"] == "access":
                    config_lines.append(f"interface range {port_type} {port_range}")
                    config_lines.append(" switchport mode access")
                    config_lines.append(f" switchport access vlan {port['raw']['vlan']}")
                    config_lines.append(" exit")
                else:  # trunk
                    config_lines.append(f"interface range {port_type} {port_range}")
                    config_lines.append(" switchport mode trunk")
                    if port['raw']['vlan'].lower() == "all":
                        config_lines.append(" switchport trunk allowed vlan all")
                    else:
                        config_lines.append(f" switchport trunk allowed vlan {port['raw']['vlan']}")
                    config_lines.append(" exit")
            elif vendor == "锐捷":
                if port["raw"]["mode"] == "access":
                    config_lines.append(f"interface range {port_type} {port_range}")
                    config_lines.append(" switchport mode access")
                    config_lines.append(f" switchport access vlan {port['raw']['vlan']}")
                    config_lines.append(" exit")
                else:  # trunk
                    config_lines.append(f"interface range {port_type} {port_range}")
                    config_lines.append(" switchport mode trunk")
                    if port['raw']['vlan'].lower() == "all":
                        config_lines.append(" switchport trunk allowed vlan all")
                    else:
                        config_lines.append(f" switchport trunk allowed vlan {port['raw']['vlan']}")
                    config_lines.append(" exit")

        # 添加光电复用配置
        if hasattr(self, 'combo_configs') and self.combo_configs:
            config_lines.append("")
            config_lines.append("! 光电复用配置")
            for combo in self.combo_configs:
                if vendor == "华为":
                    config_lines.append(f"interface {combo['port_range']}")
                    if "电口" in combo['mode']:
                        config_lines.append(" combo-port copper")
                    else:
                        config_lines.append(" combo-port fiber")
                    config_lines.append(" quit")
                elif vendor == "华三":
                    config_lines.append(f"interface {combo['port_range']}")
                    if "电口" in combo['mode']:
                        config_lines.append(" combo enable copper")
                    else:
                        config_lines.append(" combo enable fiber")
                    config_lines.append(" quit")
                elif vendor == "思科":
                    config_lines.append(f"interface range {combo['port_range']}")
                    if "电口" in combo['mode']:
                        config_lines.append(" medium-type copper")
                    else:
                        config_lines.append(" medium-type fiber")
                    config_lines.append(" exit")
                elif vendor == "锐捷":
                    config_lines.append(f"interface range {combo['port_range']}")
                    if "电口" in combo['mode']:
                        config_lines.append(" medium-type copper")
                    else:
                        config_lines.append(" medium-type fiber")
                    config_lines.append(" exit")

        # 添加端口隔离配置
        if hasattr(self, 'isolation_configs') and self.isolation_configs:
            config_lines.append("")
            config_lines.append("! 端口隔离配置")
            for isolation in self.isolation_configs:
                if vendor == "华为":
                    mode = "l2" if isolation['mode'] == "二层隔离" else "all"
                    config_lines.append(f"port-isolate mode {mode}")
                    config_lines.append(f"interface range {isolation['port_range']}")
                    config_lines.append(f" port-isolate enable group {isolation['isolation_id']}")
                    config_lines.append(" quit")
                elif vendor == "华三":
                    mode = "l2" if isolation['mode'] == "二层隔离" else "all"
                    config_lines.append(f"port-isolate mode {mode}")
                    config_lines.append(f"interface range {isolation['port_range']}")
                    config_lines.append(f" port-isolate enable group {isolation['isolation_id']}")
                    config_lines.append(" quit")
                elif vendor == "思科":
                    config_lines.append(f"interface range {isolation['port_range']}")
                    config_lines.append(" switchport protected")
                    config_lines.append(" exit")
                elif vendor == "锐捷":
                    config_lines.append(f"interface range {isolation['port_range']}")
                    config_lines.append(" switchport protected")
                    config_lines.append(" exit")
        # 添加Console密码配置
        if hasattr(self, 'console_config') and self.console_config:
            config_lines.append("")
            config_lines.append("! Console密码配置")
            if vendor in ["华为", "华三"]:
                config_lines.append("user-interface con 0")
                if self.console_config['auth_mode'] == "用户名+密码":
                    config_lines.append(f" authentication-mode scheme")
                    config_lines.append(f" local-user {self.console_config['username']} password cipher {self.console_config['password']}")
                    config_lines.append(f" local-user {self.console_config['username']} service-type terminal")
                else:
                    config_lines.append(f" authentication-mode password")
                    config_lines.append(f" set authentication password cipher {self.console_config['password']}")
                config_lines.append(" quit")
            elif vendor == "思科":
                config_lines.append("line con 0")
                if self.console_config['auth_mode'] == "用户名+密码":
                    config_lines.append(f" login local")
                    config_lines.append(f" username {self.console_config['username']} password {self.console_config['password']}")
                else:
                    config_lines.append(f" password {self.console_config['password']}")
                    config_lines.append(" login")
                config_lines.append(" exit")
            elif vendor == "锐捷":
                config_lines.append("line con 0")
                if self.console_config['auth_mode'] == "用户名+密码":
                    config_lines.append(f" login local")
                    config_lines.append(f" username {self.console_config['username']} password {self.console_config['password']}")
                else:
                    config_lines.append(f" password {self.console_config['password']}")
                    config_lines.append(" login")
                config_lines.append(" exit")

        # 添加静态路由配置
        if self.static_routes:
            config_lines.append("")
            config_lines.append("! 静态路由配置")
            for route in self.static_routes:
                if vendor in ["华为", "华三"]:
                    config_lines.append(f"ip route-static {route['dest_network']} {route['dest_mask']} {route['next_hop']} preference {route['priority']}")
                elif vendor in ["思科", "锐捷"]:
                    config_lines.append(f"ip route {route['dest_network']} {route['dest_mask']} {route['next_hop']}")

        # 添加DHCP配置
        if self.dhcp_pools:
            config_lines.append("")
            config_lines.append("! DHCP配置")
            if vendor == "华为":
                config_lines.append("dhcp enable")
                for pool in self.dhcp_pools:
                    config_lines.append(f"ip pool {pool['pool_name']}")
                    config_lines.append(f" gateway-list {pool['gateway']}")
                    config_lines.append(f" network {pool['network']} mask {pool['mask']}")
                    config_lines.append(f" excluded-ip-address {pool['range_start']} {pool['range_end']}")
                    if pool['dns1']:
                        config_lines.append(f" dns-list {pool['dns1']}")
                        if pool['dns2']:
                            config_lines.append(f" dns-list {pool['dns2']}")
                    config_lines.append(" quit")

                    if pool['interface_type'] == "VLAN接口":
                        config_lines.append(f"interface Vlanif{pool['interface_id']}")
                    else:
                        config_lines.append(f"interface {pool['interface_id']}")
                    config_lines.append(f" dhcp select global")
                    config_lines.append(" quit")

            elif vendor == "华三":
                config_lines.append("dhcp enable")
                for pool in self.dhcp_pools:
                    config_lines.append(f"dhcp server ip-pool {pool['pool_name']}")
                    config_lines.append(f" gateway-list {pool['gateway']}")
                    config_lines.append(f" network {pool['network']} mask {pool['mask']}")
                    config_lines.append(f" forbidden-ip {pool['range_start']} to {pool['range_end']}")
                    if pool['dns1']:
                        dns_list = pool['dns1']
                        if pool['dns2']:
                            dns_list += f" {pool['dns2']}"
                        config_lines.append(f" dns-list {dns_list}")
                    config_lines.append(" quit")

                    if pool['interface_type'] == "VLAN接口":
                        config_lines.append(f"interface Vlan-interface{pool['interface_id']}")
                    else:
                        config_lines.append(f"interface {pool['interface_id']}")
                    config_lines.append(f" dhcp select server")
                    config_lines.append(" quit")

            elif vendor == "思科":
                config_lines.append("service dhcp")
                for pool in self.dhcp_pools:
                    config_lines.append(f"ip dhcp pool {pool['pool_name']}")
                    config_lines.append(f" network {pool['network']} {pool['mask']}")
                    config_lines.append(f" default-router {pool['gateway']}")
                    config_lines.append(f" excluded-address {pool['range_start']} {pool['range_end']}")
                    if pool['dns1']:
                        config_lines.append(f" dns-server {pool['dns1']}")
                        if pool['dns2']:
                            config_lines.append(f" dns-server {pool['dns2']}")
                    config_lines.append(" exit")

            elif vendor == "锐捷":
                config_lines.append("service dhcp")
                for pool in self.dhcp_pools:
                    config_lines.append(f"ip dhcp pool {pool['pool_name']}")
                    config_lines.append(f" network {pool['network']} {pool['mask']}")
                    config_lines.append(f" default-router {pool['gateway']}")
                    config_lines.append(f" excluded-address {pool['range_start']} {pool['range_end']}")
                    if pool['dns1']:
                        config_lines.append(f" dns-server {pool['dns1']}")
                        if pool['dns2']:
                            config_lines.append(f" dns-server {pool['dns2']}")
                    config_lines.append(" exit")

        # 添加IP端口绑定配置
        if self.ip_bindings:
            config_lines.append("")
            config_lines.append("! IP端口绑定配置")
            for binding in self.ip_bindings:
                if vendor == "华为":
                    config_lines.append(f"interface {binding['interface']}")
                    config_lines.append(f" user-bind static ip-address {binding['ip']} mac-address {binding['mac']}")
                    config_lines.append(" quit")
                elif vendor == "华三":
                    config_lines.append(f"interface {binding['interface']}")
                    config_lines.append(f" mac-address static {binding['mac']} ip-address {binding['ip']}")
                    config_lines.append(" quit")
                elif vendor == "思科":
                    config_lines.append(f"interface {binding['interface']}")
                    config_lines.append(f" switchport port-security mac-address {binding['mac']}")
                    config_lines.append(f" switchport port-security")
                    config_lines.append(" exit")
                elif vendor == "锐捷":
                    config_lines.append(f"interface {binding['interface']}")
                    config_lines.append(f" switchport port-security mac-address {binding['mac']}")
                    config_lines.append(f" switchport port-security")
                    config_lines.append(" exit")

        # 显示配置
        self.preview_terminal.clear()
        self.preview_terminal.append(f"=== {vendor} 交换机配置 ===")
        self.preview_terminal.append("")

        for line in config_lines:
            self.preview_terminal.append(line)

        self.preview_terminal.append("")
        self.preview_terminal.append("=== 配置结束 ===")

    def copy_config(self):
        """复制配置到剪贴板"""
        text = self.preview_terminal.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def export_config(self):
        """导出配置到文件"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                "导出配置",
                                                "",
                                                "Text Files (*.txt);;All Files (*)",
                                                options=options)
        if fileName:
            if not fileName.endswith('.txt'):
                fileName += '.txt'
            with open(fileName, 'w', encoding='utf-8') as f:
                f.write(self.preview_terminal.toPlainText())

    def clear_preview(self):
        """清空预览区域"""
        self.preview_terminal.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = SwitchConfigGenerator()
    window.show()
    sys.exit(app.exec_())