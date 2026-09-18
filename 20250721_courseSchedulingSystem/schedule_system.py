import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLineEdit, QLabel, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class DatabaseManager:
    """数据库管理类"""
    def __init__(self):
        self.db_name = './db/database.db'
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 创建班级表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT,
                major TEXT
            )
        ''')
        
        # 创建课程表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                credit INTEGER,
                hours INTEGER
            )
        ''')
        
        # 创建学生表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT,
                class_id INTEGER,
                FOREIGN KEY (class_id) REFERENCES class (id)
            )
        ''')
        
        # 创建教师表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                department TEXT
            )
        ''')
        
        # 创建教师学生课程关系表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_student_course (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                student_id INTEGER,
                course_id INTEGER,
                week_day TEXT,
                lesson_number TEXT,
                FOREIGN KEY (teacher_id) REFERENCES teacher (id),
                FOREIGN KEY (student_id) REFERENCES student (id),
                FOREIGN KEY (course_id) REFERENCES course (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_name)


class BaseDialog(QDialog):
    """基础对话框类"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)


class ClassDialog(BaseDialog):
    """班级管理对话框"""
    def __init__(self, class_data=None, parent=None):
        super().__init__(parent)
        self.class_data = class_data
        self.setWindowTitle("班级信息" if not class_data else "编辑班级")
        self.init_ui()
        if class_data:
            self.fill_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.grade_edit = QLineEdit()
        self.major_edit = QLineEdit()
        
        layout.addRow("班级名称:", self.name_edit)
        layout.addRow("年级:", self.grade_edit)
        layout.addRow("专业:", self.major_edit)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def fill_data(self):
        self.name_edit.setText(self.class_data[1])
        self.grade_edit.setText(self.class_data[2])
        self.major_edit.setText(self.class_data[3])
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'grade': self.grade_edit.text().strip(),
            'major': self.major_edit.text().strip()
        }


class CourseDialog(BaseDialog):
    """课程管理对话框"""
    def __init__(self, course_data=None, parent=None):
        super().__init__(parent)
        self.course_data = course_data
        self.setWindowTitle("课程信息" if not course_data else "编辑课程")
        self.init_ui()
        if course_data:
            self.fill_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.credit_edit = QLineEdit()
        self.hours_edit = QLineEdit()
        
        layout.addRow("课程名称:", self.name_edit)
        layout.addRow("学分:", self.credit_edit)
        layout.addRow("学时:", self.hours_edit)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def fill_data(self):
        self.name_edit.setText(self.course_data[1])
        self.credit_edit.setText(str(self.course_data[2]))
        self.hours_edit.setText(str(self.course_data[3]))
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'credit': self.credit_edit.text().strip(),
            'hours': self.hours_edit.text().strip()
        }


class StudentDialog(BaseDialog):
    """学生管理对话框"""
    def __init__(self, student_data=None, classes=None, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.classes = classes or []
        self.setWindowTitle("学生信息" if not student_data else "编辑学生")
        self.init_ui()
        if student_data:
            self.fill_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.class_combo = QComboBox()
        for class_item in self.classes:
            self.class_combo.addItem(class_item[1], class_item[0])
        
        layout.addRow("学生姓名:", self.name_edit)
        layout.addRow("性别:", self.gender_combo)
        layout.addRow("班级:", self.class_combo)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def fill_data(self):
        self.name_edit.setText(self.student_data[1])
        self.gender_combo.setCurrentText(self.student_data[2])
        class_id = self.student_data[3]
        for i in range(self.class_combo.count()):
            if self.class_combo.itemData(i) == class_id:
                self.class_combo.setCurrentIndex(i)
                break
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'gender': self.gender_combo.currentText(),
            'class_id': self.class_combo.currentData()
        }


class TeacherDialog(BaseDialog):
    """教师管理对话框"""
    def __init__(self, teacher_data=None, parent=None):
        super().__init__(parent)
        self.teacher_data = teacher_data
        self.setWindowTitle("教师信息" if not teacher_data else "编辑教师")
        self.init_ui()
        if teacher_data:
            self.fill_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.title_edit = QLineEdit()
        self.department_edit = QLineEdit()
        
        layout.addRow("教师姓名:", self.name_edit)
        layout.addRow("职称:", self.title_edit)
        layout.addRow("院系:", self.department_edit)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def fill_data(self):
        self.name_edit.setText(self.teacher_data[1])
        self.title_edit.setText(self.teacher_data[2])
        self.department_edit.setText(self.teacher_data[3])
    
    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'title': self.title_edit.text().strip(),
            'department': self.department_edit.text().strip()
        }


class TSCDialog(BaseDialog):
    """教师学生课程管理对话框"""
    def __init__(self, tsc_data=None, teachers=None, students=None, courses=None, parent=None):
        super().__init__(parent)
        self.tsc_data = tsc_data
        self.teachers = teachers or []
        self.students = students or []
        self.courses = courses or []
        self.setWindowTitle("教学安排" if not tsc_data else "编辑教学安排")
        self.init_ui()
        if tsc_data:
            self.fill_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.teacher_combo = QComboBox()
        for teacher in self.teachers:
            self.teacher_combo.addItem(teacher[1], teacher[0])
        
        self.student_combo = QComboBox()
        for student in self.students:
            self.student_combo.addItem(student[1], student[0])
        
        self.course_combo = QComboBox()
        for course in self.courses:
            self.course_combo.addItem(course[1], course[0])
        
        self.week_day_combo = QComboBox()
        self.week_day_combo.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        
        self.lesson_edit = QLineEdit()
        
        layout.addRow("教师:", self.teacher_combo)
        layout.addRow("学生:", self.student_combo)
        layout.addRow("课程:", self.course_combo)
        layout.addRow("星期:", self.week_day_combo)
        layout.addRow("节次:", self.lesson_edit)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def fill_data(self):
        # 填充教师
        teacher_id = self.tsc_data[1]
        for i in range(self.teacher_combo.count()):
            if self.teacher_combo.itemData(i) == teacher_id:
                self.teacher_combo.setCurrentIndex(i)
                break
        
        # 填充学生
        student_id = self.tsc_data[2]
        for i in range(self.student_combo.count()):
            if self.student_combo.itemData(i) == student_id:
                self.student_combo.setCurrentIndex(i)
                break
        
        # 填充课程
        course_id = self.tsc_data[3]
        for i in range(self.course_combo.count()):
            if self.course_combo.itemData(i) == course_id:
                self.course_combo.setCurrentIndex(i)
                break
        
        # 填充星期
        self.week_day_combo.setCurrentText(self.tsc_data[4])
        self.lesson_edit.setText(self.tsc_data[5])
    
    def get_data(self):
        return {
            'teacher_id': self.teacher_combo.currentData(),
            'student_id': self.student_combo.currentData(),
            'course_id': self.course_combo.currentData(),
            'week_day': self.week_day_combo.currentText(),
            'lesson': self.lesson_edit.text().strip()
        }


class BaseManagementWidget(QWidget):
    """基础管理控件类"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_page = 1
        self.total_pages = 1
        self.page_size = 10
        self.total_records = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 搜索和操作区域
        top_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("请输入搜索关键字")
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.search)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh)
        
        top_layout.addWidget(QLabel("搜索:"))
        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(search_btn)
        top_layout.addWidget(refresh_btn)
        top_layout.addStretch()
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("新增")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.delete_btn.clicked.connect(self.delete_item)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 分页控制
        page_layout = QHBoxLayout()
        self.first_page_btn = QPushButton("首页")
        self.prev_page_btn = QPushButton("上一页")
        self.next_page_btn = QPushButton("下一页")
        self.last_page_btn = QPushButton("末页")
        self.page_info_label = QLabel()
        
        self.first_page_btn.clicked.connect(self.first_page)
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.next_page_btn.clicked.connect(self.next_page)
        self.last_page_btn.clicked.connect(self.last_page)
        
        page_layout.addWidget(self.first_page_btn)
        page_layout.addWidget(self.prev_page_btn)
        page_layout.addWidget(self.next_page_btn)
        page_layout.addWidget(self.last_page_btn)
        page_layout.addWidget(self.page_info_label)
        page_layout.addStretch()
        
        layout.addLayout(top_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        layout.addLayout(page_layout)
        self.setLayout(layout)
    
    def refresh(self):
        self.search()
    
    def first_page(self):
        self.current_page = 1
        self.refresh()
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh()
    
    def last_page(self):
        self.current_page = self.total_pages
        self.refresh()
    
    def update_page_info(self):
        self.page_info_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页，共 {self.total_records} 条记录")


class ClassManagementWidget(BaseManagementWidget):
    """班级管理控件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setup_table()
        self.refresh()
    
    def setup_table(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "班级名称", "年级", "专业"])
    
    def search(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        keyword = self.search_edit.text().strip()
        if keyword:
            sql = "SELECT COUNT(*) FROM class WHERE name LIKE ? OR grade LIKE ? OR major LIKE ?"
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        else:
            sql = "SELECT COUNT(*) FROM class"
            cursor.execute(sql)
        
        self.total_records = cursor.fetchone()[0]
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        
        offset = (self.current_page - 1) * self.page_size
        if keyword:
            sql = """
                SELECT * FROM class 
                WHERE name LIKE ? OR grade LIKE ? OR major LIKE ? 
                ORDER BY id 
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", self.page_size, offset))
        else:
            sql = "SELECT * FROM class ORDER BY id LIMIT ? OFFSET ?"
            cursor.execute(sql, (self.page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row_idx, col_idx, item)
        
        self.update_page_info()
    
    def add_item(self):
        dialog = ClassDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "班级名称不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO class (name, grade, major) VALUES (?, ?, ?)"
                cursor.execute(sql, (data['name'], data['grade'], data['major']))
                conn.commit()
                QMessageBox.information(self, "成功", "添加班级成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加班级失败：{str(e)}")
            finally:
                conn.close()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        class_id = int(self.table.item(selected_row, 0).text())
        class_data = []
        for col in range(self.table.columnCount()):
            class_data.append(self.table.item(selected_row, col).text())
        
        dialog = ClassDialog(class_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "班级名称不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "UPDATE class SET name=?, grade=?, major=? WHERE id=?"
                cursor.execute(sql, (data['name'], data['grade'], data['major'], class_id))
                conn.commit()
                QMessageBox.information(self, "成功", "修改班级信息成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改班级信息失败：{str(e)}")
            finally:
                conn.close()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        class_id = int(self.table.item(selected_row, 0).text())
        class_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "确认", f"确定要删除班级 [{class_name}] 吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                # 检查是否有学生属于这个班级
                cursor.execute("SELECT COUNT(*) FROM student WHERE class_id=?", (class_id,))
                student_count = cursor.fetchone()[0]
                if student_count > 0:
                    QMessageBox.warning(self, "警告", f"该班级下还有 {student_count} 名学生，不能删除！")
                    return
                
                sql = "DELETE FROM class WHERE id=?"
                cursor.execute(sql, (class_id,))
                conn.commit()
                QMessageBox.information(self, "成功", "删除班级成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除班级失败：{str(e)}")
            finally:
                conn.close()


class CourseManagementWidget(BaseManagementWidget):
    """课程管理控件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setup_table()
        self.refresh()
    
    def setup_table(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "课程名称", "学分", "学时"])
    
    def search(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        keyword = self.search_edit.text().strip()
        if keyword:
            sql = "SELECT COUNT(*) FROM course WHERE name LIKE ?"
            cursor.execute(sql, (f"%{keyword}%",))
        else:
            sql = "SELECT COUNT(*) FROM course"
            cursor.execute(sql)
        
        self.total_records = cursor.fetchone()[0]
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        
        offset = (self.current_page - 1) * self.page_size
        if keyword:
            sql = """
                SELECT * FROM course 
                WHERE name LIKE ? 
                ORDER BY id 
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (f"%{keyword}%", self.page_size, offset))
        else:
            sql = "SELECT * FROM course ORDER BY id LIMIT ? OFFSET ?"
            cursor.execute(sql, (self.page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row_idx, col_idx, item)
        
        self.update_page_info()
    
    def add_item(self):
        dialog = CourseDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "课程名称不能为空！")
                return
            
            # 验证学分和学时是否为数字
            try:
                credit = int(data['credit']) if data['credit'] else 0
                hours = int(data['hours']) if data['hours'] else 0
            except ValueError:
                QMessageBox.warning(self, "输入错误", "学分和学时必须为数字！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO course (name, credit, hours) VALUES (?, ?, ?)"
                cursor.execute(sql, (data['name'], credit, hours))
                conn.commit()
                QMessageBox.information(self, "成功", "添加课程成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加课程失败：{str(e)}")
            finally:
                conn.close()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        course_id = int(self.table.item(selected_row, 0).text())
        course_data = []
        for col in range(self.table.columnCount()):
            course_data.append(self.table.item(selected_row, col).text())
        
        dialog = CourseDialog(course_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "课程名称不能为空！")
                return
            
            # 验证学分和学时是否为数字
            try:
                credit = int(data['credit']) if data['credit'] else 0
                hours = int(data['hours']) if data['hours'] else 0
            except ValueError:
                QMessageBox.warning(self, "输入错误", "学分和学时必须为数字！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "UPDATE course SET name=?, credit=?, hours=? WHERE id=?"
                cursor.execute(sql, (data['name'], credit, hours, course_id))
                conn.commit()
                QMessageBox.information(self, "成功", "修改课程信息成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改课程信息失败：{str(e)}")
            finally:
                conn.close()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        course_id = int(self.table.item(selected_row, 0).text())
        course_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "确认", f"确定要删除课程 [{course_name}] 吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                # 检查是否有安排使用这门课程
                cursor.execute("SELECT COUNT(*) FROM teacher_student_course WHERE course_id=?", (course_id,))
                tsc_count = cursor.fetchone()[0]
                if tsc_count > 0:
                    QMessageBox.warning(self, "警告", f"该课程已被 {tsc_count} 个教学安排使用，不能删除！")
                    return
                
                sql = "DELETE FROM course WHERE id=?"
                cursor.execute(sql, (course_id,))
                conn.commit()
                QMessageBox.information(self, "成功", "删除课程成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除课程失败：{str(e)}")
            finally:
                conn.close()


class StudentManagementWidget(BaseManagementWidget):
    """学生管理控件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setup_table()
        self.refresh()
    
    def setup_table(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "学生姓名", "性别", "班级ID", "班级名称"])
    
    def search(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        keyword = self.search_edit.text().strip()
        if keyword:
            sql = """
                SELECT COUNT(*) FROM student s 
                LEFT JOIN class c ON s.class_id = c.id 
                WHERE s.name LIKE ? OR c.name LIKE ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
        else:
            sql = "SELECT COUNT(*) FROM student"
            cursor.execute(sql)
        
        self.total_records = cursor.fetchone()[0]
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        
        offset = (self.current_page - 1) * self.page_size
        if keyword:
            sql = """
                SELECT s.id, s.name, s.gender, s.class_id, c.name 
                FROM student s 
                LEFT JOIN class c ON s.class_id = c.id 
                WHERE s.name LIKE ? OR c.name LIKE ? 
                ORDER BY s.id 
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", self.page_size, offset))
        else:
            sql = """
                SELECT s.id, s.name, s.gender, s.class_id, c.name 
                FROM student s 
                LEFT JOIN class c ON s.class_id = c.id 
                ORDER BY s.id 
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (self.page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                self.table.setItem(row_idx, col_idx, item)
        
        self.update_page_info()
    
    def add_item(self):
        # 获取所有班级信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM class")
        classes = cursor.fetchall()
        conn.close()
        
        if not classes:
            QMessageBox.warning(self, "警告", "请先添加班级信息！")
            return
        
        dialog = StudentDialog(classes=classes)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "学生姓名不能为空！")
                return
            
            if not data['class_id']:
                QMessageBox.warning(self, "输入错误", "请选择班级！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO student (name, gender, class_id) VALUES (?, ?, ?)"
                cursor.execute(sql, (data['name'], data['gender'], data['class_id']))
                conn.commit()
                QMessageBox.information(self, "成功", "添加学生成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加学生失败：{str(e)}")
            finally:
                conn.close()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        student_id = int(self.table.item(selected_row, 0).text())
        student_data = []
        for col in range(self.table.columnCount()):
            student_data.append(self.table.item(selected_row, col).text())
        
        # 获取所有班级信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM class")
        classes = cursor.fetchall()
        conn.close()
        
        if not classes:
            QMessageBox.warning(self, "警告", "没有任何班级信息！")
            return
        
        dialog = StudentDialog(student_data, classes)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "学生姓名不能为空！")
                return
            
            if not data['class_id']:
                QMessageBox.warning(self, "输入错误", "请选择班级！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "UPDATE student SET name=?, gender=?, class_id=? WHERE id=?"
                cursor.execute(sql, (data['name'], data['gender'], data['class_id'], student_id))
                conn.commit()
                QMessageBox.information(self, "成功", "修改学生信息成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改学生信息失败：{str(e)}")
            finally:
                conn.close()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        student_id = int(self.table.item(selected_row, 0).text())
        student_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "确认", f"确定要删除学生 [{student_name}] 吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "DELETE FROM student WHERE id=?"
                cursor.execute(sql, (student_id,))
                conn.commit()
                QMessageBox.information(self, "成功", "删除学生成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除学生失败：{str(e)}")
            finally:
                conn.close()


class TeacherManagementWidget(BaseManagementWidget):
    """教师管理控件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setup_table()
        self.refresh()
    
    def setup_table(self):
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "教师姓名", "职称", "院系"])
    
    def search(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        keyword = self.search_edit.text().strip()
        if keyword:
            sql = "SELECT COUNT(*) FROM teacher WHERE name LIKE ? OR title LIKE ? OR department LIKE ?"
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        else:
            sql = "SELECT COUNT(*) FROM teacher"
            cursor.execute(sql)
        
        self.total_records = cursor.fetchone()[0]
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        
        offset = (self.current_page - 1) * self.page_size
        if keyword:
            sql = """
                SELECT * FROM teacher 
                WHERE name LIKE ? OR title LIKE ? OR department LIKE ? 
                ORDER BY id 
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", self.page_size, offset))
        else:
            sql = "SELECT * FROM teacher ORDER BY id LIMIT ? OFFSET ?"
            cursor.execute(sql, (self.page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.table.setItem(row_idx, col_idx, item)
        
        self.update_page_info()
    
    def add_item(self):
        dialog = TeacherDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "教师姓名不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO teacher (name, title, department) VALUES (?, ?, ?)"
                cursor.execute(sql, (data['name'], data['title'], data['department']))
                conn.commit()
                QMessageBox.information(self, "成功", "添加教师成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加教师失败：{str(e)}")
            finally:
                conn.close()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        teacher_id = int(self.table.item(selected_row, 0).text())
        teacher_data = []
        for col in range(self.table.columnCount()):
            teacher_data.append(self.table.item(selected_row, col).text())
        
        dialog = TeacherDialog(teacher_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "输入错误", "教师姓名不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "UPDATE teacher SET name=?, title=?, department=? WHERE id=?"
                cursor.execute(sql, (data['name'], data['title'], data['department'], teacher_id))
                conn.commit()
                QMessageBox.information(self, "成功", "修改教师信息成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改教师信息失败：{str(e)}")
            finally:
                conn.close()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        teacher_id = int(self.table.item(selected_row, 0).text())
        teacher_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "确认", f"确定要删除教师 [{teacher_name}] 吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                # 检查是否有教学安排使用这位教师
                cursor.execute("SELECT COUNT(*) FROM teacher_student_course WHERE teacher_id=?", (teacher_id,))
                tsc_count = cursor.fetchone()[0]
                if tsc_count > 0:
                    QMessageBox.warning(self, "警告", f"该教师有 {tsc_count} 个教学安排，不能删除！")
                    return
                
                sql = "DELETE FROM teacher WHERE id=?"
                cursor.execute(sql, (teacher_id,))
                conn.commit()
                QMessageBox.information(self, "成功", "删除教师成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除教师失败：{str(e)}")
            finally:
                conn.close()


class TSCManagementWidget(BaseManagementWidget):
    """教师学生课程管理控件"""
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        self.setup_table()
        self.refresh()
    
    def setup_table(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "教师", "学生", "课程", "星期", "节次", "教师ID"])
        self.table.setColumnHidden(6, True)  # 隐藏教师ID列
    
    def search(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        keyword = self.search_edit.text().strip()
        if keyword:
            sql = """
                SELECT COUNT(*) FROM teacher_student_course tsc
                JOIN teacher t ON tsc.teacher_id = t.id
                JOIN student s ON tsc.student_id = s.id
                JOIN course c ON tsc.course_id = c.id
                WHERE t.name LIKE ? OR s.name LIKE ? OR c.name LIKE ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        else:
            sql = """
                SELECT COUNT(*) FROM teacher_student_course tsc
                JOIN teacher t ON tsc.teacher_id = t.id
                JOIN student s ON tsc.student_id = s.id
                JOIN course c ON tsc.course_id = c.id
            """
            cursor.execute(sql)
        
        self.total_records = cursor.fetchone()[0]
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
        
        offset = (self.current_page - 1) * self.page_size
        if keyword:
            sql = """
                SELECT tsc.id, t.name, s.name, c.name, tsc.week_day, tsc.lesson_number, tsc.teacher_id
                FROM teacher_student_course tsc
                JOIN teacher t ON tsc.teacher_id = t.id
                JOIN student s ON tsc.student_id = s.id
                JOIN course c ON tsc.course_id = c.id
                WHERE t.name LIKE ? OR s.name LIKE ? OR c.name LIKE ?
                ORDER BY tsc.id
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", self.page_size, offset))
        else:
            sql = """
                SELECT tsc.id, t.name, s.name, c.name, tsc.week_day, tsc.lesson_number, tsc.teacher_id
                FROM teacher_student_course tsc
                JOIN teacher t ON tsc.teacher_id = t.id
                JOIN student s ON tsc.student_id = s.id
                JOIN course c ON tsc.course_id = c.id
                ORDER BY tsc.id
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, (self.page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                self.table.setItem(row_idx, col_idx, item)
        
        self.update_page_info()
    
    def add_item(self):
        # 获取教师、学生、课程信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher")
        teachers = cursor.fetchall()
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        cursor.execute("SELECT * FROM course")
        courses = cursor.fetchall()
        conn.close()
        
        if not teachers:
            QMessageBox.warning(self, "警告", "请先添加教师信息！")
            return
        
        if not students:
            QMessageBox.warning(self, "警告", "请先添加学生信息！")
            return
        
        if not courses:
            QMessageBox.warning(self, "警告", "请先添加课程信息！")
            return
        
        dialog = TSCDialog(teachers=teachers, students=students, courses=courses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['lesson']:
                QMessageBox.warning(self, "输入错误", "节次不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = """
                    INSERT INTO teacher_student_course 
                    (teacher_id, student_id, course_id, week_day, lesson_number) 
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    data['teacher_id'], 
                    data['student_id'], 
                    data['course_id'], 
                    data['week_day'], 
                    data['lesson']
                ))
                conn.commit()
                QMessageBox.information(self, "成功", "添加教学安排成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加教学安排失败：{str(e)}")
            finally:
                conn.close()
    
    def edit_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        tsc_id = int(self.table.item(selected_row, 0).text())
        tsc_data = []
        for col in range(self.table.columnCount()):
            tsc_data.append(self.table.item(selected_row, col).text())
        
        # 获取教师、学生、课程信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher")
        teachers = cursor.fetchall()
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        cursor.execute("SELECT * FROM course")
        courses = cursor.fetchall()
        conn.close()
        
        dialog = TSCDialog(tsc_data, teachers=teachers, students=students, courses=courses)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['lesson']:
                QMessageBox.warning(self, "输入错误", "节次不能为空！")
                return
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = """
                    UPDATE teacher_student_course 
                    SET teacher_id=?, student_id=?, course_id=?, week_day=?, lesson_number=? 
                    WHERE id=?
                """
                cursor.execute(sql, (
                    data['teacher_id'], 
                    data['student_id'], 
                    data['course_id'], 
                    data['week_day'], 
                    data['lesson'],
                    tsc_id
                ))
                conn.commit()
                QMessageBox.information(self, "成功", "修改教学安排成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"修改教学安排失败：{str(e)}")
            finally:
                conn.close()
    
    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        tsc_id = int(self.table.item(selected_row, 0).text())
        teacher_name = self.table.item(selected_row, 1).text()
        student_name = self.table.item(selected_row, 2).text()
        course_name = self.table.item(selected_row, 3).text()
        
        reply = QMessageBox.question(
            self, 
            "确认", 
            f"确定要删除教学安排 [{teacher_name}-{student_name}-{course_name}] 吗？", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            try:
                sql = "DELETE FROM teacher_student_course WHERE id=?"
                cursor.execute(sql, (tsc_id,))
                conn.commit()
                QMessageBox.information(self, "成功", "删除教学安排成功！")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除教学安排失败：{str(e)}")
            finally:
                conn.close()


class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("排课管理系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # 添加各个管理页面
        self.class_widget = ClassManagementWidget(self.db_manager)
        self.course_widget = CourseManagementWidget(self.db_manager)
        self.student_widget = StudentManagementWidget(self.db_manager)
        self.teacher_widget = TeacherManagementWidget(self.db_manager)
        self.tsc_widget = TSCManagementWidget(self.db_manager)
        
        self.tab_widget.addTab(self.class_widget, "班级管理")
        self.tab_widget.addTab(self.course_widget, "课程管理")
        self.tab_widget.addTab(self.student_widget, "学生管理")
        self.tab_widget.addTab(self.teacher_widget, "教师管理")
        self.tab_widget.addTab(self.tsc_widget, "教学安排管理")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()