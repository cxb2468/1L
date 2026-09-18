import pymysql

# 连接到数据库
conn = pymysql.connect(
    host="localhost",       # MySQL 服务器地址
    user="root",            # 用户名
    password="root",    # 密码
    database="school1"       # 数据库名称
)

# 创建一个游标对象
cursor = conn.cursor()

# 执行查询
cursor.execute("SELECT * FROM users")

# 获取结果
result = cursor.fetchall()
for row in result:
    print(row)

# 关闭连接
cursor.close()
conn.close()
