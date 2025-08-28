# u8_stock_api.py (适配 SQL Server 2012)
import pyodbc
import pandas as pd
from flask import Flask, jsonify, request
import json

# ==================== 数据库配置 ====================
server = '10.101.156.36'
database = 'UFDATA_999_2013'
username = 'U8reader'
password = 'U8@12345678'  # 请替换为真实密码

def get_db_connection():
    # 尝试不同的ODBC驱动程序
    drivers = [
        '{SQL Server Native Client 11.0}',             # SQL Server 2012 原生客户端
        '{ODBC Driver 17 for SQL Server}',    # 最新推荐驱动
        '{ODBC Driver 13 for SQL Server}',    # SQL Server 2012 兼容驱动

        '{SQL Server}'                        # 通用SQL Server驱动
    ]
    
    for driver in drivers:
        try:
            conn_str = (
                f'DRIVER={driver};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
                f'TIMEOUT=60;'
            )
            print(f"尝试使用驱动程序: {driver}")
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"驱动程序 {driver} 连接失败: {str(e)}")
            continue
    
    raise Exception("所有可用的ODBC驱动程序都无法连接数据库，请确认已安装合适的ODBC驱动程序")

def convert_bytes_to_string(data):
    """
    将数据中的字节类型转换为字符串
    """
    if isinstance(data, bytes):
        try:
            # 尝试 UTF-8 解码
            return data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # 尝试 GBK 解码（中文环境常见编码）
                return data.decode('gbk')
            except UnicodeDecodeError:
                # 如果都失败，使用 base64 编码
                import base64
                return base64.b64encode(data).decode('ascii')
    elif isinstance(data, dict):
        return {key: convert_bytes_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_bytes_to_string(item) for item in data]
    elif pd.isna(data):
        return ''
    else:
        return data

def get_current_stock(inv_code=None):
    conn = get_db_connection()
    # 使用简单的 select * 查询
    query = "SELECT * FROM V_CurrentStock"
    
    # 如果指定了存货编码，则添加过滤条件
    if inv_code:
        query += f" WHERE cInvCode LIKE '%{inv_code}%'"

    df = pd.read_sql(query, conn)
    conn.close()
    
    # 处理可能的字节类型数据
    for col in df.columns:
        df[col] = df[col].apply(lambda x: convert_bytes_to_string(x))
    
    df = df.fillna('')
    return df.to_dict(orient='records')


# ==================== Flask API ====================
app = Flask(__name__)


@app.route('/api/current_stock', methods=['GET'])
def api_current_stock():
    try:
        inv_code = request.args.get('code', None)
        data = get_current_stock(inv_code=inv_code)
        # 确保数据中没有字节类型后再返回
        data = convert_bytes_to_string(data)
        return jsonify({
            'success': True,
            'total': len(data),
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/')
def index():
    return '''
    <h3>用友U8现存量查询API (SQL Server 2012 兼容版)</h3>
    <p><strong>接口地址：</strong> 
       <a href="/api/current_stock">/api/current_stock</a>
    </p>
    <p><strong>按编码查询：</strong> 
       <a href="/api/current_stock?code=00702">/api/current_stock?code=00702</a>
    </p>
    <p>✅ 自动适配多种ODBC驱动程序</p>
    '''


if __name__ == '__main__':
    print("🚀 用友U8现存量API服务启动中...")
    print("🔍 尝试连接数据库...")
    try:
        conn = get_db_connection()
        conn.close()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print("💡 请确保已安装合适的ODBC驱动程序:")
        print("   - ODBC Driver 17 for SQL Server (推荐)")
        print("   - ODBC Driver 13 for SQL Server")
        print("   - SQL Server Native Client 11.0")
    print("🌐 访问 http://localhost:5000 查看首页")
    app.run(host='0.0.0.0', port=5000, debug=True)