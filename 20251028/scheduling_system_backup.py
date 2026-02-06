import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QMessageBox, QHeaderView, QSpinBox, QMenuBar, QAction
)
from PyQt5.QtCore import Qt


class SchedulingSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("排课系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 当前页码和每页显示数量
        self.current_page = 1
        self.rows_per_page = 10
        
        # 数据库连接
        self.conn = sqlite3.connect('schedule.db')
        self.cursor = self.conn.cursor()
        
        # 当前管理模式
        self.management_mode = "schedule"  # 默认为排课管理
        
        # 初始化UI
        self.init_ui()
        
        # 加载下拉框数据
        self.load_combobox_data()
        
        # 加载数据
        self.load_data()

    def init_ui(self):
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 排课管理菜单
        schedule_menu = menubar.addMenu('排课管理')
        schedule_action = QAction('排课管理', self)
        schedule_action.triggered.connect(lambda: self.switch_to_management("schedule"))
        schedule_menu.addAction(schedule_action)
        
        # 学生管理菜单
        student_menu = menubar.addMenu('学生管理')
        student_action = QAction('学生管理', self)
        student_action.triggered.connect(lambda: self.switch_to_management("student"))
        student_menu.addAction(student_action)
        
        # 班级管理菜单
        class_menu = menubar.addMenu('班级管理')
        class_action = QAction('班级管理', self)
        class_action.triggered.connect(lambda: self.switch_to_management("class"))
        class_menu.addAction(class_action)
        
        # 课程管理菜单
        course_menu = menubar.addMenu('课程管理')
        course_action = QAction('课程管理', self)
        course_action.triggered.connect(lambda: self.switch_to_management("course"))
        course_menu.addAction(course_action)
        
        # 教师管理菜单
        teacher_menu = menubar.addMenu('教师管理')
        teacher_action = QAction('教师管理', self)
        teacher_action.triggered.connect(lambda: self.switch_to_management("teacher"))
        teacher_menu.addAction(teacher_action)
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # 存储当前选中的行ID
        self.selected_id = None
        
        # 初始化表格
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        # 设置默认排课管理界面
        self.setup_schedule_ui()

    def switch_to_management(self, mode):
        """切换管理模式"""
        self.management_mode = mode
        self.selected_id = None
        
        # 清空布局中的所有控件
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重新创建表格
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        # 根据不同模式设置界面
        if mode == "schedule":
            self.setup_schedule_ui()
        elif mode == "student":
            self.setup_student_ui()
        elif mode == "class":
            self.setup_class_ui()
        elif mode == "course":
            self.setup_course_ui()
        elif mode == "teacher":
            self.setup_teacher_ui()
        
        # 加载数据
        self.load_data()

    def setup_schedule_ui(self):
        """设置排课管理界面"""
        # 创建顶部操作面板
        self.top_panel = QHBoxLayout()
        
        # 班级选择
        self.top_panel.addWidget(QLabel("班级:"))
        self.class_combo = QComboBox()
        self.top_panel.addWidget(self.class_combo)
        
        # 教师选择
        self.top_panel.addWidget(QLabel("教师:"))
        self.teacher_combo = QComboBox()
        self.top_panel.addWidget(self.teacher_combo)
        
        # 课程选择
        self.top_panel.addWidget(QLabel("课程:"))
        self.course_combo = QComboBox()
        self.top_panel.addWidget(self.course_combo)
        
        # 星期选择
        self.top_panel.addWidget(QLabel("星期:"))
        self.week_spin = QSpinBox()
        self.week_spin.setMinimum(1)
        self.week_spin.setMaximum(7)
        self.top_panel.addWidget(self.week_spin)
        
        # 节次选择
        self.top_panel.addWidget(QLabel("节次:"))
        self.lesson_spin = QSpinBox()
        self.lesson_spin.setMinimum(1)
        self.lesson_spin.setMaximum(8)
        self.top_panel.addWidget(self.lesson_spin)
        
        # 备注
        self.top_panel.addWidget(QLabel("备注:"))
        self.remark_edit = QLineEdit()
        self.top_panel.addWidget(self.remark_edit)
        
        # 添加按钮
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_schedule)
        self.top_panel.addWidget(self.add_button)
        
        # 更新按钮
        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.update_schedule)
        self.update_button.setEnabled(False)
        self.top_panel.addWidget(self.update_button)
        
        # 删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_schedule)
        self.delete_button.setEnabled(False)
        self.top_panel.addWidget(self.delete_button)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        # 查询输入框
        query_panel.addWidget(QLabel("查询:"))
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入任意关键字查询")
        query_panel.addWidget(self.query_input)
        
        # 查询按钮
        self.query_button = QPushButton("查询")
        self.query_button.clicked.connect(self.query_schedule)
        query_panel.addWidget(self.query_button)
        
        # 按班级查询按钮
        self.query_by_class_button = QPushButton("按班级查询")
        self.query_by_class_button.clicked.connect(self.query_by_class)
        query_panel.addWidget(self.query_by_class_button)
        
        # 按教师查询按钮
        self.query_by_teacher_button = QPushButton("按教师查询")
        self.query_by_teacher_button.clicked.connect(self.query_by_teacher)
        query_panel.addWidget(self.query_by_teacher_button)
        
        # 显示所有按钮
        self.show_all_button = QPushButton("显示所有")
        self.show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.show_all_button)
        
        # 设置表格列
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "班级", "教师", "课程", "星期", "节次", "备注", "操作"])
        
        # 将控件添加到主布局
        self.main_layout.addLayout(self.top_panel)
        self.main_layout.addLayout(query_panel)
        self.main_layout.addWidget(self.table)
        
        # 创建底部翻页控件
        self.setup_pagination()

    def setup_student_ui(self):
        """设置学生管理界面"""
        # 创建顶部操作面板
        self.top_panel = QHBoxLayout()
        
        # 姓名
        self.top_panel.addWidget(QLabel("姓名:"))
        self.student_name_edit = QLineEdit()
        self.top_panel.addWidget(self.student_name_edit)
        
        # 性别
        self.top_panel.addWidget(QLabel("性别:"))
        self.student_sex_edit = QLineEdit()
        self.top_panel.addWidget(self.student_sex_edit)
        
        # 班级
        self.top_panel.addWidget(QLabel("班级:"))
        self.student_class_combo = QComboBox()
        self.top_panel.addWidget(self.student_class_combo)
        
        # 添加按钮
        self.add_student_button = QPushButton("添加")
        self.add_student_button.clicked.connect(self.add_student)
        self.top_panel.addWidget(self.add_student_button)
        
        # 更新按钮
        self.update_student_button = QPushButton("更新")
        self.update_student_button.clicked.connect(self.update_student)
        self.update_student_button.setEnabled(False)
        self.top_panel.addWidget(self.update_student_button)
        
        # 删除按钮
        self.delete_student_button = QPushButton("删除")
        self.delete_student_button.clicked.connect(self.delete_student)
        self.delete_student_button.setEnabled(False)
        self.top_panel.addWidget(self.delete_student_button)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        # 查询输入框
        query_panel.addWidget(QLabel("查询:"))
        self.student_query_input = QLineEdit()
        self.student_query_input.setPlaceholderText("输入学生姓名或班级查询")
        query_panel.addWidget(self.student_query_input)
        
        # 查询按钮
        self.student_query_button = QPushButton("查询")
        self.student_query_button.clicked.connect(self.query_student)
        query_panel.addWidget(self.student_query_button)
        
        # 显示所有按钮
        self.student_show_all_button = QPushButton("显示所有")
        self.student_show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.student_show_all_button)
        
        # 设置表格列
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "班级", "操作", ""])
        
        # 将控件添加到主布局
        self.main_layout.addLayout(self.top_panel)
        self.main_layout.addLayout(query_panel)
        self.main_layout.addWidget(self.table)
        
        # 创建底部翻页控件
        self.setup_pagination()

    def setup_class_ui(self):
        """设置班级管理界面"""
        # 创建顶部操作面板
        self.top_panel = QHBoxLayout()
        
        # 班级名称
        self.top_panel.addWidget(QLabel("班级名称:"))
        self.class_name_edit = QLineEdit()
        self.top_panel.addWidget(self.class_name_edit)
        
        # 人数
        self.top_panel.addWidget(QLabel("人数:"))
        self.class_number_edit = QLineEdit()
        self.top_panel.addWidget(self.class_number_edit)
        
        # 添加按钮
        self.add_class_button = QPushButton("添加")
        self.add_class_button.clicked.connect(self.add_class)
        self.top_panel.addWidget(self.add_class_button)
        
        # 更新按钮
        self.update_class_button = QPushButton("更新")
        self.update_class_button.clicked.connect(self.update_class)
        self.update_class_button.setEnabled(False)
        self.top_panel.addWidget(self.update_class_button)
        
        # 删除按钮
        self.delete_class_button = QPushButton("删除")
        self.delete_class_button.clicked.connect(self.delete_class)
        self.delete_class_button.setEnabled(False)
        self.top_panel.addWidget(self.delete_class_button)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        # 查询输入框
        query_panel.addWidget(QLabel("查询:"))
        self.class_query_input = QLineEdit()
        self.class_query_input.setPlaceholderText("输入班级名称查询")
        query_panel.addWidget(self.class_query_input)
        
        # 查询按钮
        self.class_query_button = QPushButton("查询")
        self.class_query_button.clicked.connect(self.query_class)
        query_panel.addWidget(self.class_query_button)
        
        # 显示所有按钮
        self.class_show_all_button = QPushButton("显示所有")
        self.class_show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.class_show_all_button)
        
        # 设置表格列
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "班级名称", "人数", "操作", ""])
        
        # 将控件添加到主布局
        self.main_layout.addLayout(self.top_panel)
        self.main_layout.addLayout(query_panel)
        self.main_layout.addWidget(self.table)
        
        # 创建底部翻页控件
        self.setup_pagination()

    def setup_course_ui(self):
        """设置课程管理界面"""
        # 创建顶部操作面板
        self.top_panel = QHBoxLayout()
        
        # 课程名称
        self.top_panel.addWidget(QLabel("课程名称:"))
        self.course_name_edit = QLineEdit()
        self.top_panel.addWidget(self.course_name_edit)
        
        # 添加按钮
        self.add_course_button = QPushButton("添加")
        self.add_course_button.clicked.connect(self.add_course)
        self.top_panel.addWidget(self.add_course_button)
        
        # 更新按钮
        self.update_course_button = QPushButton("更新")
        self.update_course_button.clicked.connect(self.update_course)
        self.update_course_button.setEnabled(False)
        self.top_panel.addWidget(self.update_course_button)
        
        # 删除按钮
        self.delete_course_button = QPushButton("删除")
        self.delete_course_button.clicked.connect(self.delete_course)
        self.delete_course_button.setEnabled(False)
        self.top_panel.addWidget(self.delete_course_button)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        # 查询输入框
        query_panel.addWidget(QLabel("查询:"))
        self.course_query_input = QLineEdit()
        self.course_query_input.setPlaceholderText("输入课程名称查询")
        query_panel.addWidget(self.course_query_input)
        
        # 查询按钮
        self.course_query_button = QPushButton("查询")
        self.course_query_button.clicked.connect(self.query_course)
        query_panel.addWidget(self.course_query_button)
        
        # 显示所有按钮
        self.course_show_all_button = QPushButton("显示所有")
        self.course_show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.course_show_all_button)
        
        # 设置表格列
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "课程名称", "操作", ""])
        
        # 将控件添加到主布局
        self.main_layout.addLayout(self.top_panel)
        self.main_layout.addLayout(query_panel)
        self.main_layout.addWidget(self.table)
        
        # 创建底部翻页控件
        self.setup_pagination()

    def setup_teacher_ui(self):
        """设置教师管理界面"""
        # 创建顶部操作面板
        self.top_panel = QHBoxLayout()
        
        # 姓名
        self.top_panel.addWidget(QLabel("姓名:"))
        self.teacher_name_edit = QLineEdit()
        self.top_panel.addWidget(self.teacher_name_edit)
        
        # 性别
        self.top_panel.addWidget(QLabel("性别:"))
        self.teacher_sex_edit = QLineEdit()
        self.top_panel.addWidget(self.teacher_sex_edit)
        
        # 年龄
        self.top_panel.addWidget(QLabel("年龄:"))
        self.teacher_age_edit = QLineEdit()
        self.top_panel.addWidget(self.teacher_age_edit)
        
        # 添加按钮
        self.add_teacher_button = QPushButton("添加")
        self.add_teacher_button.clicked.connect(self.add_teacher)
        self.top_panel.addWidget(self.add_teacher_button)
        
        # 更新按钮
        self.update_teacher_button = QPushButton("更新")
        self.update_teacher_button.clicked.connect(self.update_teacher)
        self.update_teacher_button.setEnabled(False)
        self.top_panel.addWidget(self.update_teacher_button)
        
        # 删除按钮
        self.delete_teacher_button = QPushButton("删除")
        self.delete_teacher_button.clicked.connect(self.delete_teacher)
        self.delete_teacher_button.setEnabled(False)
        self.top_panel.addWidget(self.delete_teacher_button)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        # 查询输入框
        query_panel.addWidget(QLabel("查询:"))
        self.teacher_query_input = QLineEdit()
        self.teacher_query_input.setPlaceholderText("输入教师姓名查询")
        query_panel.addWidget(self.teacher_query_input)
        
        # 查询按钮
        self.teacher_query_button = QPushButton("查询")
        self.teacher_query_button.clicked.connect(self.query_teacher)
        query_panel.addWidget(self.teacher_query_button)
        
        # 显示所有按钮
        self.teacher_show_all_button = QPushButton("显示所有")
        self.teacher_show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.teacher_show_all_button)
        
        # 设置表格列
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "年龄", "操作"])
        
        # 将控件添加到主布局
        self.main_layout.addLayout(self.top_panel)
        self.main_layout.addLayout(query_panel)
        self.main_layout.addWidget(self.table)
        
        # 创建底部翻页控件
        self.setup_pagination()

    def setup_pagination(self):
        """设置分页控件"""
        # 创建底部翻页控件
        bottom_panel = QHBoxLayout()
        
        self.first_page_button = QPushButton("首页")
        self.first_page_button.clicked.connect(self.first_page)
        bottom_panel.addWidget(self.first_page_button)
        
        self.prev_page_button = QPushButton("上一页")
        self.prev_page_button.clicked.connect(self.prev_page)
        bottom_panel.addWidget(self.prev_page_button)
        
        self.page_label = QLabel()
        bottom_panel.addWidget(self.page_label)
        
        self.next_page_button = QPushButton("下一页")
        self.next_page_button.clicked.connect(self.next_page)
        bottom_panel.addWidget(self.next_page_button)
        
        self.last_page_button = QPushButton("末页")
        self.last_page_button.clicked.connect(self.last_page)
        bottom_panel.addWidget(self.last_page_button)
        
        self.main_layout.addLayout(bottom_panel)

    def load_combobox_data(self):
        """加载下拉框数据"""
        # 清空现有数据
        if hasattr(self, 'class_combo'):
            self.class_combo.clear()
        if hasattr(self, 'teacher_combo'):
            self.teacher_combo.clear()
        if hasattr(self, 'course_combo'):
            self.course_combo.clear()
        if hasattr(self, 'student_class_combo'):
            self.student_class_combo.clear()
        
        # 加载班级数据
        self.cursor.execute("SELECT id, classname FROM class")
        classes = self.cursor.fetchall()
        self.class_dict = {cls[1]: cls[0] for cls in classes}  # 名称到ID的映射
        self.class_list = classes  # ID到名称的映射
        
        if hasattr(self, 'class_combo'):
            self.class_combo.addItem("请选择")
            for cls in classes:
                self.class_combo.addItem(cls[1])
        
        if hasattr(self, 'student_class_combo'):
            self.student_class_combo.addItem("请选择")
            for cls in classes:
                self.student_class_combo.addItem(cls[1])
            
        # 加载教师数据
        self.cursor.execute("SELECT id, name FROM teacher")
        teachers = self.cursor.fetchall()
        self.teacher_dict = {teacher[1]: teacher[0] for teacher in teachers}  # 名称到ID的映射
        self.teacher_list = teachers  # ID到名称的映射
        
        if hasattr(self, 'teacher_combo'):
            self.teacher_combo.addItem("请选择")
            for teacher in teachers:
                self.teacher_combo.addItem(teacher[1])
            
        # 加载课程数据
        self.cursor.execute("SELECT id, coursename FROM course")
        courses = self.cursor.fetchall()
        self.course_dict = {course[1]: course[0] for course in courses}  # 名称到ID的映射
        self.course_list = courses  # ID到名称的映射
        
        if hasattr(self, 'course_combo'):
            self.course_combo.addItem("请选择")
            for course in courses:
                self.course_combo.addItem(course[1])

    def load_data(self, query_sql=None, params=None):
        """加载数据"""
        # 根据管理模式加载不同数据
        if self.management_mode == "schedule":
            self.load_schedule_data(query_sql, params)
        elif self.management_mode == "student":
            self.load_student_data(query_sql, params)
        elif self.management_mode == "class":
            self.load_class_data(query_sql, params)
        elif self.management_mode == "course":
            self.load_course_data(query_sql, params)
        elif self.management_mode == "teacher":
            self.load_teacher_data(query_sql, params)

    def load_schedule_data(self, query_sql=None, params=None):
        """加载排课数据"""
        # 如果提供了查询SQL，则使用查询SQL，否则使用默认查询
        if query_sql:
            # 计算查询结果总数
            count_sql = query_sql.replace("SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark", 
                                          "SELECT COUNT(*)")
            # 移除ORDER BY和LIMIT子句以计算总数
            if "ORDER BY" in count_sql:
                count_sql = count_sql[:count_sql.index("ORDER BY")]
            if "LIMIT" in count_sql:
                count_sql = count_sql[:count_sql.index("LIMIT")]
                
            self.cursor.execute(count_sql, params if params else ())
            total_records = self.cursor.fetchone()[0]
        else:
            # 计算总记录数
            self.cursor.execute("SELECT COUNT(*) FROM schedule")
            total_records = self.cursor.fetchone()[0]
            
        self.total_pages = (total_records + self.rows_per_page - 1) // self.rows_per_page
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1
            
        # 查询当前页数据
        offset = (self.current_page - 1) * self.rows_per_page
        if query_sql:
            # 添加分页到查询SQL
            paginated_query = query_sql + " LIMIT ? OFFSET ?"
            params_with_pagination = (params if params else ()) + (self.rows_per_page, offset)
            self.cursor.execute(paginated_query, params_with_pagination)
        else:
            self.cursor.execute("""
                SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark
                FROM schedule s
                JOIN class c ON s.class_id = c.id
                JOIN teacher t ON s.teacher_id = t.id
                JOIN course co ON s.course_id = co.id
                ORDER BY s.id
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
        
        rows = self.cursor.fetchall()
        
        # 更新表格
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(row_idx, col_idx, item)
                
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)  # 减小按钮间距，避免字体重叠
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_schedule_row(rid))
            edit_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_schedule_row(rid))
            delete_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 7, btn_widget)
        
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def load_student_data(self, query_sql=None, params=None):
        """加载学生数据"""
        # 如果提供了查询SQL，则使用查询SQL，否则使用默认查询
        if query_sql:
            # 计算查询结果总数
            count_sql = query_sql.replace("SELECT s.id, s.name, s.sex, c.classname", 
                                          "SELECT COUNT(*)")
            # 移除ORDER BY和LIMIT子句以计算总数
            if "ORDER BY" in count_sql:
                count_sql = count_sql[:count_sql.index("ORDER BY")]
            if "LIMIT" in count_sql:
                count_sql = count_sql[:count_sql.index("LIMIT")]
                
            self.cursor.execute(count_sql, params if params else ())
            total_records = self.cursor.fetchone()[0]
        else:
            # 计算总记录数
            self.cursor.execute("SELECT COUNT(*) FROM student s JOIN class c ON s.class_id = c.id")
            total_records = self.cursor.fetchone()[0]
            
        self.total_pages = (total_records + self.rows_per_page - 1) // self.rows_per_page
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1
            
        # 查询当前页数据
        offset = (self.current_page - 1) * self.rows_per_page
        if query_sql:
            # 添加分页到查询SQL
            paginated_query = query_sql + " LIMIT ? OFFSET ?"
            params_with_pagination = (params if params else ()) + (self.rows_per_page, offset)
            self.cursor.execute(paginated_query, params_with_pagination)
        else:
            self.cursor.execute("""
                SELECT s.id, s.name, s.sex, c.classname
                FROM student s
                JOIN class c ON s.class_id = c.id
                ORDER BY s.id
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
        
        rows = self.cursor.fetchall()
        
        # 更新表格
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(row_idx, col_idx, item)
                
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)  # 减小按钮间距，避免字体重叠
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_student_row(rid))
            edit_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_student_row(rid))
            delete_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 4, btn_widget)
            
            # 添加一个空列来保持布局一致
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 5, empty_item)
        
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def load_class_data(self, query_sql=None, params=None):
        """加载班级数据"""
        # 如果提供了查询SQL，则使用查询SQL，否则使用默认查询
        if query_sql:
            # 计算查询结果总数
            count_sql = query_sql.replace("SELECT id, classname, number", 
                                          "SELECT COUNT(*)")
            # 移除ORDER BY和LIMIT子句以计算总数
            if "ORDER BY" in count_sql:
                count_sql = count_sql[:count_sql.index("ORDER BY")]
            if "LIMIT" in count_sql:
                count_sql = count_sql[:count_sql.index("LIMIT")]
                
            self.cursor.execute(count_sql, params if params else ())
            total_records = self.cursor.fetchone()[0]
        else:
            # 计算总记录数
            self.cursor.execute("SELECT COUNT(*) FROM class")
            total_records = self.cursor.fetchone()[0]
            
        self.total_pages = (total_records + self.rows_per_page - 1) // self.rows_per_page
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1
            
        # 查询当前页数据
        offset = (self.current_page - 1) * self.rows_per_page
        if query_sql:
            # 添加分页到查询SQL
            paginated_query = query_sql + " LIMIT ? OFFSET ?"
            params_with_pagination = (params if params else ()) + (self.rows_per_page, offset)
            self.cursor.execute(paginated_query, params_with_pagination)
        else:
            self.cursor.execute("""
                SELECT id, classname, number
                FROM class
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
        
        rows = self.cursor.fetchall()
        
        # 更新表格
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(row_idx, col_idx, item)
                
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)  # 减小按钮间距，避免字体重叠
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_class_row(rid))
            edit_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_class_row(rid))
            delete_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 3, btn_widget)
            
            # 添加一个空列来保持布局一致
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 4, empty_item)
        
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def load_course_data(self, query_sql=None, params=None):
        """加载课程数据"""
        # 如果提供了查询SQL，则使用查询SQL，否则使用默认查询
        if query_sql:
            # 计算查询结果总数
            count_sql = query_sql.replace("SELECT id, coursename", 
                                          "SELECT COUNT(*)")
            # 移除ORDER BY和LIMIT子句以计算总数
            if "ORDER BY" in count_sql:
                count_sql = count_sql[:count_sql.index("ORDER BY")]
            if "LIMIT" in count_sql:
                count_sql = count_sql[:count_sql.index("LIMIT")]
                
            self.cursor.execute(count_sql, params if params else ())
            total_records = self.cursor.fetchone()[0]
        else:
            # 计算总记录数
            self.cursor.execute("SELECT COUNT(*) FROM course")
            total_records = self.cursor.fetchone()[0]
            
        self.total_pages = (total_records + self.rows_per_page - 1) // self.rows_per_page
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1
            
        # 查询当前页数据
        offset = (self.current_page - 1) * self.rows_per_page
        if query_sql:
            # 添加分页到查询SQL
            paginated_query = query_sql + " LIMIT ? OFFSET ?"
            params_with_pagination = (params if params else ()) + (self.rows_per_page, offset)
            self.cursor.execute(paginated_query, params_with_pagination)
        else:
            self.cursor.execute("""
                SELECT id, coursename
                FROM course
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
        
        rows = self.cursor.fetchall()
        
        # 更新表格
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(row_idx, col_idx, item)
                
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)  # 减小按钮间距，避免字体重叠
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_course_row(rid))
            edit_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_course_row(rid))
            delete_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 2, btn_widget)
            
            # 添加两个空列来保持布局一致
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 3, empty_item)
            
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def load_teacher_data(self, query_sql=None, params=None):
        """加载教师数据"""
        # 如果提供了查询SQL，则使用查询SQL，否则使用默认查询
        if query_sql:
            # 计算查询结果总数
            count_sql = query_sql.replace("SELECT id, name, sex, age", 
                                          "SELECT COUNT(*)")
            # 移除ORDER BY和LIMIT子句以计算总数
            if "ORDER BY" in count_sql:
                count_sql = count_sql[:count_sql.index("ORDER BY")]
            if "LIMIT" in count_sql:
                count_sql = count_sql[:count_sql.index("LIMIT")]
                
            self.cursor.execute(count_sql, params if params else ())
            total_records = self.cursor.fetchone()[0]
        else:
            # 计算总记录数
            self.cursor.execute("SELECT COUNT(*) FROM teacher")
            total_records = self.cursor.fetchone()[0]
            
        self.total_pages = (total_records + self.rows_per_page - 1) // self.rows_per_page
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        elif self.current_page < 1:
            self.current_page = 1
            
        # 查询当前页数据
        offset = (self.current_page - 1) * self.rows_per_page
        if query_sql:
            # 添加分页到查询SQL
            paginated_query = query_sql + " LIMIT ? OFFSET ?"
            params_with_pagination = (params if params else ()) + (self.rows_per_page, offset)
            self.cursor.execute(paginated_query, params_with_pagination)
        else:
            self.cursor.execute("""
                SELECT id, name, sex, age
                FROM teacher
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (self.rows_per_page, offset))
        
        rows = self.cursor.fetchall()
        
        # 更新表格
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(row_idx, col_idx, item)
                
            # 添加操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)  # 减小按钮间距，避免字体重叠
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_teacher_row(rid))
            edit_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_teacher_row(rid))
            delete_btn.setFixedWidth(40)  # 设置固定宽度避免重叠
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 4, btn_widget)
        
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def on_table_selection_changed(self):
        """表格选择改变事件"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_id = int(self.table.item(row, 0).text())
            
            # 根据管理模式启用/禁用按钮
            if self.management_mode == "schedule":
                self.update_button.setEnabled(True)
                self.delete_button.setEnabled(True)
            elif self.management_mode == "student":
                self.update_student_button.setEnabled(True)
                self.delete_student_button.setEnabled(True)
            elif self.management_mode == "class":
                self.update_class_button.setEnabled(True)
                self.delete_class_button.setEnabled(True)
            elif self.management_mode == "course":
                self.update_course_button.setEnabled(True)
                self.delete_course_button.setEnabled(True)
            elif self.management_mode == "teacher":
                self.update_teacher_button.setEnabled(True)
                self.delete_teacher_button.setEnabled(True)
        else:
            self.selected_id = None
            
            # 根据管理模式启用/禁用按钮
            if self.management_mode == "schedule":
                self.update_button.setEnabled(False)
                self.delete_button.setEnabled(False)
            elif self.management_mode == "student":
                self.update_student_button.setEnabled(False)
                self.delete_student_button.setEnabled(False)
            elif self.management_mode == "class":
                self.update_class_button.setEnabled(False)
                self.delete_class_button.setEnabled(False)
            elif self.management_mode == "course":
                self.update_course_button.setEnabled(False)
                self.delete_course_button.setEnabled(False)
            elif self.management_mode == "teacher":
                self.update_teacher_button.setEnabled(False)
                self.delete_teacher_button.setEnabled(False)

    # 排课管理相关方法
    def edit_schedule_row(self, record_id):
        """编辑排课行"""
        self.selected_id = record_id
        # 获取该行数据
        self.cursor.execute("""
            SELECT s.class_id, s.teacher_id, s.course_id, s.weeks, s.lessons, s.remark, 
                   c.classname, t.name, co.coursename
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN teacher t ON s.teacher_id = t.id
            JOIN course co ON s.course_id = co.id
            WHERE s.id = ?
        """, (record_id,))
        
        data = self.cursor.fetchone()
        if data:
            # 填充表单
            class_index = self.class_combo.findText(data[6])  # classname
            self.class_combo.setCurrentIndex(class_index)
            
            teacher_index = self.teacher_combo.findText(data[7])  # teacher name
            self.teacher_combo.setCurrentIndex(teacher_index)
            
            course_index = self.course_combo.findText(data[8])  # course name
            self.course_combo.setCurrentIndex(course_index)
            
            self.week_spin.setValue(data[3])  # weeks
            self.lesson_spin.setValue(data[4])  # lessons
            self.remark_edit.setText(data[5])  # remark

    def delete_schedule_row(self, record_id):
        """删除排课行"""
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM schedule WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            QMessageBox.information(self, '提示', '删除成功！')

    def add_schedule(self):
        """添加排课"""
        # 检查是否选择了必选项
        if self.class_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择班级！')
            return
            
        if self.teacher_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择教师！')
            return
            
        if self.course_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择课程！')
            return
            
        class_name = self.class_combo.currentText()
        teacher_name = self.teacher_combo.currentText()
        course_name = self.course_combo.currentText()
        weeks = self.week_spin.value()
        lessons = self.lesson_spin.value()
        remark = self.remark_edit.text()
        
        class_id = self.class_dict[class_name]
        teacher_id = self.teacher_dict[teacher_name]
        course_id = self.course_dict[course_name]
        
        # 检查是否有时间冲突（同一个班级在同一个星期和节次不能有重复排课）
        self.cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE class_id = ? AND weeks = ? AND lessons = ?
        """, (class_id, weeks, lessons))
        
        conflict_count = self.cursor.fetchone()[0]
        if conflict_count > 0:
            QMessageBox.warning(self, '警告', '该班级在该时间段已有排课，无法添加排课！')
            return
            
        # 插入数据
        self.cursor.execute("""
            INSERT INTO schedule (class_id, teacher_id, course_id, weeks, lessons, remark)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (class_id, teacher_id, course_id, weeks, lessons, remark))
        
        self.conn.commit()
        self.load_data()
        self.clear_schedule_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_schedule(self):
        """更新排课"""
        if not self.selected_id:
            return
            
        # 检查是否选择了必选项
        if self.class_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择班级！')
            return
            
        if self.teacher_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择教师！')
            return
            
        if self.course_combo.currentIndex() == 0:
            QMessageBox.warning(self, '警告', '请选择课程！')
            return
            
        class_name = self.class_combo.currentText()
        teacher_name = self.teacher_combo.currentText()
        course_name = self.course_combo.currentText()
        weeks = self.week_spin.value()
        lessons = self.lesson_spin.value()
        remark = self.remark_edit.text()
        
        class_id = self.class_dict[class_name]
        teacher_id = self.teacher_dict[teacher_name]
        course_id = self.course_dict[course_name]
        
        # 检查是否有时间冲突（同一个班级在同一个星期和节次不能有重复排课，排除自己）
        self.cursor.execute("""
            SELECT COUNT(*) FROM schedule 
            WHERE class_id = ? AND weeks = ? AND lessons = ? AND id != ?
        """, (class_id, weeks, lessons, self.selected_id))
        
        conflict_count = self.cursor.fetchone()[0]
        if conflict_count > 0:
            QMessageBox.warning(self, '警告', '该班级在该时间段已有排课，无法更新排课！')
            return
            
        # 更新数据
        self.cursor.execute("""
            UPDATE schedule 
            SET class_id = ?, teacher_id = ?, course_id = ?, weeks = ?, lessons = ?, remark = ?
            WHERE id = ?
        """, (class_id, teacher_id, course_id, weeks, lessons, remark, self.selected_id))
        
        self.conn.commit()
        self.load_data()
        self.clear_schedule_form()
        self.selected_id = None
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_schedule(self):
        """删除排课"""
        if not self.selected_id:
            return
            
        self.delete_schedule_row(self.selected_id)

    def clear_schedule_form(self):
        """清空排课表单"""
        self.class_combo.setCurrentIndex(0)
        self.teacher_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.week_spin.setValue(1)
        self.lesson_spin.setValue(1)
        self.remark_edit.clear()

    def query_schedule(self):
        """根据输入的关键字查询"""
        keyword = self.query_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, '警告', '请输入查询关键字！')
            return
            
        # 构建查询SQL，查询所有字段
        query_sql = """
            SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN teacher t ON s.teacher_id = t.id
            JOIN course co ON s.course_id = co.id
            WHERE c.classname LIKE ? OR t.name LIKE ? OR co.coursename LIKE ? OR s.remark LIKE ?
            ORDER BY s.id
        """
        
        # 参数：在每个字段中搜索关键字
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    def query_by_class(self):
        """根据班级查询"""
        class_name = self.class_combo.currentText()
        if class_name == "请选择" or not class_name:
            QMessageBox.warning(self, '警告', '请选择班级！')
            return
            
        class_id = self.class_dict[class_name]
        
        # 构建查询SQL，按班级查询并按星期和节次排序
        query_sql = """
            SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN teacher t ON s.teacher_id = t.id
            JOIN course co ON s.course_id = co.id
            WHERE s.class_id = ?
            ORDER BY s.weeks ASC, s.lessons ASC
        """
        
        # 参数
        params = (class_id,)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    def query_by_teacher(self):
        """根据教师查询"""
        teacher_name = self.teacher_combo.currentText()
        if teacher_name == "请选择" or not teacher_name:
            QMessageBox.warning(self, '警告', '请选择教师！')
            return
            
        teacher_id = self.teacher_dict[teacher_name]
        
        # 构建查询SQL，按教师查询并按星期和节次排序
        query_sql = """
            SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark
            FROM schedule s
            JOIN class c ON s.class_id = c.id
            JOIN teacher t ON s.teacher_id = t.id
            JOIN course co ON s.course_id = co.id
            WHERE s.teacher_id = ?
            ORDER BY s.weeks ASC, s.lessons ASC
        """
        
        # 参数
        params = (teacher_id,)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    # 学生管理相关方法
    def edit_student_row(self, record_id):
        """编辑学生行"""
        self.selected_id = record_id
        # 获取该行数据
        self.cursor.execute("""
            SELECT s.name, s.sex, c.classname
            FROM student s
            JOIN class c ON s.class_id = c.id
            WHERE s.id = ?
        """, (record_id,))
        
        data = self.cursor.fetchone()
        if data:
            # 填充表单
            self.student_name_edit.setText(data[0])
            self.student_sex_edit.setText(data[1])
            
            class_index = self.student_class_combo.findText(data[2])
            self.student_class_combo.setCurrentIndex(class_index)
            # 如果找不到匹配项，尝试直接设置文本（解决下拉框无法选择的问题）
            if class_index == -1 and data[2]:
                # 确保下拉框中有这个班级选项
                all_items = [self.student_class_combo.itemText(i) for i in range(self.student_class_combo.count())]
                if data[2] not in all_items:
                    self.student_class_combo.addItem(data[2])
                self.student_class_combo.setCurrentText(data[2])

    def delete_student_row(self, record_id):
        """删除学生行"""
        # 检查是否被排课表引用
        self.cursor.execute("SELECT COUNT(*) FROM schedule WHERE class_id IN (SELECT class_id FROM student WHERE id = ?)", (record_id,))
        reference_count = self.cursor.fetchone()[0]
        
        if reference_count > 0:
            QMessageBox.warning(self, '警告', '该数据已被引用，先去排课表中删除相关记录！')
            return
        
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM student WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            QMessageBox.information(self, '提示', '删除成功！')

    def add_student(self):
        """添加学生"""
        name = self.student_name_edit.text().strip()
        sex = self.student_sex_edit.text().strip()
        class_name = self.student_class_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, '警告', '请输入学生姓名！')
            return
            
        if not sex:
            QMessageBox.warning(self, '警告', '请输入学生性别！')
            return
            
        if class_name == "请选择" or not class_name:
            QMessageBox.warning(self, '警告', '请选择班级！')
            return
            
        class_id = self.class_dict[class_name]
        
        # 插入数据
        self.cursor.execute("""
            INSERT INTO student (name, sex, class_id)
            VALUES (?, ?, ?)
        """, (name, sex, class_id))
        
        self.conn.commit()
        self.load_data()
        self.clear_student_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_student(self):
        """更新学生"""
        if not self.selected_id:
            return
            
        name = self.student_name_edit.text().strip()
        sex = self.student_sex_edit.text().strip()
        class_name = self.student_class_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, '警告', '请输入学生姓名！')
            return
            
        if not sex:
            QMessageBox.warning(self, '警告', '请输入学生性别！')
            return
            
        if class_name == "请选择" or not class_name:
            QMessageBox.warning(self, '警告', '请选择班级！')
            return
            
        class_id = self.class_dict[class_name]
        
        # 更新数据
        self.cursor.execute("""
            UPDATE student 
            SET name = ?, sex = ?, class_id = ?
            WHERE id = ?
        """, (name, sex, class_id, self.selected_id))
        
        self.conn.commit()
        self.load_data()
        self.clear_student_form()
        self.selected_id = None
        self.update_student_button.setEnabled(False)
        self.delete_student_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_student(self):
        """删除学生"""
        if not self.selected_id:
            return
            
        self.delete_student_row(self.selected_id)

    def clear_student_form(self):
        """清空学生表单"""
        self.student_name_edit.clear()
        self.student_sex_edit.clear()
        self.student_class_combo.setCurrentIndex(0)

    def query_student(self):
        """查询学生"""
        keyword = self.student_query_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, '警告', '请输入查询关键字！')
            return
            
        # 构建查询SQL
        query_sql = """
            SELECT s.id, s.name, s.sex, c.classname
            FROM student s
            JOIN class c ON s.class_id = c.id
            WHERE s.name LIKE ? OR c.classname LIKE ?
            ORDER BY s.id
        """
        
        # 参数
        params = (f"%{keyword}%", f"%{keyword}%")
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    # 班级管理相关方法
    def edit_class_row(self, record_id):
        """编辑班级行"""
        self.selected_id = record_id
        # 获取该行数据
        self.cursor.execute("SELECT classname, number FROM class WHERE id = ?", (record_id,))
        data = self.cursor.fetchone()
        if data:
            # 填充表单
            self.class_name_edit.setText(data[0])
            self.class_number_edit.setText(str(data[1]))

    def delete_class_row(self, record_id):
        """删除班级行"""
        # 检查是否被学生表或排课表引用
        self.cursor.execute("SELECT COUNT(*) FROM student WHERE class_id = ?", (record_id,))
        student_reference_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM schedule WHERE class_id = ?", (record_id,))
        schedule_reference_count = self.cursor.fetchone()[0]
        
        if student_reference_count > 0 or schedule_reference_count > 0:
            QMessageBox.warning(self, '警告', '该数据已被引用，先去相关表中删除引用记录！')
            return
        
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM class WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            self.load_combobox_data()  # 重新加载下拉框数据
            QMessageBox.information(self, '提示', '删除成功！')

    def add_class(self):
        """添加班级"""
        classname = self.class_name_edit.text().strip()
        number_text = self.class_number_edit.text().strip()
        
        if not classname:
            QMessageBox.warning(self, '警告', '请输入班级名称！')
            return
            
        if not number_text:
            QMessageBox.warning(self, '警告', '请输入班级人数！')
            return
            
        try:
            number = int(number_text)
        except ValueError:
            QMessageBox.warning(self, '警告', '班级人数必须是数字！')
            return
        
        # 检查班级名称是否已存在
        self.cursor.execute("SELECT COUNT(*) FROM class WHERE classname = ?", (classname,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '班级名称已存在！')
            return
        
        # 插入数据
        self.cursor.execute("""
            INSERT INTO class (classname, number)
            VALUES (?, ?)
        """, (classname, number))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_class_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_class(self):
        """更新班级"""
        if not self.selected_id:
            return
            
        classname = self.class_name_edit.text().strip()
        number_text = self.class_number_edit.text().strip()
        
        if not classname:
            QMessageBox.warning(self, '警告', '请输入班级名称！')
            return
            
        if not number_text:
            QMessageBox.warning(self, '警告', '请输入班级人数！')
            return
            
        try:
            number = int(number_text)
        except ValueError:
            QMessageBox.warning(self, '警告', '班级人数必须是数字！')
            return
        
        # 检查班级名称是否已存在（排除自己）
        self.cursor.execute("SELECT COUNT(*) FROM class WHERE classname = ? AND id != ?", (classname, self.selected_id))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '班级名称已存在！')
            return
        
        # 更新数据
        self.cursor.execute("""
            UPDATE class 
            SET classname = ?, number = ?
            WHERE id = ?
        """, (classname, number, self.selected_id))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_class_form()
        self.selected_id = None
        self.update_class_button.setEnabled(False)
        self.delete_class_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_class(self):
        """删除班级"""
        if not self.selected_id:
            return
            
        self.delete_class_row(self.selected_id)

    def clear_class_form(self):
        """清空班级表单"""
        self.class_name_edit.clear()
        self.class_number_edit.clear()

    def query_class(self):
        """查询班级"""
        keyword = self.class_query_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, '警告', '请输入查询关键字！')
            return
            
        # 构建查询SQL
        query_sql = """
            SELECT id, classname, number
            FROM class
            WHERE classname LIKE ?
            ORDER BY id
        """
        
        # 参数
        params = (f"%{keyword}%",)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    # 课程管理相关方法
    def edit_course_row(self, record_id):
        """编辑课程行"""
        self.selected_id = record_id
        # 获取该行数据
        self.cursor.execute("SELECT coursename FROM course WHERE id = ?", (record_id,))
        data = self.cursor.fetchone()
        if data:
            # 填充表单
            self.course_name_edit.setText(data[0])

    def delete_course_row(self, record_id):
        """删除课程行"""
        # 检查是否被排课表引用
        self.cursor.execute("SELECT COUNT(*) FROM schedule WHERE course_id = ?", (record_id,))
        reference_count = self.cursor.fetchone()[0]
        
        if reference_count > 0:
            QMessageBox.warning(self, '警告', '该数据已被引用，先去排课表中删除相关记录！')
            return
        
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM course WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            self.load_combobox_data()  # 重新加载下拉框数据
            QMessageBox.information(self, '提示', '删除成功！')

    def add_course(self):
        """添加课程"""
        coursename = self.course_name_edit.text().strip()
        
        if not coursename:
            QMessageBox.warning(self, '警告', '请输入课程名称！')
            return
        
        # 检查课程名称是否已存在
        self.cursor.execute("SELECT COUNT(*) FROM course WHERE coursename = ?", (coursename,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '课程名称已存在！')
            return
        
        # 插入数据
        self.cursor.execute("""
            INSERT INTO course (coursename)
            VALUES (?)
        """, (coursename,))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_course_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_course(self):
        """更新课程"""
        if not self.selected_id:
            return
            
        coursename = self.course_name_edit.text().strip()
        
        if not coursename:
            QMessageBox.warning(self, '警告', '请输入课程名称！')
            return
        
        # 检查课程名称是否已存在（排除自己）
        self.cursor.execute("SELECT COUNT(*) FROM course WHERE coursename = ? AND id != ?", (coursename, self.selected_id))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '课程名称已存在！')
            return
        
        # 更新数据
        self.cursor.execute("""
            UPDATE course 
            SET coursename = ?
            WHERE id = ?
        """, (coursename, self.selected_id))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_course_form()
        self.selected_id = None
        self.update_course_button.setEnabled(False)
        self.delete_course_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_course(self):
        """删除课程"""
        if not self.selected_id:
            return
            
        self.delete_course_row(self.selected_id)

    def clear_course_form(self):
        """清空课程表单"""
        self.course_name_edit.clear()

    def query_course(self):
        """查询课程"""
        keyword = self.course_query_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, '警告', '请输入查询关键字！')
            return
            
        # 构建查询SQL
        query_sql = """
            SELECT id, coursename
            FROM course
            WHERE coursename LIKE ?
            ORDER BY id
        """
        
        # 参数
        params = (f"%{keyword}%",)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    # 教师管理相关方法
    def edit_teacher_row(self, record_id):
        """编辑教师行"""
        self.selected_id = record_id
        # 获取该行数据
        self.cursor.execute("SELECT name, sex, age FROM teacher WHERE id = ?", (record_id,))
        data = self.cursor.fetchone()
        if data:
            # 填充表单
            self.teacher_name_edit.setText(data[0])
            self.teacher_sex_edit.setText(data[1])
            self.teacher_age_edit.setText(data[2])

    def delete_teacher_row(self, record_id):
        """删除教师行"""
        # 检查是否被排课表引用
        self.cursor.execute("SELECT COUNT(*) FROM schedule WHERE teacher_id = ?", (record_id,))
        reference_count = self.cursor.fetchone()[0]
        
        if reference_count > 0:
            QMessageBox.warning(self, '警告', '该数据已被引用，先去排课表中删除相关记录！')
            return
        
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM teacher WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            self.load_combobox_data()  # 重新加载下拉框数据
            QMessageBox.information(self, '提示', '删除成功！')

    def add_teacher(self):
        """添加教师"""
        name = self.teacher_name_edit.text().strip()
        sex = self.teacher_sex_edit.text().strip()
        age = self.teacher_age_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, '警告', '请输入教师姓名！')
            return
            
        if not sex:
            QMessageBox.warning(self, '警告', '请输入教师性别！')
            return
            
        if not age:
            QMessageBox.warning(self, '警告', '请输入教师年龄！')
            return
        
        # 检查教师姓名是否已存在
        self.cursor.execute("SELECT COUNT(*) FROM teacher WHERE name = ?", (name,))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '教师姓名已存在！')
            return
        
        # 插入数据
        self.cursor.execute("""
            INSERT INTO teacher (name, sex, age)
            VALUES (?, ?, ?)
        """, (name, sex, age))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_teacher_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_teacher(self):
        """更新教师"""
        if not self.selected_id:
            return
            
        name = self.teacher_name_edit.text().strip()
        sex = self.teacher_sex_edit.text().strip()
        age = self.teacher_age_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, '警告', '请输入教师姓名！')
            return
            
        if not sex:
            QMessageBox.warning(self, '警告', '请输入教师性别！')
            return
            
        if not age:
            QMessageBox.warning(self, '警告', '请输入教师年龄！')
            return
        
        # 检查教师姓名是否已存在（排除自己）
        self.cursor.execute("SELECT COUNT(*) FROM teacher WHERE name = ? AND id != ?", (name, self.selected_id))
        count = self.cursor.fetchone()[0]
        if count > 0:
            QMessageBox.warning(self, '警告', '教师姓名已存在！')
            return
        
        # 更新数据
        self.cursor.execute("""
            UPDATE teacher 
            SET name = ?, sex = ?, age = ?
            WHERE id = ?
        """, (name, sex, age, self.selected_id))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data()  # 重新加载下拉框数据
        self.clear_teacher_form()
        self.selected_id = None
        self.update_teacher_button.setEnabled(False)
        self.delete_teacher_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_teacher(self):
        """删除教师"""
        if not self.selected_id:
            return
            
        self.delete_teacher_row(self.selected_id)

    def clear_teacher_form(self):
        """清空教师表单"""
        self.teacher_name_edit.clear()
        self.teacher_sex_edit.clear()
        self.teacher_age_edit.clear()

    def query_teacher(self):
        """查询教师"""
        keyword = self.teacher_query_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, '警告', '请输入查询关键字！')
            return
            
        # 构建查询SQL
        query_sql = """
            SELECT id, name, sex, age
            FROM teacher
            WHERE name LIKE ?
            ORDER BY id
        """
        
        # 参数
        params = (f"%{keyword}%",)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    # 分页相关方法
    def first_page(self):
        """首页"""
        self.current_page = 1
        self.load_data()

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def last_page(self):
        """末页"""
        self.current_page = self.total_pages
        self.load_data()

    def closeEvent(self, event):
        """关闭事件"""
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SchedulingSystem()
    window.show()
    sys.exit(app.exec_())