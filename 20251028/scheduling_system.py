import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QTextEdit, QMessageBox, QHeaderView, QSpinBox, QInputDialog
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
        
        # 初始化UI
        self.init_ui()
        
        # 加载数据
        self.load_data()
        
        # 加载下拉框数据
        self.load_combobox_data()

    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建顶部操作面板
        top_panel = QHBoxLayout()
        
        # 班级选择
        top_panel.addWidget(QLabel("班级:"))
        self.class_combo = QComboBox()
        top_panel.addWidget(self.class_combo)
        
        # 教师选择
        top_panel.addWidget(QLabel("教师:"))
        self.teacher_combo = QComboBox()
        top_panel.addWidget(self.teacher_combo)
        
        # 课程选择
        top_panel.addWidget(QLabel("课程:"))
        self.course_combo = QComboBox()
        top_panel.addWidget(self.course_combo)
        
        # 星期选择
        top_panel.addWidget(QLabel("星期:"))
        self.week_spin = QSpinBox()
        self.week_spin.setMinimum(1)
        self.week_spin.setMaximum(7)
        top_panel.addWidget(self.week_spin)
        
        # 节次选择
        top_panel.addWidget(QLabel("节次:"))
        self.lesson_spin = QSpinBox()
        self.lesson_spin.setMinimum(1)
        self.lesson_spin.setMaximum(8)
        top_panel.addWidget(self.lesson_spin)
        
        # 备注
        top_panel.addWidget(QLabel("备注:"))
        self.remark_edit = QLineEdit()
        top_panel.addWidget(self.remark_edit)
        
        # 添加按钮
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_schedule)
        top_panel.addWidget(self.add_button)
        
        # 更新按钮
        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.update_schedule)
        self.update_button.setEnabled(False)
        top_panel.addWidget(self.update_button)
        
        # 删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_schedule)
        self.delete_button.setEnabled(False)
        top_panel.addWidget(self.delete_button)
        
        main_layout.addLayout(top_panel)
        
        # 创建查询面板
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
        
        # 按课程查询按钮
        self.query_by_course_button = QPushButton("按课程查询")
        self.query_by_course_button.clicked.connect(self.query_by_course)
        query_panel.addWidget(self.query_by_course_button)
        
        # 查询学生课表按钮
        self.query_student_schedule_button = QPushButton("查学生课表")
        self.query_student_schedule_button.clicked.connect(self.query_student_schedule)
        query_panel.addWidget(self.query_student_schedule_button)
        
        # 刷新下拉框按钮
        self.refresh_button = QPushButton("刷新下拉框")
        self.refresh_button.clicked.connect(self.refresh_comboboxes)
        query_panel.addWidget(self.refresh_button)
        
        # 显示所有按钮
        self.show_all_button = QPushButton("显示所有")
        self.show_all_button.clicked.connect(self.load_data)
        query_panel.addWidget(self.show_all_button)
        
        main_layout.addLayout(query_panel)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "班级", "教师", "课程", "星期", "节次", "备注", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
        main_layout.addWidget(self.table)
        
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
        
        main_layout.addLayout(bottom_panel)
        
        # 存储当前选中的行ID
        self.selected_schedule_id = None

    def load_combobox_data(self):
        """加载下拉框数据"""
        # 清空现有数据
        self.class_combo.clear()
        self.teacher_combo.clear()
        self.course_combo.clear()
        
        # 加载班级数据
        self.cursor.execute("SELECT id, classname FROM class")
        classes = self.cursor.fetchall()
        self.class_dict = {cls[1]: cls[0] for cls in classes}  # 名称到ID的映射
        self.class_combo.addItem("请选择")
        for cls in classes:
            self.class_combo.addItem(cls[1])
            
        # 加载教师数据
        self.cursor.execute("SELECT id, name FROM teacher")
        teachers = self.cursor.fetchall()
        self.teacher_dict = {teacher[1]: teacher[0] for teacher in teachers}  # 名称到ID的映射
        self.teacher_combo.addItem("请选择")
        for teacher in teachers:
            self.teacher_combo.addItem(teacher[1])
            
        # 加载课程数据
        self.cursor.execute("SELECT id, coursename FROM course")
        courses = self.cursor.fetchall()
        self.course_dict = {course[1]: course[0] for course in courses}  # 名称到ID的映射
        self.course_combo.addItem("请选择")
        for course in courses:
            self.course_combo.addItem(course[1])

    def load_data(self, query_sql=None, params=None):
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
            
            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, rid=row_data[0]: self.edit_row(rid))
            btn_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda checked, rid=row_data[0]: self.delete_row(rid))
            btn_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row_idx, 7, btn_widget)
        
        # 更新页码标签
        self.page_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页 (共 {total_records} 条记录)")

    def load_combobox_data_if_needed(self):
        """根据需要加载下拉框数据"""
        # 检查当前下拉框中是否缺少数据
        # 通过重新加载下拉框数据确保是最新的
        self.load_combobox_data()

    def on_table_selection_changed(self):
        """表格选择改变事件"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.selected_schedule_id = int(self.table.item(row, 0).text())
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.selected_schedule_id = None
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def edit_row(self, record_id):
        """编辑行"""
        self.selected_schedule_id = record_id
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

    def delete_row(self, record_id):
        """删除行"""
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM schedule WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()
            self.load_combobox_data_if_needed()  # 自动刷新下拉框
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
        self.load_combobox_data_if_needed()  # 自动刷新下拉框
        self.clear_form()
        QMessageBox.information(self, '提示', '添加成功！')

    def update_schedule(self):
        """更新排课"""
        if not self.selected_schedule_id:
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
        """, (class_id, weeks, lessons, self.selected_schedule_id))
        
        conflict_count = self.cursor.fetchone()[0]
        if conflict_count > 0:
            QMessageBox.warning(self, '警告', '该班级在该时间段已有排课，无法更新排课！')
            return
            
        # 更新数据
        self.cursor.execute("""
UPDATE schedule 
SET class_id = ?, teacher_id = ?, course_id = ?, weeks = ?, lessons = ?, remark = ?
WHERE id = ?
        """, (class_id, teacher_id, course_id, weeks, lessons, remark, self.selected_schedule_id))
        
        self.conn.commit()
        self.load_data()
        self.load_combobox_data_if_needed()  # 自动刷新下拉框
        self.clear_form()
        self.selected_schedule_id = None
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        QMessageBox.information(self, '提示', '更新成功！')

    def delete_schedule(self):
        """删除排课"""
        if not self.selected_schedule_id:
            return
            
        self.delete_row(self.selected_schedule_id)

    def clear_form(self):
        """清空表单"""
        self.class_combo.setCurrentIndex(0)
        self.teacher_combo.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.week_spin.setValue(1)
        self.lesson_spin.setValue(1)
        self.remark_edit.clear()

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

    def query_by_course(self):
        """根据课程查询"""
        course_name = self.course_combo.currentText()
        if course_name == "请选择" or not course_name:
            QMessageBox.warning(self, '警告', '请选择课程！')
            return
            
        course_id = self.course_dict[course_name]
        
        # 构建查询SQL，按课程查询并按星期和节次排序
        query_sql = """
SELECT s.id, c.classname, t.name, co.coursename, s.weeks, s.lessons, s.remark
FROM schedule s
JOIN class c ON s.class_id = c.id
JOIN teacher t ON s.teacher_id = t.id
JOIN course co ON s.course_id = co.id
WHERE s.course_id = ?
ORDER BY s.weeks ASC, s.lessons ASC
        """
        
        # 参数
        params = (course_id,)
        
        # 重置页码并加载数据
        self.current_page = 1
        self.load_data(query_sql, params)

    def query_student_schedule(self):
        """查询学生课表"""
        # 弹出输入框让用户输入学生姓名
        student_name, ok = QInputDialog.getText(self, '查询学生课表', '请输入学生姓名:')
        if not ok or not student_name.strip():
            return
            
        student_name = student_name.strip()
        
        # 首先查询学生所在的班级ID
        self.cursor.execute("SELECT class_id FROM student WHERE name = ?", (student_name,))
        class_result = self.cursor.fetchone()
        
        if not class_result:
            QMessageBox.information(self, '提示', f'未找到学生"{student_name}"')
            return
            
        class_id = class_result[0]
        
        # 构建查询SQL，查询该学生所在班级的课程安排
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
        
        # 检查是否有结果
        if self.table.rowCount() == 0:
            QMessageBox.information(self, '提示', f'未找到学生"{student_name}"的课表信息')
    
    def refresh_comboboxes(self):
        """手动刷新下拉框的槽函数"""
        self.load_combobox_data()
        QMessageBox.information(self, '提示', '下拉框刷新成功！')


    def closeEvent(self, event):
        """关闭事件"""
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SchedulingSystem()
    window.show()
    sys.exit(app.exec_())