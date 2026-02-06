import pandas as pd
import sqlite3
import os
import re
from typing import Dict, List


class SoftwareDataCleaner:
    def __init__(self, db_path: str = "software_data.db"):
        """
        初始化数据清洗器
        
        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path
        self.software_categories = {
            "压缩 PDF": ["压缩", "pdf", "解压", "7zip", "rar", "zip", "winrar", "winzip", "福昕", "adobe reader", "acrobat"],
            "Microsoft Office": ["office", "word", "excel", "powerpoint", "outlook", "access", "publisher", "onenote", "microsoft office"],
            "杀毒软件": ["杀毒", "病毒", "防护", "安全", "360", "卡巴斯基", "诺顿", "小红伞", "迈克菲", "avast", "avg", "bitdefender", "norton", "kaspersky", "瑞星", "江民"],
            "扫描软件": ["扫描", "scan", "ocr", "图像识别", "扫描仪", "尚书", "七彩"],
            "打印机软件": ["打印", "printer", "惠普", "hp", "佳能", "canon", "爱普生", "epson", "兄弟", "brother", "联想", "lenovo", "三星", "samsumg", "lexmark"],
            "Microsoft OneDrive": ["onedrive", "one drive"],
            "Microsoft Update Health Tools": ["update health tools", "health tools"],
            "Microsoft Visual C++ Redistributable 系列": ["visual c", "vc redist", "microsoft visual c", "vcredist", "vc++", "c++ redistributable"],
            "Microsoft Visual Studio 2010 Tools for Office Runtime": ["visual studio 2010 tools for office runtime"],
            "Microsoft 系列其他组件（含运行时、更新包）": ["microsoft", ".net", "runtime", "framework", "activex", "directx", "xna", "silverlight", "visual studio", "msxml", "windows update", "wmi"],
            "远程桌面连接": ["远程桌面", "remote desktop", "mstsc", "rdp", "远程协助"],
            "腾讯系列软件（QQ、微信、企业微信、腾讯会议等）": ["qq", "微信", "wechat", "企业微信", "腾讯会议", "tim", "tencent", "wegame"],
            "输入法": ["输入法", "ime", "搜狗", "sougou", "百度输入法", "谷歌输入法", "讯飞输入法", "qq输入法", "微软拼音", "五笔", "rime"],
            "远程控制 / 连接工具": ["远程控制", "teamviewer", "anydesk", "向日葵", "sunlogin", "vnc", "ssh", "telnet", "toDesk", "rustdesk", "向日葵", "pcanywhere"],
            "浏览器": ["chrome", "firefox", "edge", "internet explorer", "ie", "safari", "opera", "uc", "夸克", "搜狗浏览器", "360浏览器", "火狐", "谷歌", "遨游", "猎豹"],
            "设计 / 工程类软件": ["photoshop", "ps", "illustrator", "ai", "indesign", "id", "autocad", "cad", "3ds max", "3dmax", "sketchup", "coreldraw", "cdr", "blender", "caxa", "solidworks", "pro/e", "ug", "catia", "ansys", "adobe", "dreamweaver", "dw", "flash", "premiere", "pr", "after effects", "ae"],
            "驱动管理工具": ["驱动", "driver", "驱动精灵", "驱动人生", "鲁大师", "dism", "显卡驱动", "声卡驱动", "主板驱动"],
            "财务 / 企业系统/安全控件 / 证书类软件": ["财务", "用友", "金蝶", "税控", "发票", "会计", "erp", "oa", "安全控件", "证书", "ca", "网银", "银行", "证券"],
            "报关系统": ["报关", "海关", "国际贸易", "物流", "报检"],
            "其他工具软件": []  # 默认类别
        }
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()
    
    def create_table(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS software_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_name TEXT NOT NULL,
                category TEXT NOT NULL,
                original_row INTEGER
            )
        ''')
        self.conn.commit()
    
    def categorize_software(self, app_name: str) -> str:
        """
        根据软件名称分类
        
        Args:
            app_name: 软件名称
            
        Returns:
            分类名称
        """
        if not app_name or pd.isna(app_name):
            return "其他工具软件"
        
        app_lower = app_name.lower()
        
        # 检查是否为序列号格式（如：字母数字组合带连字符）
        serial_pattern = r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$'
        if re.match(serial_pattern, app_name.strip()):
            # 如果是标准序列号格式，暂时归类为"其他工具软件"
            # 实际上序列号本身不是软件名，但按题目要求需进行分类
            pass  # 继续执行后续分类逻辑
        
        for category, keywords in self.software_categories.items():
            for keyword in keywords:
                if keyword.lower() in app_lower:
                    return category
        
        # 特殊处理：如果包含"序列号"或"license"等词
        if "序列号" in app_name or "license" in app_lower or "key" in app_lower:
            # 尝试从描述中提取软件信息
            if "office" in app_lower:
                return "Microsoft Office"
            elif "adobe" in app_lower or "acrobat" in app_lower:
                return "设计 / 工程类软件"
            elif "杀毒" in app_name or "security" in app_lower:
                return "杀毒软件"
            elif "pdf" in app_lower:
                return "压缩 PDF"
            elif "qq" in app_lower or "wechat" in app_lower or "微信" in app_name:
                return "腾讯系列软件（QQ、微信、企业微信、腾讯会议等）"
            elif "chrome" in app_lower or "firefox" in app_lower or "edge" in app_lower:
                return "浏览器"
            elif "cad" in app_lower or "design" in app_lower:
                return "设计 / 工程类软件"
            elif "printer" in app_lower or "打印" in app_name:
                return "打印机软件"
            elif "antivirus" in app_lower:
                return "杀毒软件"
            else:
                return "其他工具软件"
        
        return "其他工具软件"
    
    def clean_and_insert_data(self, excel_path: str, sheet_name: str = None):
        """
        从Excel读取数据，清洗后插入数据库
        
        Args:
            excel_path: Excel文件路径
            sheet_name: 表名，默认为第一个表
        """
        # 读取Excel文件
        try:
            if sheet_name is None:
                # 如果没有指定工作表，则读取第一个工作表
                xl_file = pd.ExcelFile(excel_path)
                sheet_name = xl_file.sheet_names[0]
                    
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        except Exception as e:
            print(f"读取Excel文件失败: {e}")
            return
        
        print(f"Excel文件包含 {len(df)} 行数据，{len(df.columns)} 列")
        
        # 检查是否有A列或名为"应用"的列
        target_column = None
        # 首先尝试直接访问A列 (第1列，索引为0)
        if len(df.columns) > 0:  # A是第1列 (0-indexed为0)
            # 获取A列对应的列名
            a_col_name = df.columns[0]
            if a_col_name is not None and str(a_col_name).strip() != '':
                # 如果A列有标题，使用该标题
                target_column = a_col_name
            else:
                # 如果A列标题为空，使用索引作为列名
                target_column = df.columns[0]
                
        # 如果没找到A列，再检查是否有名为"应用"的列
        if target_column is None:
            if '应用' in df.columns:
                target_column = '应用'
            else:
                # 尝试查找可能表示"应用"的列
                for col in df.columns:
                    if '应用' in str(col) or 'application' in str(col).lower():
                        target_column = col
                        break
        
        if target_column is None:
            print("未找到A列或名为'应用'的列")
            print(f"可用列: {list(df.columns)}")
            return
        
        print(f"找到目标列: {target_column}")
        
        # 清洗数据并插入数据库
        cursor = self.conn.cursor()
        
        # 先清空表
        cursor.execute("DELETE FROM software_data")
        
        processed_count = 0
        for idx, row in df.iterrows():
            app_name = row[target_column]
            
            # 跳过空值
            if pd.isna(app_name) or app_name is None or str(app_name).strip() == '':
                continue
            
            # 检查是否为逗号分隔的多个应用
            if ',' in str(app_name):
                # 将逗号分隔的应用拆分为独立的应用
                apps = [app.strip() for app in str(app_name).split(',')]
                for single_app in apps:
                    if single_app and single_app.strip():
                        # 分类
                        category = self.categorize_software(single_app.strip())
                        
                        # 调试输出前几行数据
                        if processed_count < 5:
                            print(f"  行 {idx + 2}: '{single_app.strip()}' -> {category}")

                        # 插入数据库
                        cursor.execute(
                            "INSERT INTO software_data (application_name, category, original_row) VALUES (?, ?, ?)",
                            (single_app.strip(), category, idx + 2)  # +2 因为Excel行号从1开始，标题占一行
                        )
                        processed_count += 1
            else:
                # 单个应用名称
                # 分类
                category = self.categorize_software(str(app_name))
                
                # 调试输出前几行数据
                if processed_count < 5:
                    print(f"  行 {idx + 2}: '{app_name}' -> {category}")

                # 插入数据库
                cursor.execute(
                    "INSERT INTO software_data (application_name, category, original_row) VALUES (?, ?, ?)",
                    (str(app_name).strip(), category, idx + 2)  # +2 因为Excel行号从1开始，标题占一行
                )
                processed_count += 1

        self.conn.commit()
        print(f"数据清洗完成，共处理 {len(df)} 行数据，其中有效数据 {processed_count} 条")
    
    def sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不兼容的字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除或替换不兼容的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 处理其他潜在问题字符
        filename = filename.replace('\u00A0', '_')  # 替换不间断空格
        filename = filename.replace('\u3000', '_')  # 替换全角空格
        
        return filename
    
    def export_by_category(self, output_dir: str = "output"):
        """
        按类别导出数据
        
        Args:
            output_dir: 输出目录
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        cursor = self.conn.cursor()
        
        # 获取所有类别
        cursor.execute("SELECT DISTINCT category FROM software_data ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        # 按类别导出
        for category in categories:
            cursor.execute(
                "SELECT application_name, original_row FROM software_data WHERE category = ? ORDER BY application_name",
                (category,)
            )
            rows = cursor.fetchall()
            
            # 创建DataFrame
            category_df = pd.DataFrame(rows, columns=['应用名称', '原始行号'])
            
            # 去重：相同应用名称只保留一条记录（保留第一次出现的记录）
            category_df_unique = category_df.drop_duplicates(subset=['应用名称'], keep='first')
            
            # 使用清理后的类别名作为文件名
            sanitized_category = self.sanitize_filename(category)
            output_path = os.path.join(output_dir, f"{sanitized_category}.csv")
            category_df_unique.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"已导出 {category} 类别到 {output_path}")
    
    def print_statistics(self):
        """打印统计信息"""
        cursor = self.conn.cursor()
        
        # 总数统计
        cursor.execute("SELECT COUNT(*) FROM software_data")
        total_count = cursor.fetchone()[0]
        print(f"\n总软件数量: {total_count}")
        
        # 各类别统计
        cursor.execute("SELECT category, COUNT(*) FROM software_data GROUP BY category ORDER BY COUNT(*) DESC")
        category_stats = cursor.fetchall()
        
        print("\n各分类统计:")
        for category, count in category_stats:
            print(f"  {category}: {count} 个")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def main():
    # 设置文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = None
    
    # 查找当前目录下的Excel文件
    for file in os.listdir(current_dir):
        if file.lower().endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
            excel_file = os.path.join(current_dir, file)
            break
    
    if not excel_file:
        print("未在当前目录找到Excel文件")
        return
    
    print(f"找到Excel文件: {excel_file}")
    
    # 创建数据清洗器
    cleaner = SoftwareDataCleaner()
    
    try:
        # 清洗并插入数据
        cleaner.clean_and_insert_data(excel_file)
        
        # 打印统计信息
        cleaner.print_statistics()
        
        # 按类别导出数据
        cleaner.export_by_category()
        
    finally:
        cleaner.close()


if __name__ == "__main__":
    main()