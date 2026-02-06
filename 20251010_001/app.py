import pandas as pd
import sqlite3
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from config import config

# 定义词汇分类的自定义顺序 - 确保与数据库中的实际名称完全匹配
CATEGORY_ORDER = [
    '化学品名称',
    '制造相关',
    '分析指标&仪器',
    '公司&人员名称',
    '庆典仪式',
    '其它',
]

# 用户角色定义
USER_ROLES = {
    'admin': '管理员',
    'user': '普通用户'
}

def create_app(config_name=None):
    app = Flask(__name__)
    
    # 配置应用
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    app.secret_key = app.config['SECRET_KEY']
    
    # 配置日志
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )

    # 数据库文件名
    DB_NAME = app.config['DATABASE_URL']

    def init_db():
        """初始化数据库，将Excel数据导入SQLite"""
        if os.path.exists(DB_NAME):
            return
        
        # 读取Excel文件
        df = pd.read_excel('japan.xlsx')
        
        # 创建数据库连接
        conn = sqlite3.connect(DB_NAME)
        
        # 将数据存储到SQLite数据库
        df.to_sql('japan_data', conn, if_exists='replace', index=True)
        
        # 创建索引以提高查询性能
        cursor = conn.cursor()
        for column in df.columns:
            if df[column].dtype == 'object':  # 文本列
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{column} ON japan_data ({column})")
                except:
                    pass  # 某些列名可能包含特殊字符
        
        conn.commit()
        conn.close()

    def get_db_connection():
        """获取数据库连接"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @app.route('/')
    def index():
        """首页，显示搜索框"""
        conn = get_db_connection()
        # 获取所有唯一的词汇分类
        cursor = conn.execute("SELECT DISTINCT 词汇分类 FROM japan_data ORDER BY 词汇分类 DESC")
        all_categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 按照自定义顺序排序
        def category_sort_key(category):
            try:
                return CATEGORY_ORDER.index(category)
            except ValueError:
                return len(CATEGORY_ORDER)  # 不在列表中的放到最后，按字母顺序排列
        
        categories = sorted(all_categories, key=category_sort_key)
        
        # 获取用户角色
        user_role = session.get('user_role')
        
        return render_template('index.html', categories=categories, user_role=user_role)

    @app.route('/search')
    def search():
        """搜索页面"""
        query = request.args.get('query', '').strip()
        category = request.args.get('category', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        conn = get_db_connection()
        
        # 构建查询条件
        if query or category:
            # 构建WHERE子句
            where_conditions = []
            params = []
            
            if query:
                search_term = f"%{query}%"
                where_conditions.append("(中文 LIKE ? OR 日语 LIKE ? OR 发音 LIKE ? OR 词汇分类 LIKE ? OR 备注 LIKE ?)")
                params.extend([search_term, search_term, search_term, search_term, search_term])
            
            if category:
                where_conditions.append("词汇分类 = ?")
                params.append(category)
            
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM japan_data {where_clause}"
            cursor = conn.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # 查询数据
            data_query = f"""
                SELECT * FROM japan_data 
                {where_clause}
                ORDER BY 序号
                LIMIT ? OFFSET ?
            """
            params.extend([per_page, (page-1)*per_page])
            cursor = conn.execute(data_query, params)
            results = cursor.fetchall()
        else:
            # 获取总数
            count_query = "SELECT COUNT(*) FROM japan_data"
            cursor = conn.execute(count_query)
            total = cursor.fetchone()[0]
            
            # 获取所有数据
            data_query = "SELECT * FROM japan_data ORDER BY 序号 LIMIT ? OFFSET ?"
            cursor = conn.execute(data_query, (per_page, (page-1)*per_page))
            results = cursor.fetchall()
        
        conn.close()
        
        # 计算分页信息
        total_pages = (total + per_page - 1) // per_page
        
        # 计算当前页面的起始序号
        start_index = (page - 1) * per_page + 1
        
        # 获取用户角色
        user_role = session.get('user_role')
        
        return render_template('search.html', 
                             results=results, 
                             query=query,
                             category=category,
                             page=page, 
                             total_pages=total_pages, 
                             total=total,
                             start_index=start_index,
                             user_role=user_role)

    @app.route('/add', methods=['GET', 'POST'])
    def add():
        """添加新记录"""
        if request.method == 'POST':
            try:
                # 获取表单数据
                category = request.form['category']
                chinese = request.form['chinese']
                japanese = request.form['japanese']
                pronunciation = request.form['pronunciation']
                note = request.form['note']
                
                conn = get_db_connection()
                
                # 获取最大序号
                cursor = conn.execute("SELECT MAX(CAST(序号 AS INTEGER)) FROM japan_data")
                max_id = cursor.fetchone()[0]
                new_id = str(int(max_id) + 1) if max_id else "1"
                
                # 插入新记录
                # Let SQLite handle the index automatically by not specifying it
                conn.execute("""
                    INSERT INTO japan_data (序号, 词汇分类, 中文, 日语, 发音, 备注)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (new_id, category, chinese, japanese, pronunciation, note))
                
                conn.commit()
                conn.close()
                
                flash('记录添加成功！', 'success')
                return redirect(url_for('search', query=chinese))
            except Exception as e:
                flash(f'添加记录时出错: {str(e)}', 'error')
        
        return render_template('add.html')

    @app.route('/edit/<int:index>', methods=['GET', 'POST'])
    def edit(index):
        """编辑记录"""
        # 检查用户权限
        if session.get('user_role') != 'admin':
            flash('您没有权限执行此操作！', 'error')
            return redirect(url_for('search'))
            
        conn = get_db_connection()
        
        if request.method == 'POST':
            try:
                # 获取表单数据
                category = request.form['category']
                chinese = request.form['chinese']
                japanese = request.form['japanese']
                pronunciation = request.form['pronunciation']
                note = request.form['note']
                
                # 更新记录 - 使用index作为主键
                conn.execute("""
                    UPDATE japan_data 
                    SET 词汇分类=?, 中文=?, 日语=?, 发音=?, 备注=?
                    WHERE "index"=?
                """, (category, chinese, japanese, pronunciation, note, index))
                
                conn.commit()
                conn.close()
                
                flash('记录更新成功！', 'success')
                return redirect(url_for('search', query=chinese))
            except Exception as e:
                flash(f'更新记录时出错: {str(e)}', 'error')
        
        # 获取要编辑的记录 - 使用index作为主键
        cursor = conn.execute('SELECT * FROM japan_data WHERE "index" = ?', (index,))
        record = cursor.fetchone()
        conn.close()
        
        if record is None:
            flash('记录未找到！', 'error')
            return redirect(url_for('search'))
        
        return render_template('edit.html', record=record)

    @app.route('/delete/<int:index>', methods=['POST'])
    def delete(index):
        """删除记录"""
        # 检查用户权限
        if session.get('user_role') != 'admin':
            flash('您没有权限执行此操作！', 'error')
            return redirect(url_for('search'))
            
        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM japan_data WHERE "index" = ?', (index,))
            conn.commit()
            conn.close()
            
            flash('记录删除成功！', 'success')
        except Exception as e:
            flash(f'删除记录时出错: {str(e)}', 'error')
        
        return redirect(url_for('search'))

    @app.route('/api/smart_search')
    def smart_search():
        """智能搜索API"""
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify([])
        
        conn = get_db_connection()
        
        # 根据不同字段进行搜索
        search_term = f"%{query}%"
        cursor = conn.execute("""
            SELECT * FROM japan_data 
            WHERE 中文 LIKE ? OR 日语 LIKE ? OR 发音 LIKE ? OR 词汇分类 LIKE ? OR 备注 LIKE ?
            ORDER BY 序号
            LIMIT 10
        """, (search_term, search_term, search_term, search_term, search_term))
        
        results = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表，并处理空值
        data = []
        for row in results:
            row_dict = dict(row)
            # 处理空值，将None显示为空白
            for key in row_dict:
                if row_dict[key] is None:
                    row_dict[key] = ""
            data.append(row_dict)
        
        return jsonify(data)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """用户登录"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            
            # 简单的身份验证
            if username == 'admin' and password == 'admin@123':
                session['user_role'] = 'admin'
                flash('管理员登录成功！', 'success')
                return redirect(url_for('index'))
            elif username == 'user' and password == 'user':
                session['user_role'] = 'user'
                flash('用户登录成功！', 'success')
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误！', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """用户登出"""
        session.pop('user_role', None)
        flash('您已成功登出！', 'success')
        return redirect(url_for('index'))
    
    # 初始化数据库
    with app.app_context():
        init_db()
    
    return app

app = create_app()

if __name__ == '__main__':
    # 修改主机绑定设置，允许外部访问
    app.run(debug=app.config['FLASK_DEBUG'], host='0.0.0.0')