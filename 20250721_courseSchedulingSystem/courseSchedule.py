import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QComboBox, QFileDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


# ========== 1. 数据库连接配置 ==========
import pymysql

def create_connection():
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="school1",
            port=3306,
            charset='utf8mb4'
        )
        print("数据库连接成功")
        return db
    except pymysql.MySQLError as e:
        print("数据库连接失败:", str(e))
        return None


# ========== 2. 主窗口类 ==========
class StudentDialog(QDialog):
    def __init__(self, parent=None, name="", gender="", phone="", class_id=""):
        super().__init__(parent)
        self.setWindowTitle("学生信息")
        self.name = name
        self.gender = gender
        self.phone = phone
        self.class_id = class_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 学生姓名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("学生姓名:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.name)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # 性别
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("性别:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.gender_combo.setCurrentText(self.gender)
        gender_layout.addWidget(self.gender_combo)
        layout.addLayout(gender_layout)

        # 手机号
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("手机号:"))
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.phone)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # 所属班级
        class_id_layout = QHBoxLayout()
        class_id_layout.addWidget(QLabel("所属班级ID:"))
        self.class_id_input = QLineEdit()
        self.class_id_input.setText(self.class_id)
        class_id_layout.addWidget(self.class_id_input)
        layout.addLayout(class_id_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


# ========== 2. 主窗口类 ==========
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("教师工作量查询系统")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 第一行搜索区域
        search_layout1 = QHBoxLayout()
        self.teacher_id_input = QLineEdit()
        self.teacher_id_input.setPlaceholderText("请输入教师ID")
        search_btn = QPushButton("查询")
        search_btn.clicked.connect(self.search_teacher_workload)
        export_btn = QPushButton("导出为Excel")
        export_btn.clicked.connect(self.export_to_excel)
        search_layout1.addWidget(QLabel("教师ID:"))
        search_layout1.addWidget(self.teacher_id_input)
        search_layout1.addWidget(search_btn)
        search_layout1.addWidget(export_btn)

        # 新增姓名搜索区域
        self.teacher_name_input = QLineEdit()
        self.teacher_name_input.setPlaceholderText("请输入教师姓名")
        name_search_btn = QPushButton("姓名查询")
        name_search_btn.clicked.connect(self.search_teacher_by_name)
        search_layout1.addWidget(QLabel("教师姓名:"))
        search_layout1.addWidget(self.teacher_name_input)
        search_layout1.addWidget(name_search_btn)

        # 第二行搜索区域
        search_layout2 = QHBoxLayout()

        # 新增课程表查询区域
        self.teacher_schedule_input = QLineEdit()
        self.teacher_schedule_input.setPlaceholderText("请输入教师姓名")
        schedule_search_btn = QPushButton("课程表查询")
        schedule_search_btn.clicked.connect(self.search_teacher_schedule)
        search_layout2.addWidget(QLabel("课程表查询:"))
        search_layout2.addWidget(self.teacher_schedule_input)
        search_layout2.addWidget(schedule_search_btn)

        # 新增学生课程表查询区域
        self.student_schedule_input = QLineEdit()
        self.student_schedule_input.setPlaceholderText("请输入学生姓名")
        student_schedule_btn = QPushButton("学生课程表查询")
        student_schedule_btn.clicked.connect(self.search_student_schedule)
        search_layout2.addWidget(QLabel("学生课程表查询:"))
        search_layout2.addWidget(self.student_schedule_input)
        search_layout2.addWidget(student_schedule_btn)

        # 第三行学生管理按钮区域
        student_management_layout = QHBoxLayout()
        add_btn = QPushButton("新增")
        add_btn.clicked.connect(self.add_student)
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_student)
        edit_btn = QPushButton("修改")
        edit_btn.clicked.connect(self.edit_student)
        student_search_btn = QPushButton("学生查询")
        student_search_btn.clicked.connect(self.search_student)
        student_management_layout.addWidget(add_btn)
        student_management_layout.addWidget(delete_btn)
        student_management_layout.addWidget(edit_btn)
        student_management_layout.addWidget(student_search_btn)
        student_management_layout.addStretch()

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels([
            "studentID", "学生名", "教师名", "班级名",
            "课程名", "星期", "节次", "备注"
        ])

        # 添加到主布局
        main_layout.addLayout(search_layout1)
        main_layout.addLayout(search_layout2)
        main_layout.addLayout(student_management_layout)
        main_layout.addWidget(self.result_table)
        self.setLayout(main_layout)

    def search_teacher_workload(self):
        teacher_id = self.teacher_id_input.text().strip()
        if not teacher_id.isdigit():
            QMessageBox.warning(self, "输入错误", "教师ID必须为数字！")
            return

        db = create_connection()
        if not db:
            QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
            return

        try:
            with db.cursor() as cursor:
                sql = """
                    SELECT t.id, t.name, COUNT(*) AS total_lessons
                    FROM teacher_student_course ct
                    JOIN teacher t ON ct.teacher_id = t.id
                    WHERE ct.teacher_id = %s
                    GROUP BY t.id, t.name
                """
                cursor.execute(sql, (teacher_id,))
                results = cursor.fetchall()

                self.result_table.setRowCount(0)
                for row_data in results:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    self.result_table.setItem(row, 0, QTableWidgetItem(str(row_data[0])))
                    self.result_table.setItem(row, 1, QTableWidgetItem(row_data[1]))
                    self.result_table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))

        except Exception as e:
            QMessageBox.critical(self, "查询失败", f"数据库错误: {str(e)}")
        finally:
            db.close()

    def search_teacher_by_name(self):
        teacher_name = self.teacher_name_input.text().strip()
        if not teacher_name:
            QMessageBox.warning(self, "输入错误", "请输入教师姓名！")
            return

        db = create_connection()
        if not db:
            QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
            return

        try:
            with db.cursor() as cursor:
                sql = """
                    SELECT t.id, t.name, COUNT(*) AS total_lessons
                    FROM teacher_student_course ct
                    JOIN teacher t ON ct.teacher_id = t.id
                    WHERE t.name LIKE %s
                    GROUP BY t.id, t.name
                """
                cursor.execute(sql, (f"%{teacher_name}%"))
                results = cursor.fetchall()

                self.result_table.setRowCount(0)
                for row_data in results:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    self.result_table.setItem(row, 0, QTableWidgetItem(str(row_data[0])))
                    self.result_table.setItem(row, 1, QTableWidgetItem(row_data[1]))
                    self.result_table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))

        except Exception as e:
            QMessageBox.critical(self, "查询失败", f"数据库错误: {str(e)}")
            print(f"详细错误信息: {str(e)}")  # 添加详细错误日志
        finally:
            db.close()

    def search_teacher_schedule(self):
        teacher_name = self.teacher_schedule_input.text().strip()
        if not teacher_name:
            QMessageBox.warning(self, "输入错误", "请输入教师姓名！")
            return

        db = create_connection()
        if not db:
            QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
            return

        try:
            with db.cursor() as cursor:
                sql = """
                    SELECT DISTINCT
                        c.course_name AS 课程名称,
                        tsc.week_day AS 星期,
                        tsc.lesson_number AS 节次,
                        tsc.remark AS 备注
                    FROM
                        teacher_student_course tsc
                    JOIN
                        teacher t ON tsc.teacher_id = t.id
                    JOIN
                        course c ON tsc.course_id = c.id
                    WHERE
                        t.name = %s
                    ORDER BY
                        tsc.week_day, tsc.lesson_number
                """
                cursor.execute(sql, (teacher_name,))
                results = cursor.fetchall()

                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(4)
                self.result_table.setHorizontalHeaderLabels(["课程名称", "星期", "节次", "备注"])

                for row_data in results:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    for col, data in enumerate(row_data):
                        self.result_table.setItem(row, col, QTableWidgetItem(str(data)))

        except Exception as e:
            QMessageBox.critical(self, "查询失败", f"数据库错误: {str(e)}")
            print(f"详细错误信息: {str(e)}")
        finally:
            db.close()

    def search_student_schedule(self):
        student_name = self.student_schedule_input.text().strip()
        if not student_name:
            QMessageBox.warning(self, "输入错误", "请输入学生姓名！")
            return

        db = create_connection()
        if not db:
            QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
            return

        try:
            with db.cursor() as cursor:
                sql = """
                    SELECT
                        s.id AS studentID,
                        s.name AS 学生名,
                        t.name AS 教师名,
                        c.class_name AS 班级名,
                        co.course_name AS 课程名,
                        tsc.week_day AS 星期,
                        tsc.lesson_number AS 节次,
                        tsc.remark AS 备注
                    FROM
                        teacher_student_course tsc
                    JOIN
                        student s ON tsc.student_id = s.id
                    JOIN
                        teacher t ON tsc.teacher_id = t.id
                    JOIN
                        class c ON s.class_id = c.id
                    JOIN
                        course co ON tsc.course_id = co.id
                    WHERE
                        s.name = %s
                    ORDER BY
                        tsc.week_day, tsc.lesson_number
                """
                cursor.execute(sql, (student_name,))
                results = cursor.fetchall()

                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(8)
                self.result_table.setHorizontalHeaderLabels([
                    "studentID", "学生名", "教师名", "班级名",
                    "课程名", "星期", "节次", "备注"
                ])

                for row_data in results:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    for col, data in enumerate(row_data):
                        self.result_table.setItem(row, col, QTableWidgetItem(str(data)))

        except Exception as e:
            QMessageBox.critical(self, "查询失败", f"数据库错误: {str(e)}")
            print(f"详细错误信息: {str(e)}")
        finally:
            db.close()

    def search_student(self):
        db = create_connection()
        if not db:
            QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
            return

        try:
            with db.cursor() as cursor:
                sql = "SELECT id, name, gender, phone, class_id FROM student"
                cursor.execute(sql)
                results = cursor.fetchall()

                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(5)
                self.result_table.setHorizontalHeaderLabels(["studentID", "学生名", "性别", "手机号", "班级ID"])

                for row_data in results:
                    row = self.result_table.rowCount()
                    self.result_table.insertRow(row)
                    for col, data in enumerate(row_data):
                        self.result_table.setItem(row, col, QTableWidgetItem(str(data)))

        except Exception as e:
            QMessageBox.critical(self, "查询失败", f"数据库错误: {str(e)}")
            print(f"详细错误信息: {str(e)}")
        finally:
            db.close()

    def add_student(self):
        dialog = StudentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            db = create_connection()
            if not db:
                QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
                return

            try:
                with db.cursor() as cursor:
                    sql = """
                        INSERT INTO student (name, gender, phone, class_id)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        dialog.name_input.text(),
                        dialog.gender_combo.currentText(),
                        dialog.phone_input.text(),
                        dialog.class_id_input.text()
                    ))
                    db.commit()
                    self.search_student()  # 刷新查询
            except Exception as e:
                QMessageBox.critical(self, "新增失败", f"数据库错误: {str(e)}")
            finally:
                db.close()

    def delete_student(self):
        selected_row = self.result_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "删除错误", "请先选中一行数据")
            return

        student_id = self.result_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "确认删除", "确定要删除选中的学生吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = create_connection()
            if not db:
                QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
                return

            try:
                with db.cursor() as cursor:
                    sql = "DELETE FROM student WHERE id = %s"
                    cursor.execute(sql, (student_id,))
                    db.commit()
                    self.result_table.removeRow(selected_row)
            except Exception as e:
                QMessageBox.critical(self, "删除失败", f"数据库错误: {str(e)}")
            finally:
                db.close()

    def edit_student(self):
        selected_row = self.result_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "编辑错误", "请先选中一行数据")
            return

        student_id = self.result_table.item(selected_row, 0).text()
        name = self.result_table.item(selected_row, 1).text()
        gender = self.result_table.item(selected_row, 2).text()
        phone = self.result_table.item(selected_row, 3).text()
        class_id = self.result_table.item(selected_row, 4).text()

        dialog = StudentDialog(self, name, gender, phone, class_id)
        if dialog.exec_() == QDialog.Accepted:
            db = create_connection()
            if not db:
                QMessageBox.critical(self, "数据库错误", "无法连接到数据库")
                return

            try:
                with db.cursor() as cursor:
                    sql = """
                        UPDATE student
                        SET name = %s, gender = %s, phone = %s, class_id = %s, update_time = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """
                    cursor.execute(sql, (
                        dialog.name_input.text(),
                        dialog.gender_combo.currentText(),
                        dialog.phone_input.text(),
                        dialog.class_id_input.text(),
                        student_id
                    ))
                    db.commit()
                    self.search_student()  # 刷新查询
            except Exception as e:
                QMessageBox.critical(self, "修改失败", f"数据库错误: {str(e)}")
            finally:
                db.close()

    def export_to_excel(self):
        try:
            data = []
            for row in range(self.result_table.rowCount()):
                row_data = [
                    self.result_table.item(row, 0).text(),
                    self.result_table.item(row, 1).text(),
                    self.result_table.item(row, 2).text()
                ]
                data.append(row_data)

            import pandas as pd
            df = pd.DataFrame(data, columns=["教师ID", "教师姓名", "总课时数"])
            df.to_excel("teacher_workload.xlsx", index=False)
            QMessageBox.information(self, "导出成功", "数据已导出为 teacher_workload.xlsx")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出失败: {str(e)}")


# ========== 3. 启动程序 ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 连接数据库
    db = create_connection()
    if not db:
        sys.exit(1)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

