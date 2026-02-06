import sqlite3
import random
import os

# 删除已存在的数据库文件
if os.path.exists('schedule.db'):
    os.remove('schedule.db')

# 连接到SQLite数据库
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# 创建表 (将MySQL语法转换为SQLite语法)
cursor.execute('''
CREATE TABLE class(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classname TEXT,
    number INTEGER
)
''')

cursor.execute('''
CREATE TABLE course(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coursename TEXT
)
''')

cursor.execute('''
CREATE TABLE schedule(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    teacher_id INTEGER,
    course_id INTEGER,
    weeks INTEGER,
    lessons INTEGER,
    remark TEXT
)
''')

cursor.execute('''
CREATE TABLE student(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    sex TEXT,
    class_id INTEGER
)
''')

cursor.execute('''
CREATE TABLE teacher(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    sex TEXT,
    age TEXT
)
''')

# 插入测试数据
print("正在插入测试数据...")

# 插入班级数据
classes = []
for i in range(1, 31):
    classname = f"班级{i}"
    number = random.randint(30, 50)
    cursor.execute("INSERT INTO class (classname, number) VALUES (?, ?)", (classname, number))
    classes.append((i, classname))

# 插入课程数据
courses = []
course_names = ["数学", "语文", "英语", "物理", "化学", "生物", "历史", "地理", "政治", "体育"]
for i in range(1, 31):
    coursename = course_names[(i-1) % len(course_names)] + str((i-1) // len(course_names) + 1)
    cursor.execute("INSERT INTO course (coursename) VALUES (?)", (coursename,))
    courses.append((i, coursename))

# 插入教师数据
teachers = []
sexes = ["男", "女"]
ages = [str(i) for i in range(25, 60)]
for i in range(1, 31):
    name = f"教师{i}"
    sex = random.choice(sexes)
    age = random.choice(ages)
    cursor.execute("INSERT INTO teacher (name, sex, age) VALUES (?, ?, ?)", (name, sex, age))
    teachers.append((i, name))

# 插入学生数据
students = []
for i in range(1, 31):
    name = f"学生{i}"
    sex = random.choice(sexes)
    class_id = random.randint(1, 30)
    cursor.execute("INSERT INTO student (name, sex, class_id) VALUES (?, ?, ?)", (name, sex, class_id))
    students.append((i, name))

# 插入排课数据
schedules = []
# 为避免冲突，我们生成不重复的 (weeks, lessons) 组合
used_slots = set()
for i in range(1, 31):
    class_id = random.randint(1, 30)
    teacher_id = random.randint(1, 30)
    course_id = random.randint(1, 30)
    
    # 确保生成唯一的 (weeks, lessons) 组合
    weeks = random.randint(1, 7)  # 一周7天
    lessons = random.randint(1, 8)  # 一天8节课
    
    # 确保不会产生完全重复的组合
    max_attempts = 100
    attempts = 0
    while (weeks, lessons) in used_slots and attempts < max_attempts:
        weeks = random.randint(1, 7)
        lessons = random.randint(1, 8)
        attempts += 1
    
    used_slots.add((weeks, lessons))
    
    remark = f"备注{i}"
    cursor.execute("INSERT INTO schedule (class_id, teacher_id, course_id, weeks, lessons, remark) VALUES (?, ?, ?, ?, ?, ?)", 
                   (class_id, teacher_id, course_id, weeks, lessons, remark))
    schedules.append((i, class_id, teacher_id, course_id, weeks, lessons, remark))

print("测试数据插入完成")

# 提交事务
conn.commit()

# 查询并显示数据以验证
print("\n班级表数据:")
cursor.execute("SELECT * FROM class LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\n课程表数据:")
cursor.execute("SELECT * FROM course LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\n教师表数据:")
cursor.execute("SELECT * FROM teacher LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\n排课表数据:")
cursor.execute("SELECT * FROM schedule LIMIT 5")
for row in cursor.fetchall():
    print(row)

# 关闭连接
conn.close()

print("\n数据库初始化完成!")