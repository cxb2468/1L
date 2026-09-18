import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkcalendar import DateEntry
import sqlite3
import csv
import re
import os
from datetime import datetime, timedelta
import chardet
from dateutil import parser
import calendar
import signal
import sys
import traceback


class FIFOProfitCalculator:
    def __init__(self, cursor):
        self.cursor = cursor

    def calculate_stock_profit(self, stock_code):
        """计算单只股票的盈亏（已实现盈亏 + 红利）"""
        # 获取股票的所有交易记录
        transactions = self._get_transactions(stock_code)

        # 分离买入和卖出记录
        buy_records = [t for t in transactions if t['direction'] == '买入']
        sell_records = [t for t in transactions if t['direction'] == '卖出']

        # 按交易日期排序
        buy_records.sort(key=lambda x: x['trade_date'])
        sell_records.sort(key=lambda x: x['trade_date'])

        # FIFO计算盈亏
        realized_profit = self._calculate_fifo_profit(buy_records, sell_records)

        # 计算红利
        dividend = self._get_dividends(stock_code)

        return realized_profit + dividend

    def _calculate_fifo_profit(self, buy_records, sell_records):
        """使用时间戳匹配最近批次的方法计算已实现盈亏"""
        total_profit = 0.0
        # 初始化买入批次（深拷贝）
        buy_batches = [
            {
                'trade_date': buy['trade_date'],
                'quantity': buy['quantity'],
                'remaining_quantity': buy['remaining_quantity'],
                'total_cost': buy['total_cost']
            }
            for buy in buy_records
        ]

        # 按交易日期升序处理卖出记录
        for sell in sorted(sell_records, key=lambda x: x['trade_date']):
            remaining_sell_quantity = sell['quantity']
            sell_income = sell['amount'] - sell['commission'] - sell['stamp_duty'] - sell['transfer_fee']
            sell_cost = 0.0

            while remaining_sell_quantity > 0:
                # 1. 筛选可用批次：卖出日期前 & 有剩余数量
                available_batches = [
                    batch for batch in buy_batches
                    if batch['trade_date'] <= sell['trade_date'] and batch['remaining_quantity'] > 0
                ]

                # 2. 按交易日期降序排序（最近的在前）
                available_batches.sort(key=lambda x: x['trade_date'], reverse=True)

                if not available_batches:
                    break  # 无可用批次

                # 3. 取最近的批次
                current_batch = available_batches[0]
                match_quantity = min(remaining_sell_quantity, current_batch['remaining_quantity'])
                cost_ratio = match_quantity / current_batch['quantity']
                matched_cost = current_batch['total_cost'] * cost_ratio

                # 4. 更新匹配数据
                sell_cost += matched_cost
                remaining_sell_quantity -= match_quantity
                current_batch['remaining_quantity'] -= match_quantity
                current_batch['total_cost'] -= matched_cost

                # 5. 移除剩余为0的批次
                if current_batch['remaining_quantity'] <= 0:
                    buy_batches.remove(current_batch)

            # 计算单笔盈亏
            total_profit += sell_income - sell_cost

        return total_profit

    def _get_transactions(self, stock_code):
        """从数据库获取交易记录"""
        self.cursor.execute('''
                            SELECT trade_date,
                                   direction,
                                   quantity,
                                   amount,
                                   commission,
                                   stamp_duty,
                                   transfer_fee
                            FROM transactions
                            WHERE stock_code = ?
                            ORDER BY trade_date
                            ''', (stock_code,))

        transactions = []  # 初始化交易记录空列表
        for row in self.cursor.fetchall():
            transactions.append({
                'trade_date': row[0],
                'direction': row[1],
                'quantity': row[2],
                'amount': row[3],
                'commission': row[4],
                'stamp_duty': row[5],
                'transfer_fee': row[6],
                'remaining_quantity': row[2],  # 初始剩余数量
                'total_cost': row[3] + row[4] + row[5] + row[6]  # 总成本
            })

        return transactions

    def _get_dividends(self, stock_code: str) -> float:
        """获取指定股票代码的红利总额

        参数：
            stock_code: 股票代码（如'AAPL'）

        返回：
            分红总额（无记录时返回0.0）
        """
        try:
            self.cursor.execute('''
                                SELECT COALESCE(SUM(dividend), 0.0)
                                FROM dividends
                                WHERE stock_code = ?
                                ''', (stock_code,))
            return self.cursor.fetchone()[0]  # 总是返回float类型
        except Exception as e:
            # 实际项目中应记录日志
            print(f"查询分红出错: {str(e)}")
            return 0.0


class StockManagementSystem:
    def __init__(self, root):
        self.dividend_detail_tree = None
        self.master = None
        self.position_trans_tree = None
        self.root = root
        self.root.title("股票交易管理系统")
        self.root.geometry("1200x800")

        # 设置中断信号处理
        signal.signal(signal.SIGINT, self.signal_handler)

        # 连接数据库 - 使用绝对路径确保一致性
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stock_management.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 创建数据库表
        self.create_tables()

        # 创建主界面
        self.create_main_interface()

        # 初始化股票代码下拉框
        self.update_stock_combobox()

        # 初始化交易记录表格
        self.refresh_transaction_table()

        # 初始化持仓表格
        self.refresh_position_table()

        # 初始化红利表格
        self.refresh_dividend_table()

        # 初始化资产表格
        self.refresh_asset_table()

        # 在打开软件时刷新资金流水列表
        self.refresh_cash_flow_table()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def signal_handler(self, signum, frame):
        """处理中断信号"""
        self.on_closing()
        sys.exit(0)

    def on_closing(self):
        """窗口关闭时的处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗?"):
            # 关闭数据库连接
            self.conn.close()
            self.root.destroy()

    def create_tables(self):
        # 股票代码表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS stock_codes
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                stock_code TEXT UNIQUE,
                                stock_name TEXT
                            )
                            ''')

        # 交易记录表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS transactions
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                stock_code TEXT,
                                stock_name TEXT,
                                price REAL,
                                quantity INTEGER,
                                trade_date TEXT,
                                commission REAL,
                                stamp_duty REAL,
                                transfer_fee REAL,
                                direction TEXT,
                                amount REAL
                            )
                            ''')

        # 红利记录表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS dividends
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                stock_code TEXT,
                                stock_name TEXT,
                                dividend REAL,
                                dividend_date DATE NOT NULL
                            )
                            ''')

        # 检查索引是否存在，不存在再创建
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_dividend_date'")
        if not self.cursor.fetchone():
            self.cursor.execute('''CREATE INDEX idx_dividend_date ON dividends (dividend_date)''')

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_stock_code'")
        if not self.cursor.fetchone():
            self.cursor.execute('''CREATE INDEX idx_stock_code ON dividends (stock_code);''')

        # 资金流水表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS cash_flow
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                amount REAL,
                                flow_date TEXT,
                                type TEXT,
                                description TEXT
                            )
                            ''')

        # 现金余额表
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS cash
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                balance REAL,
                                update_date TEXT
                            )
                            ''')

        self.conn.commit()

    def create_main_interface(self):
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 股票代码管理标签页
        self.stock_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stock_tab, text="股票代码管理")
        self.create_stock_tab()

        # 交易记录管理标签页
        self.transaction_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transaction_tab, text="交易记录管理")
        self.create_transaction_tab()

        # 持仓管理标签页
        self.position_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.position_tab, text="持仓管理")
        self.create_position_tab()

        # 红利管理标签页
        self.dividend_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dividend_tab, text="红利管理")
        self.create_dividend_tab()

        # 资产管理标签页
        self.asset_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.asset_tab, text="资产管理")
        self.create_asset_tab()

    def create_stock_tab(self):
        # 导入股票代码区域
        import_frame = ttk.LabelFrame(self.stock_tab, text="导入股票代码")
        import_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(import_frame, text="CSV文件路径:").grid(row=0, column=0, padx=5, pady=5)
        self.csv_path = ttk.Entry(import_frame, width=50)
        self.csv_path.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(import_frame, text="浏览", command=self.browse_csv).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(import_frame, text="导入", command=self.import_stock_codes).grid(row=0, column=3, padx=5, pady=5)

        # 手动添加股票代码区域
        add_frame = ttk.LabelFrame(self.stock_tab, text="手动添加股票代码")
        add_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(add_frame, text="股票代码:").grid(row=0, column=0, padx=5, pady=5)
        self.stock_code_entry = ttk.Entry(add_frame)
        self.stock_code_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="股票名称:").grid(row=0, column=2, padx=5, pady=5)
        self.stock_name_entry = ttk.Entry(add_frame)
        self.stock_name_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(add_frame, text="添加", command=self.add_stock_code).grid(row=0, column=4, padx=5, pady=5)

        # 股票代码列表
        list_frame = ttk.LabelFrame(self.stock_tab, text="股票代码列表")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "stock_code", "stock_name")
        self.stock_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        self.stock_tree.heading("id", text="ID")
        self.stock_tree.heading("stock_code", text="股票代码")
        self.stock_tree.heading("stock_name", text="股票名称")

        self.stock_tree.column("id", width=50)
        self.stock_tree.column("stock_code", width=100)
        self.stock_tree.column("stock_name", width=200)

        self.stock_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # 删除按钮
        ttk.Button(list_frame, text="删除选中项", command=self.delete_stock_code).pack(pady=5)

        # 刷新股票列表
        self.refresh_stock_list()

    def create_transaction_tab(self):
        # 手动添加交易记录区域
        add_frame = ttk.LabelFrame(self.transaction_tab, text="添加交易记录")
        add_frame.pack(fill='x', padx=10, pady=5)

        # 股票代码和名称
        ttk.Label(add_frame, text="股票代码:").grid(row=0, column=0, padx=5, pady=5)
        self.trans_stock_code = ttk.Combobox(add_frame, width=10)
        self.trans_stock_code.grid(row=0, column=1, padx=5, pady=5)
        self.trans_stock_code.bind("<<ComboboxSelected>>", self.on_stock_code_select)
        self.trans_stock_code.bind("<Return>", self.on_stock_code_enter)

        ttk.Label(add_frame, text="股票名称:").grid(row=0, column=2, padx=5, pady=5)
        self.trans_stock_name = ttk.Combobox(add_frame, width=15)
        self.trans_stock_name.grid(row=0, column=3, padx=5, pady=5)
        self.trans_stock_name.bind("<<ComboboxSelected>>", self.on_stock_name_select)
        self.trans_stock_name.bind("<Return>", self.on_stock_name_enter)

        # 委托类别
        ttk.Label(add_frame, text="委托类别:").grid(row=0, column=4, padx=5, pady=5)
        self.direction_var = tk.StringVar()
        self.direction_combo = ttk.Combobox(add_frame, textvariable=self.direction_var, width=8)
        self.direction_combo['values'] = ('买入', '卖出')
        self.direction_combo.current(0)
        self.direction_combo.grid(row=0, column=5, padx=5, pady=5)

        # 价格和数量
        ttk.Label(add_frame, text="价格:").grid(row=1, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(add_frame, width=10)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="数量:").grid(row=1, column=2, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(add_frame, width=10)
        self.quantity_entry.grid(row=1, column=3, padx=5, pady=5)

        # 日期
        ttk.Label(add_frame, text="日期:").grid(row=1, column=4, padx=5, pady=5)
        self.trans_date = DateEntry(add_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.trans_date.grid(row=1, column=5, padx=5, pady=5)

        # 费用
        ttk.Label(add_frame, text="佣金:").grid(row=2, column=0, padx=5, pady=5)
        self.commission_entry = ttk.Entry(add_frame, width=10)
        self.commission_entry.grid(row=2, column=1, padx=5, pady=5)
        self.commission_entry.insert(0, "0.00")

        ttk.Label(add_frame, text="印花税:").grid(row=2, column=2, padx=5, pady=5)
        self.stamp_duty_entry = ttk.Entry(add_frame, width=10)
        self.stamp_duty_entry.grid(row=2, column=3, padx=5, pady=5)
        self.stamp_duty_entry.insert(0, "0.00")

        ttk.Label(add_frame, text="过户费:").grid(row=2, column=4, padx=5, pady=5)
        self.transfer_fee_entry = ttk.Entry(add_frame, width=10)
        self.transfer_fee_entry.grid(row=2, column=5, padx=5, pady=5)
        self.transfer_fee_entry.insert(0, "0.00")

        # 按钮
        ttk.Button(add_frame, text="添加记录", command=self.add_transaction).grid(row=3, column=0, columnspan=6,
                                                                              pady=10)

        # 导入交易记录区域
        import_frame = ttk.LabelFrame(self.transaction_tab, text="导入交易记录")
        import_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(import_frame, text="CSV文件路径:").grid(row=0, column=0, padx=5, pady=5)
        self.trans_csv_path = ttk.Entry(import_frame, width=50)
        self.trans_csv_path.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(import_frame, text="浏览", command=self.browse_trans_csv).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(import_frame, text="导入", command=self.import_transactions).grid(row=0, column=3, padx=5, pady=5)

        # 交易记录列表
        list_frame = ttk.LabelFrame(self.transaction_tab, text="交易记录列表")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "stock_code", "stock_name", "price", "quantity", "trade_date",
                   "commission", "stamp_duty", "transfer_fee", "direction", "amount")
        self.trans_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        column_names = {"id": "ID",
                        "stock_code": "股票代码",
                        "stock_name": "股票名称",
                        "price": "成交价格",
                        "quantity": "成交数量",
                        "trade_date": "交易日期",
                        "commission": "佣金",
                        "stamp_duty": "印花税",
                        "transfer_fee": "过户费",
                        "direction": "委托类别",
                        "amount": "成交金额"}

        for col in columns:
            self.trans_tree.heading(col, text=column_names[col])
            self.trans_tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.trans_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # 删除按钮
        ttk.Button(list_frame, text="删除选中项", command=self.delete_transaction).pack(pady=5)

    def create_position_tab(self):
        # 持仓查询区域
        query_frame = ttk.LabelFrame(self.position_tab, text="持仓查询")
        query_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(query_frame, text="股票代码:").grid(row=0, column=0, padx=5, pady=5)
        self.position_stock_code = ttk.Combobox(query_frame, width=10)
        self.position_stock_code.grid(row=0, column=1, padx=5, pady=5)
        self.position_stock_code.bind("<<ComboboxSelected>>", self.on_position_stock_select)

        ttk.Button(query_frame, text="查询", command=self.query_position).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(query_frame, text="显示全部", command=self.show_all_positions).grid(row=0, column=3, padx=5, pady=5)

        # 交易记录列表
        trans_frame = ttk.LabelFrame(self.position_tab, text="交易记录")
        trans_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "stock_code", "stock_name", "price", "quantity", "trade_date",
                   "commission", "stamp_duty", "transfer_fee", "direction", "amount", "profit")
        self.position_trans_tree = ttk.Treeview(trans_frame, columns=columns, show="headings")

        column_names = {"id": "ID",
                        "stock_code": "股票代码",
                        "stock_name": "股票名称",
                        "price": "成交价格",
                        "quantity": "成交数量",
                        "trade_date": "交易日期",
                        "commission": "佣金",
                        "stamp_duty": "印花税",
                        "transfer_fee": "过户费",
                        "direction": "委托类别",
                        "amount": "成交金额",
                        "profit": "盈亏金额"}

        for col in columns:
            self.position_trans_tree.heading(col, text=column_names[col])
            self.position_trans_tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(trans_frame, orient="vertical", command=self.position_trans_tree.yview)
        self.position_trans_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.position_trans_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # 持仓汇总列表
        position_frame = ttk.LabelFrame(self.position_tab, text="持仓汇总")
        position_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("stock_code", "stock_name", "position")
        self.position_tree = ttk.Treeview(position_frame, columns=columns, show="headings")

        column_names = {"stock_code": "股票代码",
                        "stock_name": "股票名称",
                        "position": "持仓数量"}

        for col in columns:
            self.position_tree.heading(col, text=column_names[col])
            self.position_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(position_frame, orient="vertical", command=self.position_tree.yview)
        self.position_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.position_tree.pack(fill='both', expand=True, padx=5, pady=5)

    def create_dividend_tab(self):
        # 添加红利记录区域
        add_frame = ttk.LabelFrame(self.dividend_tab, text="添加/修改红利记录")
        add_frame.pack(fill='x', padx=10, pady=5)

        # 股票代码和名称
        ttk.Label(add_frame, text="股票代码:").grid(row=0, column=0, padx=5, pady=5)
        self.div_stock_code = ttk.Combobox(add_frame, width=10)
        self.div_stock_code.grid(row=0, column=1, padx=5, pady=5)
        self.div_stock_code.bind("<<ComboboxSelected>>", self.on_div_stock_select)
        self.div_stock_code.bind("<Return>", self.on_div_stock_code_enter)

        ttk.Label(add_frame, text="股票名称:").grid(row=0, column=2, padx=5, pady=5)
        self.div_stock_name = ttk.Entry(add_frame, width=15, state='readonly')
        self.div_stock_name.grid(row=0, column=3, padx=5, pady=5)

        # 红利金额
        ttk.Label(add_frame, text="红利金额:").grid(row=1, column=0, padx=5, pady=5)
        self.dividend_entry = ttk.Entry(add_frame, width=10)
        self.dividend_entry.grid(row=1, column=1, padx=5, pady=5)

        # 日期
        ttk.Label(add_frame, text="日期:").grid(row=1, column=2, padx=5, pady=5)
        self.div_date = DateEntry(add_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.div_date.grid(row=1, column=3, padx=5, pady=5)

        # 按钮区域
        btn_frame = ttk.Frame(add_frame)
        btn_frame.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

        # 添加和修改按钮
        self.add_btn = ttk.Button(btn_frame, text="添加", command=self.add_dividend)
        self.add_btn.pack(side=tk.LEFT, padx=2)

        self.modify_btn = ttk.Button(btn_frame, text="修改", command=self.modify_dividend, state=tk.DISABLED)
        self.modify_btn.pack(side=tk.LEFT, padx=2)

        # 红利列表区域
        list_frame = ttk.LabelFrame(self.dividend_tab, text="红利记录")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # 年份筛选器
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(filter_frame, text="选择年份:").pack(side=tk.LEFT, padx=5)
        self.year_combo = ttk.Combobox(filter_frame, width=8, state="readonly")
        self.year_combo.pack(side=tk.LEFT, padx=5)

        # 初始化年份选择器
        self.update_year_combobox()

        # 绑定选择事件
        self.year_combo.bind("<<ComboboxSelected>>", self.refresh_dividend_table)

        # 刷新按钮
        ttk.Button(filter_frame, text="刷新", command=self.refresh_dividend_table).pack(side=tk.LEFT, padx=5)

        # 红利表格
        columns = ["year", "stock_code", "stock_name", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Total"]

        self.dividend_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        # 配置列标题和宽度
        column_names = {
            "year": "年份",
            "stock_code": "股票代码",
            "stock_name": "股票名称",
            "Jan": "一月", "Feb": "二月", "Mar": "三月", "Apr": "四月",
            "May": "五月", "Jun": "六月", "Jul": "七月", "Aug": "八月",
            "Sep": "九月", "Oct": "十月", "Nov": "十一月", "Dec": "十二月",
            "Total": "红利总和"
        }

        for col in columns:
            self.dividend_tree.heading(col, text=column_names[col])
            self.dividend_tree.column(col, width=60, anchor=tk.CENTER)

        # 绑定选择事件
        self.dividend_tree.bind("<<TreeviewSelect>>", self.on_dividend_select)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.dividend_tree.yview)
        self.dividend_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.dividend_tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.update_year_combobox()

    def create_asset_tab(self):
        # 资产查询区域
        query_frame = ttk.LabelFrame(self.asset_tab, text="资产查询")
        query_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(query_frame, text="查询日期:").grid(row=0, column=0, padx=5, pady=5)
        self.asset_date = DateEntry(query_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.asset_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(query_frame, text="查询日盈亏", command=self.query_daily_profit).grid(row=0, column=2, padx=5,
                                                                                    pady=5)
        ttk.Button(query_frame, text="查询月盈亏", command=self.query_monthly_profit).grid(row=0, column=3, padx=5,
                                                                                      pady=5)
        ttk.Button(query_frame, text="查询年盈亏", command=self.query_yearly_profit).grid(row=0, column=4, padx=5,
                                                                                     pady=5)

        # 资产列表区域
        asset_frame = ttk.LabelFrame(self.asset_tab, text="持仓资产")
        asset_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("stock_code", "stock_name", "position", "cost", "profit")
        self.asset_tree = ttk.Treeview(asset_frame, columns=columns, show="headings")

        column_names = {"stock_code": "股票代码",
                        "stock_name": "股票名称",
                        "position": "持仓数量",
                        "cost": "持仓成本",
                        "profit": "盈亏金额"}

        for col in columns:
            self.asset_tree.heading(col, text=column_names[col])
            self.asset_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(asset_frame, orient="vertical", command=self.asset_tree.yview)
        self.asset_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.asset_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # 资金流水区域
        cash_frame = ttk.LabelFrame(self.asset_tab, text="资金流水")
        cash_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ("id", "amount", "flow_date", "type")
        self.cash_tree = ttk.Treeview(cash_frame, columns=columns, show="headings")

        column_names = {"id": "ID",
                        "amount": "金额",
                        "flow_date": "日期",
                        "type": "类型"}

        for col in columns:
            self.cash_tree.heading(col, text=column_names[col])
            self.cash_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(cash_frame, orient="vertical", command=self.cash_tree.yview)
        self.cash_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.cash_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # 添加资金流水按钮
        ttk.Button(cash_frame, text="添加入账", command=lambda: self.add_cash_flow("入账")).pack(side="left", padx=5, pady=5)
        ttk.Button(cash_frame, text="添加出账", command=lambda: self.add_cash_flow("出账")).pack(side="left", padx=5, pady=5)
        ttk.Button(cash_frame, text="利润提取", command=lambda: self.add_cash_flow("利润提取")).pack(side="left", padx=5,
                                                                                             pady=5)

        # 删除资金流水按钮
        ttk.Button(cash_frame, text="删除选中", command=self.delete_cash_flow).pack(side="right", padx=5, pady=5)

        # 状态栏显示总资产和总盈亏
        self.status_frame = ttk.Frame(self.asset_tab)
        self.status_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(self.status_frame, text="总盈亏:").grid(row=0, column=2, padx=5, sticky='e')
        self.total_profit_var = tk.StringVar(value="0.00")
        ttk.Label(self.status_frame, textvariable=self.total_profit_var, width=10).grid(row=0, column=3, padx=5,
                                                                                        sticky='w')

        ttk.Label(self.status_frame, text="提取利润金额:").grid(row=1, column=0, padx=5, sticky='e')
        self.withdrawn_profit_var = tk.StringVar(value="0.00")
        ttk.Label(self.status_frame, textvariable=self.withdrawn_profit_var, width=10).grid(row=1, column=1, padx=5,
                                                                                            sticky='w')

        ttk.Label(self.status_frame, text="盈亏余额:").grid(row=1, column=2, padx=5, sticky='e')
        self.profit_balance_var = tk.StringVar(value="0.00")
        ttk.Label(self.status_frame, textvariable=self.profit_balance_var, width=10).grid(row=1, column=3, padx=5,
                                                                                          sticky='w')

        ttk.Label(self.status_frame, text="入账金额:").grid(row=1, column=4, padx=5, sticky='e')
        self.income_amount_var = tk.StringVar(value="0.00")
        ttk.Label(self.status_frame, textvariable=self.income_amount_var, width=10).grid(row=1, column=5, padx=5,
                                                                                         sticky='w')

        ttk.Label(self.status_frame, text="出账金额:").grid(row=1, column=6, padx=5, sticky='e')
        self.expense_amount_var = tk.StringVar(value="0.00")
        ttk.Label(self.status_frame, textvariable=self.expense_amount_var, width=10).grid(row=1, column=7, padx=5,
                                                                                          sticky='w')

    # 股票代码管理功能
    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_path.delete(0, tk.END)
            self.csv_path.insert(0, file_path)

    def import_stock_codes(self):
        file_path = self.csv_path.get()
        if not file_path:
            messagebox.showerror("错误", "请选择CSV文件")
            return

        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            # 检测分隔符
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1024)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter

            # 读取CSV文件
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                messagebox.showinfo("导入结果", "CSV文件中没有数据")
                return

            # 查找股票代码和股票名称列
            code_aliases = ["证券代码", "股票代码", "代码"]
            name_aliases = ["证券名称", "股票名称", "名称"]

            code_col = None
            name_col = None

            for col in reader.fieldnames:
                if col in code_aliases:
                    code_col = col
                if col in name_aliases:
                    name_col = col

            if not code_col or not name_col:
                messagebox.showerror("错误", "未找到股票代码或股票名称列")
                return

            # 导入数据
            success = 0
            errors = []

            for i, row in enumerate(rows, start=1):
                try:
                    code = row[code_col].strip()
                    name = row[name_col].strip()

                    # 验证股票代码
                    if not code.isdigit() or len(code) > 6:
                        errors.append(f"行 {i}: 无效的股票代码 '{code}'")
                        continue

                    # 补全股票代码
                    code = code.zfill(6)

                    # 插入数据库
                    self.cursor.execute("INSERT OR IGNORE INTO stock_codes (stock_code, stock_name) VALUES (?, ?)",
                                        (code, name))
                    success += 1
                except Exception as e:
                    errors.append(f"行 {i}: {str(e)}")

            self.conn.commit()
            self.refresh_stock_list()
            self.update_stock_combobox()

            # 显示导入结果
            result_msg = f"成功导入 {success} 条记录"
            if errors:
                result_msg += f"\n失败 {len(errors)} 条记录:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    result_msg += f"\n...及其他 {len(errors) - 5} 条错误"

            messagebox.showinfo("导入结果", result_msg)

        except Exception as e:
            messagebox.showerror("导入错误", f"导入过程中发生错误: {str(e)}")

    def add_stock_code(self):
        code = self.stock_code_entry.get().strip()
        name = self.stock_name_entry.get().strip()

        if not code or not name:
            messagebox.showerror("错误", "股票代码和名称不能为空")
            return

        # 验证股票代码
        if not code.isdigit() or len(code) > 6:
            messagebox.showerror("错误", "股票代码必须是6位数字")
            return

        # 补全股票代码
        code = code.zfill(6)

        try:
            self.cursor.execute("INSERT INTO stock_codes (stock_code, stock_name) VALUES (?, ?)", (code, name))
            self.conn.commit()

            self.stock_code_entry.delete(0, tk.END)
            self.stock_name_entry.delete(0, tk.END)

            self.refresh_stock_list()
            self.update_stock_combobox()

            messagebox.showinfo("成功", "股票代码添加成功")
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "该股票代码已存在")

    def delete_stock_code(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要删除的记录")
            return

        item = self.stock_tree.item(selected[0])
        # 确保获取完整的股票代码格式（包含前导零）
        raw_code = item['values'][1]
        # 格式化股票代码，确保是6位数字格式
        code = str(raw_code).zfill(6) if isinstance(raw_code, (int, float)) else str(raw_code).ljust(6, '0')[:6]
        print(f"[调试] 尝试删除股票代码: 原始格式='{raw_code}', 格式化后='{code}'")
        print(f"[调试] 数据库路径: {self.conn.execute('PRAGMA database_list').fetchall()}")

        try:
            # 调试：在删除前检查数据库中是否存在该股票代码
            self.cursor.execute("SELECT COUNT(*) FROM stock_codes WHERE stock_code = ?", (code,))
            exists_before = self.cursor.fetchone()[0]
            print(f"[调试] 删除前数据库中股票代码 {code} 存在数量: {exists_before}")

            # 获取股票的交易数量
            self.cursor.execute("SELECT SUM(quantity) FROM transactions WHERE stock_code = ?", (code,))
            result = self.cursor.fetchone()[0]
            transaction_quantity = result if result is not None else 0

            # 如果有交易数量，提示用户确认
            if transaction_quantity != 0:
                confirm = messagebox.askyesno("确认操作", "该股票存在历史交易数量，直接删除可能导致盈亏计算误差。是否确认彻底删除?")
                if not confirm:
                    return

            # 开始事务
            self.conn.execute("BEGIN TRANSACTION")

            # 先尝试删除关联记录
            self.cursor.execute("DELETE FROM dividends WHERE stock_code = ?", (code,))
            div_count = self.cursor.rowcount

            self.cursor.execute("DELETE FROM transactions WHERE stock_code = ?", (code,))
            trans_count = self.cursor.rowcount

            # 最后删除股票代码本身
            self.cursor.execute("DELETE FROM stock_codes WHERE stock_code = ?", (code,))
            stock_count = self.cursor.rowcount

            # 提交事务
            self.conn.commit()
            print(f"[调试] 事务已提交，删除记录计数: 红利记录={div_count}, 交易记录={trans_count}, 股票代码={stock_count}")

            # 验证删除后数据库状态
            self.cursor.execute("SELECT COUNT(*) FROM stock_codes WHERE stock_code = ?", (code,))
            exists_after = self.cursor.fetchone()[0]
            print(f"[调试] 删除后数据库中股票代码 {code} 存在数量: {exists_after}")

            # 验证删除是否成功
            if stock_count > 0:
                # 从UI中移除项目
                self.stock_tree.delete(selected[0])
                # 刷新下拉框
                self.update_stock_combobox()
                # 刷新整个股票列表（关键修复）
                self.refresh_stock_list()

                messagebox.showinfo("成功", f"股票代码 {code} 已从数据库彻底删除\n删除了 {div_count} 条红利记录和 {trans_count} 条交易记录")
                print(f"[调试] 删除操作成功完成")
            else:
                messagebox.showerror("错误", f"删除失败: 股票代码 {code} 不存在于数据库中")
                print(f"[调试] 删除操作失败: 数据库中未找到股票代码 {code}")

        except Exception as e:
            self.conn.rollback()  # 回滚事务
            messagebox.showerror("错误", f"数据库删除失败: {str(e)}")
            print(f"[调试] 删除股票代码错误详情: {str(e)}")

    def refresh_stock_list(self):
        # 清空现有数据
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        # 从数据库获取最新数据
        try:
            self.cursor.execute("SELECT id, stock_code, stock_name FROM stock_codes")
            rows = self.cursor.fetchall()

            # 更新表格
            for row in rows:
                self.stock_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"刷新股票列表失败: {str(e)}")

    # 交易记录管理功能
    def browse_trans_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.trans_csv_path.delete(0, tk.END)
            self.trans_csv_path.insert(0, file_path)

    def import_transactions(self):
        file_path = self.trans_csv_path.get()
        if not file_path:
            messagebox.showerror("错误", "请选择CSV文件")
            return

        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            # 检测分隔符
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1024)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter

            # 读取CSV文件
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                messagebox.showinfo("导入结果", "CSV文件中没有数据")
                return

            # 查找列映射
            col_map = {
                "code": ["证券代码", "股票代码", "代码"],
                "name": ["证券名称", "股票名称", "名称"],
                "price": ["成交价格", "价格", "Price"],
                "quantity": ["成交数量", "数量", "Quantity"],
                "date": ["成交日期", "日期", "Date"],
                "commission": ["佣金", "手续费", "Commission"],
                "stamp_duty": ["印花税", "StampDuty"],
                "transfer_fee": ["过户费", "TransferFee"],
                "direction": ["委托类别", "方向", "Direction"],
                "amount": ["成交金额", "金额", "Amount"]
            }

            field_map = {}

            for col_name, aliases in col_map.items():
                for alias in aliases:
                    if alias in reader.fieldnames:
                        field_map[col_name] = alias
                        break
                else:
                    if col_name in ["code", "name", "price", "quantity", "date", "direction"]:
                        messagebox.showerror("错误", f"未找到必要的列: {col_name}")
                        return

            # 导入数据
            success = 0
            errors = []

            for i, row in enumerate(rows, start=1):
                try:
                    # 获取字段值
                    code = row[field_map["code"]].strip()
                    name = row[field_map["name"]].strip()
                    price = float(row[field_map["price"]])
                    quantity = int(row[field_map["quantity"]])
                    direction_str = row[field_map["direction"]].strip()
                    date_str = row[field_map["date"]].strip()

                    # 验证股票代码
                    if not code.isdigit() or len(code) > 6:
                        errors.append(f"行 {i}: 无效的股票代码 '{code}'")
                        continue

                    # 补全股票代码
                    code = code.zfill(6)

                    # 转换委托类别
                    direction_map = {
                        "买入": "买入",
                        "买": "买入",
                        "buy": "买入",
                        "b": "买入",
                        "卖出": "卖出",
                        "卖": "卖出",
                        "sell": "卖出",
                        "s": "卖出"
                    }

                    direction = direction_map.get(direction_str.lower())
                    if not direction:
                        errors.append(f"行 {i}: 无效的委托类别 '{direction_str}'")
                        continue

                    # 解析日期
                    try:
                        # 方法1: 使用dateutil.parser
                        try:
                            trade_date = parser.parse(date_str).strftime("%Y-%m-%d")
                        except:
                            # 方法2: 尝试常见格式
                            formats = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
                            for fmt in formats:
                                try:
                                    trade_date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                                    break
                                except:
                                    continue
                            else:
                                # 方法3: 提取数字组合
                                nums = re.findall(r'\d+', date_str)
                                if len(nums) >= 3:
                                    year = nums[0]
                                    month = nums[1].zfill(2)
                                    day = nums[2].zfill(2)
                                    trade_date = f"{year}-{month}-{day}"
                                else:
                                    raise ValueError("无法解析日期")
                    except Exception as e:
                        errors.append(f"行 {i}: 日期解析错误: {str(e)}")
                        continue

                    # 获取其他可选字段
                    commission = float(row.get(field_map.get("commission"), 0))
                    stamp_duty = float(row.get(field_map.get("stamp_duty"), 0))
                    transfer_fee = float(row.get(field_map.get("transfer_fee"), 0))
                    amount = float(row.get(field_map.get("amount"), price * quantity))

                    # 插入数据库
                    self.cursor.execute('''
                        INSERT INTO transactions (stock_code, stock_name, price, quantity, trade_date,
                                                  commission, stamp_duty, transfer_fee, direction,
                                                  amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (code, name, price, quantity, trade_date,
                              commission, stamp_duty, transfer_fee, direction, amount))
                    success += 1
                except Exception as e:
                    errors.append(f"行 {i}: {str(e)}")

            self.conn.commit()
            self.refresh_transaction_table()

            # 显示导入结果
            result_msg = f"成功导入 {success} 条记录"
            if errors:
                result_msg += f"\n失败 {len(errors)} 条记录:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    result_msg += f"\n...及其他 {len(errors) - 5} 条错误"

            messagebox.showinfo("导入结果", result_msg)

        except Exception as e:
            messagebox.showerror("导入错误", f"导入过程中发生错误: {str(e)}")

    def add_transaction(self):
        # 获取输入值
        code = self.trans_stock_code.get().strip()
        name = self.trans_stock_name.get().strip()
        direction = self.direction_var.get()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        commission = self.commission_entry.get().strip()
        stamp_duty = self.stamp_duty_entry.get().strip()
        transfer_fee = self.transfer_fee_entry.get().strip()
        trade_date = self.trans_date.get_date()

        # 验证输入
        if not code or not name:
            messagebox.showerror("错误", "股票代码和名称不能为空")
            return

        if not price or not quantity:
            messagebox.showerror("错误", "价格和数量不能为空")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            commission = float(commission) if commission else 0.0
            stamp_duty = float(stamp_duty) if stamp_duty else 0.0
            transfer_fee = float(transfer_fee) if transfer_fee else 0.0
            amount = price * quantity
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        # 验证股票代码
        if not code.isdigit() or len(code) > 6:
            messagebox.showerror("错误", "股票代码必须是6位数字")
            return

        # 补全股票代码
        code = code.zfill(6)

        try:
            # 插入交易记录
            self.cursor.execute('''
                                INSERT INTO transactions (stock_code, stock_name, price, quantity, trade_date,
                                                          commission, stamp_duty, transfer_fee, direction, amount)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (code, name, price, quantity, trade_date,
                                      commission, stamp_duty, transfer_fee, direction, amount))
            self.conn.commit()

            # 清空输入
            self.price_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.commission_entry.delete(0, tk.END)
            self.commission_entry.insert(0, "0.00")
            self.stamp_duty_entry.delete(0, tk.END)
            self.stamp_duty_entry.insert(0, "0.00")
            self.transfer_fee_entry.delete(0, tk.END)
            self.transfer_fee_entry.insert(0, "0.00")

            # 刷新表格
            self.refresh_transaction_table()
            messagebox.showinfo("成功", "交易记录添加成功")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def delete_transaction(self):
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要删除的记录")
            return

        item = self.trans_tree.item(selected[0])
        trans_id = item['values'][0]

        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            self.conn.commit()
            self.refresh_transaction_table()
            messagebox.showinfo("成功", "删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    def refresh_transaction_table(self):
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        self.cursor.execute("SELECT * FROM transactions ORDER BY trade_date DESC")
        rows = self.cursor.fetchall()

        for row in rows:
            self.trans_tree.insert("", "end", values=row)

    def on_stock_code_select(self, event):
        code = self.trans_stock_code.get()
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.trans_stock_name.set(name[0])

    def on_stock_code_enter(self, event):
        code = self.trans_stock_code.get().strip().zfill(6)
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.trans_stock_name.set(name[0])
        else:
            messagebox.showinfo("提示", "未找到该股票代码")

    def on_stock_name_select(self, event):
        name = self.trans_stock_name.get()
        self.cursor.execute("SELECT stock_code FROM stock_codes WHERE stock_name = ?", (name,))
        code = self.cursor.fetchone()
        if code:
            self.trans_stock_code.set(code[0])

    def on_stock_name_enter(self, event):
        name = self.trans_stock_name.get().strip()
        self.cursor.execute("SELECT stock_code FROM stock_codes WHERE stock_name = ?", (name,))
        code = self.cursor.fetchone()
        if code:
            self.trans_stock_code.set(code[0])
        else:
            messagebox.showinfo("提示", "未找到该股票名称")

    def on_position_stock_select(self, event):
        code = self.position_stock_code.get()
        self.query_position()

    def on_dividend_select(self, event):
        """当选择红利记录时触发"""
        selected = self.dividend_tree.selection()
        if selected:
            self.modify_btn.config(state=tk.NORMAL)
        else:
            self.modify_btn.config(state=tk.DISABLED)

    def on_div_stock_select(self, event):
        code = self.div_stock_code.get()
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.insert(0, name[0])
            self.div_stock_name.config(state='readonly')

    def on_div_stock_code_enter(self, event):
        code = self.div_stock_code.get().strip().zfill(6)
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.insert(0, name[0])
            self.div_stock_name.config(state='readonly')
        else:
            messagebox.showinfo("提示", "未找到该股票代码")
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.config(state='readonly')

    # 持仓管理功能
    def query_position(self):
        code = self.position_stock_code.get().strip()
        if not code:
            return

        # 清空表格
        for item in self.position_trans_tree.get_children():
            self.position_trans_tree.delete(item)

        # 查询股票名称
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        stock_name_result = self.cursor.fetchone()
        stock_name = stock_name_result[0] if stock_name_result else "未知"

        # 查询该股票的交易记录
        self.cursor.execute('''
                            SELECT id,
                                   stock_code,
                                   stock_name,
                                   price,
                                   quantity,
                                   trade_date,
                                   commission,
                                   stamp_duty,
                                   transfer_fee,
                                   direction,
                                   amount
                            FROM transactions
                            WHERE stock_code = ?
                            ORDER BY trade_date ASC
                            ''', (code,))
        transactions = self.cursor.fetchall()

        # 计算盈亏
        buy_records = []
        position = 0
        total_cost = 0.0

        for trans in transactions:
            trans_id, stock_code, stock_name, price, quantity, trade_date, commission, stamp_duty, transfer_fee, direction, amount = trans

            if direction == "买入":
                buy_records.append({
                    "id": trans_id,
                    "price": price,
                    "quantity": quantity,
                    "date": trade_date,
                    "cost": amount + commission + stamp_duty + transfer_fee
                })
                position += quantity
                total_cost += amount + commission + stamp_duty + transfer_fee
                profit = 0.0
            else:
                # 卖出操作
                sell_quantity = quantity
                sell_amount = amount - commission - stamp_duty - transfer_fee
                sell_profit = 0.0

                while sell_quantity > 0 and buy_records:
                    buy_record = buy_records[0]
                    if buy_record["quantity"] > sell_quantity:
                        # 部分卖出
                        cost_portion = buy_record["cost"] * (sell_quantity / buy_record["quantity"])
                        profit_portion = sell_amount * (sell_quantity / quantity) - cost_portion
                        sell_profit += profit_portion

                        # 更新买入记录
                        buy_record["quantity"] -= sell_quantity
                        buy_record["cost"] -= cost_portion
                        sell_quantity = 0
                    else:
                        # 全部卖出该批次
                        sell_quantity -= buy_record["quantity"]
                        profit_portion = sell_amount * (buy_record["quantity"] / quantity) - buy_record["cost"]
                        sell_profit += profit_portion
                        buy_records.pop(0)

                position -= quantity
                total_cost -= sell_amount
                profit = sell_profit

            # 添加到表格
            self.position_trans_tree.insert("", "end", values=(
                trans_id, stock_code, stock_name, price, quantity, trade_date,
                commission, stamp_duty, transfer_fee, direction, amount, f"{profit:.2f}"
            ))

        # 更新持仓汇总
        for item in self.position_tree.get_children():
            self.position_tree.delete(item)

        self.position_tree.insert("", "end", values=(code, stock_name, position))

    def show_all_positions(self):
        # 清空表格
        for item in self.position_trans_tree.get_children():
            self.position_trans_tree.delete(item)

        for item in self.position_tree.get_children():
            self.position_tree.delete(item)

        # 查询所有股票代码
        self.cursor.execute("SELECT DISTINCT stock_code FROM transactions")
        codes = [row[0] for row in self.cursor.fetchall()]

        # 计算每个股票的持仓
        for code in codes:
            self.cursor.execute('''
                                SELECT stock_name, direction, SUM(quantity)
                                FROM transactions
                                WHERE stock_code = ?
                                GROUP BY direction
                                ''', (code,))
            rows = self.cursor.fetchall()

            buy_qty = 0
            sell_qty = 0
            stock_name = ""

            for row in rows:
                stock_name = row[0]
                if row[1] == "买入":
                    buy_qty = row[2]
                elif row[1] == "卖出":
                    sell_qty = row[2]

            position = buy_qty - sell_qty
            if position > 0:
                self.position_tree.insert("", "end", values=(code, stock_name, position))

    def refresh_position_table(self):
        self.show_all_positions()

    # 红利管理功能
    def add_dividend(self):
        """添加红利记录"""
        code = self.div_stock_code.get().strip()
        name = self.div_stock_name.get().strip()
        dividend = self.dividend_entry.get().strip()
        div_date = self.div_date.get_date()

        # 验证输入
        if not code or not name:
            messagebox.showerror("错误", "股票代码和名称不能为空")
            return

        if not dividend:
            messagebox.showerror("错误", "红利金额不能为空")
            return

        try:
            dividend = float(dividend)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的红利金额")
            return

        # 补全股票代码
        code = code.zfill(6)

        # 如果名称为空，尝试从数据库获取
        if not name:
            self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
            name_result = self.cursor.fetchone()
            name = name_result[0] if name_result else "未知"

        try:
            # 插入红利记录
            self.cursor.execute("""
                                INSERT INTO dividends (stock_code, stock_name, dividend, dividend_date)
                                VALUES (?, ?, ?, ?)
                                """, (code, name, dividend, div_date))
            self.conn.commit()

            # 清空输入
            self.div_stock_code.set('')
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.config(state='readonly')
            self.dividend_entry.delete(0, tk.END)
            # 获取新添加记录的年份
            record_year = div_date.strftime("%Y")
            # 更新年份选择器
            self.update_year_combobox()

            # 设置为当前年份并刷新
            # self.year_combo.set(record_year)
            self.refresh_dividend_table()

            messagebox.showinfo("成功", f"红利记录添加成功 ({record_year}年)")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def save_record_change(self, rec_id, stock_code, amount, date, dialog, tree, year):
        """保存修改后的记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的红利金额")
            return

        try:
            # 更新数据库
            self.cursor.execute("""
                                UPDATE dividends
                                SET dividend      = ?,
                                    dividend_date = ?
                                WHERE id = ?
                                """, (amount, date, rec_id))
            self.conn.commit()

            # 更新树视图
            tree.item(rec_id, values=(date, f"{amount:.2f}", "修改/删除"))
            dialog.destroy()

            # 刷新主表格
            self.refresh_dividend_table()
            messagebox.showinfo("成功", "记录更新成功")
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {str(e)}")

    def delete_record(self, rec_id, dialog, tree, year):
        """删除单条记录"""
        if not messagebox.askyesno("确认", "确定要删除这条记录吗?"):
            return

        try:
            self.cursor.execute("DELETE FROM dividends WHERE id = ?", (rec_id,))
            self.conn.commit()
            tree.delete(rec_id)
            dialog.destroy()

            # 刷新主表格
            self.refresh_dividend_table()
            messagebox.showinfo("成功", "记录删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    # 以下代码为新代码
    def refresh_dividend_table(self, event=None):
        """刷新红利表格"""
        # 清空现有数据
        for item in self.dividend_tree.get_children():
            self.dividend_tree.delete(item)

        try:
            selected_year = self.year_combo.get()
            if not selected_year:
                return

            # 获取所有股票及其红利数据
            self.cursor.execute("""
                                SELECT d.stock_code,
                                       COALESCE(s.stock_name, d.stock_name) AS stock_name,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '01' THEN d.dividend
                                               ELSE 0 END)                  AS Jan,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '02' THEN d.dividend
                                               ELSE 0 END)                  AS Feb,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '03' THEN d.dividend
                                               ELSE 0 END)                  AS Mar,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '04' THEN d.dividend
                                               ELSE 0 END)                  AS Apr,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '05' THEN d.dividend
                                               ELSE 0 END)                  AS May,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '06' THEN d.dividend
                                               ELSE 0 END)                  AS Jun,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '07' THEN d.dividend
                                               ELSE 0 END)                  AS Jul,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '08' THEN d.dividend
                                               ELSE 0 END)                  AS Aug,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '09' THEN d.dividend
                                               ELSE 0 END)                  AS Sep,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '10' THEN d.dividend
                                               ELSE 0 END)                  AS Oct,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '11' THEN d.dividend
                                               ELSE 0 END)                  AS Nov,
                                       SUM(CASE WHEN strftime('%m', d.dividend_date) = '12' THEN d.dividend ELSE 0 END) AS Dec,
                    SUM(d.dividend) AS Total
                                FROM dividends d
                                    LEFT JOIN stock_codes s
                                ON d.stock_code = s.stock_code
                                WHERE strftime('%Y', d.dividend_date) = ?
                                GROUP BY d.stock_code
                                ORDER BY d.stock_code
                                """, (selected_year,))

            for row in self.cursor.fetchall():
                stock_code = row[0]
                stock_name = row[1]
                row_data = [selected_year, stock_code, stock_name]

                # 添加月份数据
                for month in range(2, 14):  # Jan 到 Dec
                    row_data.append(f"{row[month]:.2f}")

                # 添加总计
                row_data.append(f"{row[14]:.2f}")

                self.dividend_tree.insert("", "end", values=row_data)

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"查询失败: {str(e)}")

    def modify_dividend(self):
        """修改选中的红利记录 - 修复版本"""
        try:  # 添加 try 块
            selected = self.dividend_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要修改的记录")
                return

            item = self.dividend_tree.item(selected[0])
            values = item['values']

            # 确保有足够的列
            if len(values) < 3:
                messagebox.showerror("错误", "无效的记录格式")
                return

            # 获取股票代码、名称和年份
            year = values[0]  # 年份
            stock_code = str(values[1])  # 股票代码
            stock_name = values[2]  # 股票名称

            # 确保股票代码是6位格式
            stock_code = stock_code.zfill(6)

            # 创建编辑窗口
            edit_win = tk.Toplevel(self.root)
            edit_win.title(f"编辑红利记录 - {stock_code} {stock_name} ({year}年)")
            edit_win.geometry("800x600")
            edit_win.transient(self.root)
            edit_win.grab_set()

            # 主框架
            main_frame = ttk.Frame(edit_win)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 创建树形视图
            columns = ("id", "dividend_date", "dividend")
            self.dividend_detail_tree = ttk.Treeview(
                main_frame,
                columns=columns,
                show="headings",
                selectmode="browse"
            )

            # 配置列标题
            self.dividend_detail_tree.heading("id", text="ID")
            self.dividend_detail_tree.column("id", width=50, anchor=tk.CENTER)

            self.dividend_detail_tree.heading("dividend_date", text="分红日期")
            self.dividend_detail_tree.column("dividend_date", width=120, anchor=tk.CENTER)

            self.dividend_detail_tree.heading("dividend", text="分红金额")
            self.dividend_detail_tree.column("dividend", width=100, anchor=tk.CENTER)

            # 添加滚动条
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.dividend_detail_tree.yview)
            self.dividend_detail_tree.configure(yscrollcommand=scrollbar.set)

            # 布局
            self.dividend_detail_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # 按钮框架
            btn_frame = ttk.Frame(edit_win)
            btn_frame.pack(fill="x", padx=10, pady=5)

            # 编辑按钮
            edit_btn = ttk.Button(btn_frame, text="编辑选中记录",
                                  command=lambda: self.edit_dividend_detail(stock_code, stock_name, year))
            edit_btn.pack(side="left", padx=5)

            # 添加按钮
            add_btn = ttk.Button(btn_frame, text="添加新记录",
                                 command=lambda: self.add_dividend_detail(stock_code, stock_name, year))
            add_btn.pack(side="left", padx=5)

            # 删除按钮
            delete_btn = ttk.Button(btn_frame, text="删除选中记录",
                                    command=self.delete_dividend_detail)
            delete_btn.pack(side="left", padx=5)

            # 关闭按钮
            close_btn = ttk.Button(btn_frame, text="关闭", command=edit_win.destroy)
            close_btn.pack(side="right", padx=5)

            # 加载红利详情数据
            self.load_dividend_details(stock_code, stock_name, year)

            # 绑定选择事件
            self.dividend_detail_tree.bind("<<TreeviewSelect>>", lambda e: edit_btn.config(state=tk.NORMAL))

            # 初始禁用编辑按钮
            edit_btn.config(state=tk.DISABLED)

        except Exception as e:  # 添加 except 块
            messagebox.showerror("错误", f"打开编辑窗口失败: {str(e)}")
            traceback.print_exc()

    def load_dividend_details(self, stock_code=None, stock_name=None, year=None):
        """加载指定股票在指定年份的红利详情 - 增强调试版"""
        try:
            # 清空现有数据
            self.dividend_detail_tree.delete(*self.dividend_detail_tree.get_children())

            # 确保股票代码格式正确
            clean_code = stock_code[:6].zfill(6)  # 处理前缀/后缀

            # 查询指定年份的分红
            self.cursor.execute("""
                                SELECT id, dividend_date, dividend
                                FROM dividends
                                WHERE stock_code = ?
                                  AND substr(dividend_date, 1, 4) = ?
                                ORDER BY dividend_date
                                """, (clean_code, str(year)))

            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    date_str = row[1]
                    if len(date_str) > 10:  # 简化日期显示
                        date_str = date_str[:10]

                    self.dividend_detail_tree.insert("", "end", values=(
                        row[0],  # ID
                        date_str,  # 分红日期
                        f"{row[2]:.4f}"  # 分红金额
                    ))
            else:
                # 显示更详细的提示信息
                tip = f"没有找到 {stock_name}({clean_code}) 在 {year} 年的分红记录"
                self.dividend_detail_tree.insert("", "end", values=("", tip, ""))

        except sqlite3.Error as e:
            error_msg = f"数据库错误: {str(e)}"
            messagebox.showerror("数据库错误", error_msg)
            self.dividend_detail_tree.insert("", "end", values=("", "查询失败", ""))

    def edit_dividend_detail(self, stock_code, stock_name, year):
        """编辑选中的红利详情记录 - 修复版本"""
        try:
            selected = self.dividend_detail_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要编辑的记录")
                return

            item = self.dividend_detail_tree.item(selected[0])
            values = item['values']

            # 检查是否是提示行
            if not values[0]:  # 如果没有ID
                messagebox.showinfo("提示", "请选择有效的分红记录")
                return

            dividend_id = values[0]
            current_date = values[1]
            current_amount = values[2].replace('&#165;', '').replace(',', '')  # 清理金额格式

            # 创建编辑对话框
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title(f"编辑分红记录 - {stock_code} {stock_name}")
            edit_dialog.geometry("300x200")
            edit_dialog.transient(self.root)
            edit_dialog.grab_set()

            # 框架
            content_frame = ttk.Frame(edit_dialog)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 股票信息
            ttk.Label(content_frame, text=f"股票: {stock_code} {stock_name}").grid(row=0, column=0, columnspan=2,
                                                                                 sticky=tk.W)
            ttk.Label(content_frame, text=f"年份: {year}").grid(row=1, column=0, columnspan=2, sticky=tk.W)

            # 日期
            ttk.Label(content_frame, text="分红日期:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            date_entry = DateEntry(content_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.set_date(current_date)
            date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            # 金额
            ttk.Label(content_frame, text="分红金额:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            amount_var = tk.StringVar(value=current_amount)
            amount_entry = ttk.Entry(content_frame, textvariable=amount_var)
            amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # 按钮框架
            btn_frame = ttk.Frame(content_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            # 保存按钮
            save_btn = ttk.Button(btn_frame, text="保存",
                                  command=lambda: self.save_dividend_detail(dividend_id, amount_var.get(),
                                                                            date_entry.get_date(), stock_code, year,
                                                                            edit_dialog))
            save_btn.pack(side="left", padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(btn_frame, text="取消", command=edit_dialog.destroy)
            cancel_btn.pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"编辑分红详情失败: {str(e)}")
            traceback.print_exc()

    def add_dividend_detail(self, stock_code, stock_name, year):
        """添加新的红利详情记录 - 修复版本"""
        try:
            # 创建添加对话框
            add_dialog = tk.Toplevel(self.root)
            add_dialog.title(f"添加分红记录 - {stock_code} {stock_name}")
            add_dialog.geometry("300x200")
            add_dialog.transient(self.root)
            add_dialog.grab_set()

            # 框架
            content_frame = ttk.Frame(add_dialog)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 股票信息
            ttk.Label(content_frame, text=f"股票: {stock_code} {stock_name}").grid(row=0, column=0, columnspan=2,
                                                                                 sticky=tk.W)
            ttk.Label(content_frame, text=f"年份: {year}").grid(row=1, column=0, columnspan=2, sticky=tk.W)

            # 日期
            ttk.Label(content_frame, text="分红日期:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            date_entry = DateEntry(content_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            # 金额
            ttk.Label(content_frame, text="分红金额:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            amount_var = tk.StringVar()
            amount_entry = ttk.Entry(content_frame, textvariable=amount_var)
            amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # 按钮框架
            btn_frame = ttk.Frame(content_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            # 添加按钮
            add_btn = ttk.Button(btn_frame, text="添加",
                                 command=lambda: self.save_new_dividend_detail(
                                     stock_code, stock_name, amount_var.get(), date_entry.get_date(),
                                     year, add_dialog))
            add_btn.pack(side="left", padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(btn_frame, text="取消", command=add_dialog.destroy)
            cancel_btn.pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"添加分红详情失败: {str(e)}")
            traceback.print_exc()

    def delete_dividend_detail(self, stock_code=None, year=None):
        """删除选中的红利详情记录 - 修复版本"""
        try:

            # 初始化变量
            dividend_id = None
            stock_code = ""
            year = ""

            # 检查是否有选中的记录
            selected = self.dividend_detail_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要删除的记录")
                return

            item = self.dividend_detail_tree.item(selected[0])
            values = item['values']

            # 检查是否是有效记录（有ID值）
            if values and len(values) > 0 and values[0]:
                dividend_id = values[0]
            else:
                messagebox.showinfo("提示", "请选择有效的分红记录")
                return

            # 确认删除
            if messagebox.askyesno("确认", "确定要删除这条分红记录吗？"):
                try:
                    # 从数据库删除
                    self.cursor.execute("DELETE FROM dividends WHERE id = ?", (dividend_id,))
                    self.conn.commit()

                    # 从树形视图删除
                    self.dividend_detail_tree.delete(selected[0])

                    # 刷新主界面的红利汇总表格
                    self.refresh_dividend_table()

                    # 重新加载详情数据
                    if stock_code and year:
                        # 获取股票名称
                        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (stock_code,))
                        name_result = self.cursor.fetchone()
                        stock_name = name_result[0] if name_result else ""

                        self.load_dividend_details(stock_code, stock_name, year)

                    messagebox.showinfo("成功", "分红记录已删除")
                except sqlite3.Error as e:
                    messagebox.showerror("数据库错误", f"删除失败: {str(e)}")
                    traceback.print_exc()

        except Exception as e:
            messagebox.showerror("错误", f"删除分红详情失败: {str(e)}")
            traceback.print_exc()

    def save_dividend_detail(self, dividend_id, amount, date, stock_code, year, dialog):
        """保存编辑的分红详情记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的分红金额")
            return

        try:
            # 更新数据库
            self.cursor.execute("""
                                UPDATE dividends
                                SET dividend      = ?,
                                    dividend_date = ?
                                WHERE id = ?
                                """, (amount, date, dividend_id))
            self.conn.commit()

            # 刷新详情列表
            self.load_dividend_details(stock_code, year)

            # 刷新主界面的红利汇总表格
            self.refresh_dividend_table()

            dialog.destroy()
            messagebox.showinfo("成功", "分红记录更新成功")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"更新失败: {str(e)}")

    def save_new_dividend_detail(self, stock_code, stock_name, amount, date, year, dialog):
        """保存新的分红详情记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的分红金额")
            return

        try:
            # 插入新记录
            self.cursor.execute("""
                                INSERT INTO dividends (stock_code, stock_name, dividend, dividend_date)
                                VALUES (?, ?, ?, ?)
                                """, (stock_code, stock_name, amount, date))
            self.conn.commit()

            # 刷新详情列表
            self.load_dividend_details(stock_code, year)

            # 刷新主界面的红利汇总表格
            self.refresh_dividend_table()

            dialog.destroy()
            messagebox.showinfo("成功", "新分红记录添加成功")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"添加失败: {str(e)}")

    # 股票代码下拉框相关功能

    def update_stock_combobox(self):
        """更新股票代码下拉框"""
        try:
            self.cursor.execute("SELECT stock_code FROM stock_codes")
            codes = [row[0] for row in self.cursor.fetchall()]

            # 更新交易记录标签页的股票代码下拉框
            self.trans_stock_code['values'] = codes

            # 更新持仓查询标签页的股票代码下拉框
            self.position_stock_code['values'] = codes

            # 更新红利标签页的股票代码下拉框
            self.div_stock_code['values'] = codes

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取股票代码失败: {str(e)}")

    def update_year_combobox(self):
        """更新年份选择器选项"""
        try:
            self.cursor.execute(
                "SELECT DISTINCT strftime('%Y', dividend_date) AS year FROM dividends ORDER BY year DESC")
            years = [row[0] for row in self.cursor.fetchall()]
            self.year_combo['values'] = years

            # 设置默认选择
            if years:
                self.year_combo.set(years[0])
            else:
                self.year_combo.set('')
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取年份失败: {str(e)}")

    # 盈亏计算方法
    def calculate_daily_profit(self, date):
        """计算指定日期的盈亏"""
        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date = ?)
                            ''', (date,))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE dividend_date = ?
                            ''', (date,))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    def calculate_monthly_profit(self, year, month):
        """计算指定月份的盈亏"""
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(int(year), int(month))[1]
        end_date = f"{year}-{month:02d}-{last_day}"

        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date BETWEEN ? AND ?)
                            ''', (start_date, end_date))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE strftime('%Y-%m', dividend_date) = ?
                            ''', (f"{year}-{month:02d}",))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    def calculate_yearly_profit(self, year):
        """计算指定年份的盈亏"""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date BETWEEN ? AND ?)
                            ''', (start_date, end_date))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE strftime('%Y', dividend_date) = ?
                            ''', (year,))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    # 资产管理功能
    def query_daily_profit(self):
        """查询日盈亏"""
        try:
            date = self.asset_date.get_date()
            profit = self.calculate_daily_profit(date)
            messagebox.showinfo("日盈亏统计", f"{date} 日盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询日盈亏失败: {str(e)}")

    def query_monthly_profit(self):
        """查询月盈亏"""
        try:
            date = self.asset_date.get_date()
            date_str = str(date)
            year, month, _ = date_str.split('-')
            profit = self.calculate_monthly_profit(year, int(month))
            messagebox.showinfo("月盈亏统计", f"{year}年{month}月盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询月盈亏失败: {str(e)}")

    def query_yearly_profit(self):
        """查询年盈亏"""
        try:
            date = self.asset_date.get_date()
            date_str = str(date)
            year = date_str.split('-')[0]
            profit = self.calculate_yearly_profit(year)
            messagebox.showinfo("年盈亏统计", f"{year}年盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询年盈亏失败: {str(e)}")

    def add_cash_flow(self, flow_type):
        """添加资金流水记录"""
        try:
            amount = simpledialog.askfloat("添加记录", f"请输入{flow_type}金额:")
            if amount is None:
                return

            flow_date = self.asset_date.get_date()

            self.cursor.execute('''
                                INSERT INTO cash_flow (amount, flow_date, type)
                                VALUES (?, ?, ?)
                                ''', (amount, flow_date, flow_type))
            self.conn.commit()
            self.refresh_cash_flow_table()
            self.refresh_asset_table()
            messagebox.showinfo("成功", f"{flow_type}记录添加成功")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def delete_cash_flow(self):
        """删除资金流水记录"""
        try:
            selected = self.cash_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要删除的记录")
                return

            item = self.cash_tree.item(selected[0])
            flow_id = item['values'][0]

            self.cursor.execute("DELETE FROM cash_flow WHERE id = ?", (flow_id,))
            self.conn.commit()
            self.refresh_cash_flow_table()
            self.refresh_asset_table()
            messagebox.showinfo("成功", "删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    def refresh_cash_flow_table(self):
        """刷新资金流水表格"""
        # 清空表格
        for item in self.cash_tree.get_children():
            self.cash_tree.delete(item)

        # 查询并填充数据
        self.cursor.execute("SELECT id, amount, flow_date, type FROM cash_flow ORDER BY flow_date DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            self.stock_tree.insert("", "end", values=row)

    # 交易记录管理功能
    def browse_trans_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.trans_csv_path.delete(0, tk.END)
            self.trans_csv_path.insert(0, file_path)

    def import_transactions(self):
        file_path = self.trans_csv_path.get()
        if not file_path:
            messagebox.showerror("错误", "请选择CSV文件")
            return

        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            # 检测分隔符
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1024)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter

            # 读取CSV文件
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                messagebox.showinfo("导入结果", "CSV文件中没有数据")
                return

            # 查找列映射
            col_map = {
                "code": ["证券代码", "股票代码", "代码"],
                "name": ["证券名称", "股票名称", "名称"],
                "price": ["成交价格", "价格", "Price"],
                "quantity": ["成交数量", "数量", "Quantity"],
                "date": ["成交日期", "日期", "Date"],
                "commission": ["佣金", "手续费", "Commission"],
                "stamp_duty": ["印花税", "StampDuty"],
                "transfer_fee": ["过户费", "TransferFee"],
                "direction": ["委托类别", "方向", "Direction"],
                "amount": ["成交金额", "金额", "Amount"]
            }

            field_map = {}

            for col_name, aliases in col_map.items():
                for alias in aliases:
                    if alias in reader.fieldnames:
                        field_map[col_name] = alias
                        break
                else:
                    if col_name in ["code", "name", "price", "quantity", "date", "direction"]:
                        messagebox.showerror("错误", f"未找到必要的列: {col_name}")
                        return

            # 导入数据
            success = 0
            errors = []

            for i, row in enumerate(rows, start=1):
                try:
                    # 获取字段值
                    code = row[field_map["code"]].strip()
                    name = row[field_map["name"]].strip()
                    price = float(row[field_map["price"]])
                    quantity = int(row[field_map["quantity"]])
                    direction_str = row[field_map["direction"]].strip()
                    date_str = row[field_map["date"]].strip()

                    # 验证股票代码
                    if not code.isdigit() or len(code) > 6:
                        errors.append(f"行 {i}: 无效的股票代码 '{code}'")
                        continue

                    # 补全股票代码
                    code = code.zfill(6)

                    # 转换委托类别
                    direction_map = {
                        "买入": "买入",
                        "买": "买入",
                        "buy": "买入",
                        "b": "买入",
                        "卖出": "卖出",
                        "卖": "卖出",
                        "sell": "卖出",
                        "s": "卖出"
                    }

                    direction = direction_map.get(direction_str.lower())
                    if not direction:
                        errors.append(f"行 {i}: 无效的委托类别 '{direction_str}'")
                        continue

                    # 解析日期
                    try:
                        # 方法1: 使用dateutil.parser
                        try:
                            trade_date = parser.parse(date_str).strftime("%Y-%m-%d")
                        except:
                            # 方法2: 尝试常见格式
                            formats = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]
                            for fmt in formats:
                                try:
                                    trade_date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                                    break
                                except:
                                    continue
                            else:
                                # 方法3: 提取数字组合
                                nums = re.findall(r'\d+', date_str)
                                if len(nums) >= 3:
                                    year = nums[0]
                                    month = nums[1].zfill(2)
                                    day = nums[2].zfill(2)
                                    trade_date = f"{year}-{month}-{day}"
                                else:
                                    raise ValueError("无法解析日期")
                    except Exception as e:
                        errors.append(f"行 {i}: 日期解析错误: {str(e)}")
                        continue

                    # 获取其他可选字段
                    commission = float(row.get(field_map.get("commission"), 0))
                    stamp_duty = float(row.get(field_map.get("stamp_duty"), 0))
                    transfer_fee = float(row.get(field_map.get("transfer_fee"), 0))
                    amount = float(row.get(field_map.get("amount"), price * quantity))

                    # 插入数据库
                    self.cursor.execute('''
                        INSERT INTO transactions (stock_code, stock_name, price, quantity, trade_date,
                                                  commission, stamp_duty, transfer_fee, direction,
                                                  amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (code, name, price, quantity, trade_date,
                              commission, stamp_duty, transfer_fee, direction, amount))
                    success += 1
                except Exception as e:
                    errors.append(f"行 {i}: {str(e)}")

            self.conn.commit()
            self.refresh_transaction_table()

            # 显示导入结果
            result_msg = f"成功导入 {success} 条记录"
            if errors:
                result_msg += f"\n失败 {len(errors)} 条记录:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    result_msg += f"\n...及其他 {len(errors) - 5} 条错误"

            messagebox.showinfo("导入结果", result_msg)

        except Exception as e:
            messagebox.showerror("导入错误", f"导入过程中发生错误: {str(e)}")

    def add_transaction(self):
        # 获取输入值
        code = self.trans_stock_code.get().strip()
        name = self.trans_stock_name.get().strip()
        direction = self.direction_var.get()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        commission = self.commission_entry.get().strip()
        stamp_duty = self.stamp_duty_entry.get().strip()
        transfer_fee = self.transfer_fee_entry.get().strip()
        trade_date = self.trans_date.get_date()

        # 验证输入
        if not code or not name:
            messagebox.showerror("错误", "股票代码和名称不能为空")
            return

        if not price or not quantity:
            messagebox.showerror("错误", "价格和数量不能为空")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            commission = float(commission) if commission else 0.0
            stamp_duty = float(stamp_duty) if stamp_duty else 0.0
            transfer_fee = float(transfer_fee) if transfer_fee else 0.0
            amount = price * quantity
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        # 验证股票代码
        if not code.isdigit() or len(code) > 6:
            messagebox.showerror("错误", "股票代码必须是6位数字")
            return

        # 补全股票代码
        code = code.zfill(6)

        try:
            # 插入交易记录
            self.cursor.execute('''
                                INSERT INTO transactions (stock_code, stock_name, price, quantity, trade_date,
                                                          commission, stamp_duty, transfer_fee, direction, amount)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (code, name, price, quantity, trade_date,
                                      commission, stamp_duty, transfer_fee, direction, amount))
            self.conn.commit()

            # 清空输入
            self.price_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.commission_entry.delete(0, tk.END)
            self.commission_entry.insert(0, "0.00")
            self.stamp_duty_entry.delete(0, tk.END)
            self.stamp_duty_entry.insert(0, "0.00")
            self.transfer_fee_entry.delete(0, tk.END)
            self.transfer_fee_entry.insert(0, "0.00")

            # 刷新表格
            self.refresh_transaction_table()
            messagebox.showinfo("成功", "交易记录添加成功")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def delete_transaction(self):
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要删除的记录")
            return

        item = self.trans_tree.item(selected[0])
        trans_id = item['values'][0]

        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            self.conn.commit()
            self.refresh_transaction_table()
            messagebox.showinfo("成功", "删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    def refresh_transaction_table(self):
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        self.cursor.execute("SELECT * FROM transactions ORDER BY trade_date DESC")
        rows = self.cursor.fetchall()

        for row in rows:
            self.trans_tree.insert("", "end", values=row)

    def on_stock_code_select(self, event):
        code = self.trans_stock_code.get()
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.trans_stock_name.set(name[0])

    def on_stock_code_enter(self, event):
        code = self.trans_stock_code.get().strip().zfill(6)
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.trans_stock_name.set(name[0])
        else:
            messagebox.showinfo("提示", "未找到该股票代码")

    def on_stock_name_select(self, event):
        name = self.trans_stock_name.get()
        self.cursor.execute("SELECT stock_code FROM stock_codes WHERE stock_name = ?", (name,))
        code = self.cursor.fetchone()
        if code:
            self.trans_stock_code.set(code[0])

    def on_stock_name_enter(self, event):
        name = self.trans_stock_name.get().strip()
        self.cursor.execute("SELECT stock_code FROM stock_codes WHERE stock_name = ?", (name,))
        code = self.cursor.fetchone()
        if code:
            self.trans_stock_code.set(code[0])
        else:
            messagebox.showinfo("提示", "未找到该股票名称")

    def on_position_stock_select(self, event):
        code = self.position_stock_code.get()
        self.query_position()

    def on_dividend_select(self, event):
        """当选择红利记录时触发"""
        selected = self.dividend_tree.selection()
        if selected:
            self.modify_btn.config(state=tk.NORMAL)
        else:
            self.modify_btn.config(state=tk.DISABLED)

    def on_div_stock_select(self, event):
        code = self.div_stock_code.get()
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.insert(0, name[0])
            self.div_stock_name.config(state='readonly')

    def on_div_stock_code_enter(self, event):
        code = self.div_stock_code.get().strip().zfill(6)
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        name = self.cursor.fetchone()
        if name:
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.insert(0, name[0])
            self.div_stock_name.config(state='readonly')
        else:
            messagebox.showinfo("提示", "未找到该股票代码")
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.config(state='readonly')

    # 持仓管理功能
    def query_position(self):
        code = self.position_stock_code.get().strip()
        if not code:
            return

        # 清空表格
        for item in self.position_trans_tree.get_children():
            self.position_trans_tree.delete(item)

        # 查询股票名称
        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
        stock_name_result = self.cursor.fetchone()
        stock_name = stock_name_result[0] if stock_name_result else "未知"

        # 查询该股票的交易记录
        self.cursor.execute('''
                            SELECT id,
                                   stock_code,
                                   stock_name,
                                   price,
                                   quantity,
                                   trade_date,
                                   commission,
                                   stamp_duty,
                                   transfer_fee,
                                   direction,
                                   amount
                            FROM transactions
                            WHERE stock_code = ?
                            ORDER BY trade_date ASC
                            ''', (code,))
        transactions = self.cursor.fetchall()

        # 计算盈亏
        buy_records = []
        position = 0
        total_cost = 0.0

        for trans in transactions:
            trans_id, stock_code, stock_name, price, quantity, trade_date, commission, stamp_duty, transfer_fee, direction, amount = trans

            if direction == "买入":
                buy_records.append({
                    "id": trans_id,
                    "price": price,
                    "quantity": quantity,
                    "date": trade_date,
                    "cost": amount + commission + stamp_duty + transfer_fee
                })
                position += quantity
                total_cost += amount + commission + stamp_duty + transfer_fee
                profit = 0.0
            else:
                # 卖出操作
                sell_quantity = quantity
                sell_amount = amount - commission - stamp_duty - transfer_fee
                sell_profit = 0.0

                while sell_quantity > 0 and buy_records:
                    buy_record = buy_records[0]
                    if buy_record["quantity"] > sell_quantity:
                        # 部分卖出
                        cost_portion = buy_record["cost"] * (sell_quantity / buy_record["quantity"])
                        profit_portion = sell_amount * (sell_quantity / quantity) - cost_portion
                        sell_profit += profit_portion

                        # 更新买入记录
                        buy_record["quantity"] -= sell_quantity
                        buy_record["cost"] -= cost_portion
                        sell_quantity = 0
                    else:
                        # 全部卖出该批次
                        sell_quantity -= buy_record["quantity"]
                        profit_portion = sell_amount * (buy_record["quantity"] / quantity) - buy_record["cost"]
                        sell_profit += profit_portion
                        buy_records.pop(0)

                position -= quantity
                total_cost -= sell_amount
                profit = sell_profit

            # 添加到表格
            self.position_trans_tree.insert("", "end", values=(
                trans_id, stock_code, stock_name, price, quantity, trade_date,
                commission, stamp_duty, transfer_fee, direction, amount, f"{profit:.2f}"
            ))

        # 更新持仓汇总
        for item in self.position_tree.get_children():
            self.position_tree.delete(item)

        self.position_tree.insert("", "end", values=(code, stock_name, position))

    def show_all_positions(self):
        # 清空表格
        for item in self.position_trans_tree.get_children():
            self.position_trans_tree.delete(item)

        for item in self.position_tree.get_children():
            self.position_tree.delete(item)

        # 查询所有股票代码
        self.cursor.execute("SELECT DISTINCT stock_code FROM transactions")
        codes = [row[0] for row in self.cursor.fetchall()]

        # 计算每个股票的持仓
        for code in codes:
            self.cursor.execute('''
                                SELECT stock_name, direction, SUM(quantity)
                                FROM transactions
                                WHERE stock_code = ?
                                GROUP BY direction
                                ''', (code,))
            rows = self.cursor.fetchall()

            buy_qty = 0
            sell_qty = 0
            stock_name = ""

            for row in rows:
                stock_name = row[0]
                if row[1] == "买入":
                    buy_qty = row[2]
                elif row[1] == "卖出":
                    sell_qty = row[2]

            position = buy_qty - sell_qty
            if position > 0:
                self.position_tree.insert("", "end", values=(code, stock_name, position))

    def refresh_position_table(self):
        self.show_all_positions()

    # 红利管理功能
    def add_dividend(self):
        """添加红利记录"""
        code = self.div_stock_code.get().strip()
        name = self.div_stock_name.get().strip()
        dividend = self.dividend_entry.get().strip()
        div_date = self.div_date.get_date()

        # 验证输入
        if not code or not name:
            messagebox.showerror("错误", "股票代码和名称不能为空")
            return

        if not dividend:
            messagebox.showerror("错误", "红利金额不能为空")
            return

        try:
            dividend = float(dividend)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的红利金额")
            return

        # 补全股票代码
        code = code.zfill(6)

        # 如果名称为空，尝试从数据库获取
        if not name:
            self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (code,))
            name_result = self.cursor.fetchone()
            name = name_result[0] if name_result else "未知"

        try:
            # 插入红利记录
            self.cursor.execute("""
                                INSERT INTO dividends (stock_code, stock_name, dividend, dividend_date)
                                VALUES (?, ?, ?, ?)
                                """, (code, name, dividend, div_date))
            self.conn.commit()

            # 清空输入
            self.div_stock_code.set('')
            self.div_stock_name.config(state='normal')
            self.div_stock_name.delete(0, tk.END)
            self.div_stock_name.config(state='readonly')
            self.dividend_entry.delete(0, tk.END)
            # 获取新添加记录的年份
            record_year = div_date.strftime("%Y")
            # 更新年份选择器
            self.update_year_combobox()

            # 设置为当前年份并刷新
            # self.year_combo.set(record_year)
            self.refresh_dividend_table()

            messagebox.showinfo("成功", f"红利记录添加成功 ({record_year}年)")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def save_record_change(self, rec_id, stock_code, amount, date, dialog, tree, year):
        """保存修改后的记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的红利金额")
            return

        try:
            # 更新数据库
            self.cursor.execute("""
                                UPDATE dividends
                                SET dividend      = ?,
                                    dividend_date = ?
                                WHERE id = ?
                                """, (amount, date, rec_id))
            self.conn.commit()

            # 更新树视图
            tree.item(rec_id, values=(date, f"{amount:.2f}", "修改/删除"))
            dialog.destroy()

            # 刷新主表格
            self.refresh_dividend_table()
            messagebox.showinfo("成功", "记录更新成功")
        except Exception as e:
            messagebox.showerror("错误", f"更新失败: {str(e)}")

    def delete_record(self, rec_id, dialog, tree, year):
        """删除单条记录"""
        if not messagebox.askyesno("确认", "确定要删除这条记录吗?"):
            return

        try:
            self.cursor.execute("DELETE FROM dividends WHERE id = ?", (rec_id,))
            self.conn.commit()
            tree.delete(rec_id)
            dialog.destroy()

            # 刷新主表格
            self.refresh_dividend_table()
            messagebox.showinfo("成功", "记录删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    # 以下代码为新代码
    def refresh_dividend_table(self, event=None):
        """刷新红利表格"""
        # 清空现有数据
        for item in self.dividend_tree.get_children():
            self.dividend_tree.delete(item)

        try:
            selected_year = self.year_combo.get()
            if not selected_year:
                return

            # 获取所有股票及其红利数据
            self.cursor.execute("""
                                SELECT d.stock_code,
                                       COALESCE(s.stock_name, d.stock_name) AS stock_name,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '01' THEN d.dividend
                                               ELSE 0 END)                  AS Jan,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '02' THEN d.dividend
                                               ELSE 0 END)                  AS Feb,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '03' THEN d.dividend
                                               ELSE 0 END)                  AS Mar,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '04' THEN d.dividend
                                               ELSE 0 END)                  AS Apr,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '05' THEN d.dividend
                                               ELSE 0 END)                  AS May,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '06' THEN d.dividend
                                               ELSE 0 END)                  AS Jun,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '07' THEN d.dividend
                                               ELSE 0 END)                  AS Jul,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '08' THEN d.dividend
                                               ELSE 0 END)                  AS Aug,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '09' THEN d.dividend
                                               ELSE 0 END)                  AS Sep,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '10' THEN d.dividend
                                               ELSE 0 END)                  AS Oct,
                                       SUM(CASE
                                               WHEN strftime('%m', d.dividend_date) = '11' THEN d.dividend
                                               ELSE 0 END)                  AS Nov,
                                       SUM(CASE WHEN strftime('%m', d.dividend_date) = '12' THEN d.dividend ELSE 0 END) AS Dec,
                    SUM(d.dividend) AS Total
                                FROM dividends d
                                    LEFT JOIN stock_codes s
                                ON d.stock_code = s.stock_code
                                WHERE strftime('%Y', d.dividend_date) = ?
                                GROUP BY d.stock_code
                                ORDER BY d.stock_code
                                """, (selected_year,))

            for row in self.cursor.fetchall():
                stock_code = row[0]
                stock_name = row[1]
                row_data = [selected_year, stock_code, stock_name]

                # 添加月份数据
                for month in range(2, 14):  # Jan 到 Dec
                    row_data.append(f"{row[month]:.2f}")

                # 添加总计
                row_data.append(f"{row[14]:.2f}")

                self.dividend_tree.insert("", "end", values=row_data)

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"查询失败: {str(e)}")

    def modify_dividend(self):
        """修改选中的红利记录 - 修复版本"""
        try:  # 添加 try 块
            selected = self.dividend_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要修改的记录")
                return

            item = self.dividend_tree.item(selected[0])
            values = item['values']

            # 确保有足够的列
            if len(values) < 3:
                messagebox.showerror("错误", "无效的记录格式")
                return

            # 获取股票代码、名称和年份
            year = values[0]  # 年份
            stock_code = str(values[1])  # 股票代码
            stock_name = values[2]  # 股票名称

            # 确保股票代码是6位格式
            stock_code = stock_code.zfill(6)

            # 创建编辑窗口
            edit_win = tk.Toplevel(self.root)
            edit_win.title(f"编辑红利记录 - {stock_code} {stock_name} ({year}年)")
            edit_win.geometry("800x600")
            edit_win.transient(self.root)
            edit_win.grab_set()

            # 主框架
            main_frame = ttk.Frame(edit_win)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 创建树形视图
            columns = ("id", "dividend_date", "dividend")
            self.dividend_detail_tree = ttk.Treeview(
                main_frame,
                columns=columns,
                show="headings",
                selectmode="browse"
            )

            # 配置列标题
            self.dividend_detail_tree.heading("id", text="ID")
            self.dividend_detail_tree.column("id", width=50, anchor=tk.CENTER)

            self.dividend_detail_tree.heading("dividend_date", text="分红日期")
            self.dividend_detail_tree.column("dividend_date", width=120, anchor=tk.CENTER)

            self.dividend_detail_tree.heading("dividend", text="分红金额")
            self.dividend_detail_tree.column("dividend", width=100, anchor=tk.CENTER)

            # 添加滚动条
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.dividend_detail_tree.yview)
            self.dividend_detail_tree.configure(yscrollcommand=scrollbar.set)

            # 布局
            self.dividend_detail_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # 按钮框架
            btn_frame = ttk.Frame(edit_win)
            btn_frame.pack(fill="x", padx=10, pady=5)

            # 编辑按钮
            edit_btn = ttk.Button(btn_frame, text="编辑选中记录",
                                  command=lambda: self.edit_dividend_detail(stock_code, stock_name, year))
            edit_btn.pack(side="left", padx=5)

            # 添加按钮
            add_btn = ttk.Button(btn_frame, text="添加新记录",
                                 command=lambda: self.add_dividend_detail(stock_code, stock_name, year))
            add_btn.pack(side="left", padx=5)

            # 删除按钮
            delete_btn = ttk.Button(btn_frame, text="删除选中记录",
                                    command=self.delete_dividend_detail)
            delete_btn.pack(side="left", padx=5)

            # 关闭按钮
            close_btn = ttk.Button(btn_frame, text="关闭", command=edit_win.destroy)
            close_btn.pack(side="right", padx=5)

            # 加载红利详情数据
            self.load_dividend_details(stock_code, stock_name, year)

            # 绑定选择事件
            self.dividend_detail_tree.bind("<<TreeviewSelect>>", lambda e: edit_btn.config(state=tk.NORMAL))

            # 初始禁用编辑按钮
            edit_btn.config(state=tk.DISABLED)

        except Exception as e:  # 添加 except 块
            messagebox.showerror("错误", f"打开编辑窗口失败: {str(e)}")
            traceback.print_exc()

    def load_dividend_details(self, stock_code=None, stock_name=None, year=None):
        """加载指定股票在指定年份的红利详情 - 增强调试版"""
        try:
            # 清空现有数据
            self.dividend_detail_tree.delete(*self.dividend_detail_tree.get_children())

            # 确保股票代码格式正确
            clean_code = stock_code[:6].zfill(6)  # 处理前缀/后缀

            # 查询指定年份的分红
            self.cursor.execute("""
                                SELECT id, dividend_date, dividend
                                FROM dividends
                                WHERE stock_code = ?
                                  AND substr(dividend_date, 1, 4) = ?
                                ORDER BY dividend_date
                                """, (clean_code, str(year)))

            rows = self.cursor.fetchall()

            if rows:
                for row in rows:
                    date_str = row[1]
                    if len(date_str) > 10:  # 简化日期显示
                        date_str = date_str[:10]

                    self.dividend_detail_tree.insert("", "end", values=(
                        row[0],  # ID
                        date_str,  # 分红日期
                        f"{row[2]:.4f}"  # 分红金额
                    ))
            else:
                # 显示更详细的提示信息
                tip = f"没有找到 {stock_name}({clean_code}) 在 {year} 年的分红记录"
                self.dividend_detail_tree.insert("", "end", values=("", tip, ""))

        except sqlite3.Error as e:
            error_msg = f"数据库错误: {str(e)}"
            messagebox.showerror("数据库错误", error_msg)
            self.dividend_detail_tree.insert("", "end", values=("", "查询失败", ""))

    def edit_dividend_detail(self, stock_code, stock_name, year):
        """编辑选中的红利详情记录 - 修复版本"""
        try:
            selected = self.dividend_detail_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要编辑的记录")
                return

            item = self.dividend_detail_tree.item(selected[0])
            values = item['values']

            # 检查是否是提示行
            if not values[0]:  # 如果没有ID
                messagebox.showinfo("提示", "请选择有效的分红记录")
                return

            dividend_id = values[0]
            current_date = values[1]
            current_amount = values[2].replace('&#165;', '').replace(',', '')  # 清理金额格式

            # 创建编辑对话框
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title(f"编辑分红记录 - {stock_code} {stock_name}")
            edit_dialog.geometry("300x200")
            edit_dialog.transient(self.root)
            edit_dialog.grab_set()

            # 框架
            content_frame = ttk.Frame(edit_dialog)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 股票信息
            ttk.Label(content_frame, text=f"股票: {stock_code} {stock_name}").grid(row=0, column=0, columnspan=2,
                                                                                 sticky=tk.W)
            ttk.Label(content_frame, text=f"年份: {year}").grid(row=1, column=0, columnspan=2, sticky=tk.W)

            # 日期
            ttk.Label(content_frame, text="分红日期:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            date_entry = DateEntry(content_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.set_date(current_date)
            date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            # 金额
            ttk.Label(content_frame, text="分红金额:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            amount_var = tk.StringVar(value=current_amount)
            amount_entry = ttk.Entry(content_frame, textvariable=amount_var)
            amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # 按钮框架
            btn_frame = ttk.Frame(content_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            # 保存按钮
            save_btn = ttk.Button(btn_frame, text="保存",
                                  command=lambda: self.save_dividend_detail(dividend_id, amount_var.get(),
                                                                            date_entry.get_date(), stock_code, year,
                                                                            edit_dialog))
            save_btn.pack(side="left", padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(btn_frame, text="取消", command=edit_dialog.destroy)
            cancel_btn.pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"编辑分红详情失败: {str(e)}")
            traceback.print_exc()

    def add_dividend_detail(self, stock_code, stock_name, year):
        """添加新的红利详情记录 - 修复版本"""
        try:
            # 创建添加对话框
            add_dialog = tk.Toplevel(self.root)
            add_dialog.title(f"添加分红记录 - {stock_code} {stock_name}")
            add_dialog.geometry("300x200")
            add_dialog.transient(self.root)
            add_dialog.grab_set()

            # 框架
            content_frame = ttk.Frame(add_dialog)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # 股票信息
            ttk.Label(content_frame, text=f"股票: {stock_code} {stock_name}").grid(row=0, column=0, columnspan=2,
                                                                                 sticky=tk.W)
            ttk.Label(content_frame, text=f"年份: {year}").grid(row=1, column=0, columnspan=2, sticky=tk.W)

            # 日期
            ttk.Label(content_frame, text="分红日期:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            date_entry = DateEntry(content_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            date_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            # 金额
            ttk.Label(content_frame, text="分红金额:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            amount_var = tk.StringVar()
            amount_entry = ttk.Entry(content_frame, textvariable=amount_var)
            amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # 按钮框架
            btn_frame = ttk.Frame(content_frame)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            # 添加按钮
            add_btn = ttk.Button(btn_frame, text="添加",
                                 command=lambda: self.save_new_dividend_detail(
                                     stock_code, stock_name, amount_var.get(), date_entry.get_date(),
                                     year, add_dialog))
            add_btn.pack(side="left", padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(btn_frame, text="取消", command=add_dialog.destroy)
            cancel_btn.pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"添加分红详情失败: {str(e)}")
            traceback.print_exc()

    def delete_dividend_detail(self, stock_code=None, year=None):
        """删除选中的红利详情记录 - 修复版本"""
        try:

            # 初始化变量
            dividend_id = None
            stock_code = ""
            year = ""

            # 检查是否有选中的记录
            selected = self.dividend_detail_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要删除的记录")
                return

            item = self.dividend_detail_tree.item(selected[0])
            values = item['values']

            # 检查是否是有效记录（有ID值）
            if values and len(values) > 0 and values[0]:
                dividend_id = values[0]
            else:
                messagebox.showinfo("提示", "请选择有效的分红记录")
                return

            # 确认删除
            if messagebox.askyesno("确认", "确定要删除这条分红记录吗？"):
                try:
                    # 从数据库删除
                    self.cursor.execute("DELETE FROM dividends WHERE id = ?", (dividend_id,))
                    self.conn.commit()

                    # 从树形视图删除
                    self.dividend_detail_tree.delete(selected[0])

                    # 刷新主界面的红利汇总表格
                    self.refresh_dividend_table()

                    # 重新加载详情数据
                    if stock_code and year:
                        # 获取股票名称
                        self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (stock_code,))
                        name_result = self.cursor.fetchone()
                        stock_name = name_result[0] if name_result else ""

                        self.load_dividend_details(stock_code, stock_name, year)

                    messagebox.showinfo("成功", "分红记录已删除")
                except sqlite3.Error as e:
                    messagebox.showerror("数据库错误", f"删除失败: {str(e)}")
                    traceback.print_exc()

        except Exception as e:
            messagebox.showerror("错误", f"删除分红详情失败: {str(e)}")
            traceback.print_exc()

    def save_dividend_detail(self, dividend_id, amount, date, stock_code, year, dialog):
        """保存编辑的分红详情记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的分红金额")
            return

        try:
            # 更新数据库
            self.cursor.execute("""
                                UPDATE dividends
                                SET dividend      = ?,
                                    dividend_date = ?
                                WHERE id = ?
                                """, (amount, date, dividend_id))
            self.conn.commit()

            # 刷新详情列表
            self.load_dividend_details(stock_code, year)

            # 刷新主界面的红利汇总表格
            self.refresh_dividend_table()

            dialog.destroy()
            messagebox.showinfo("成功", "分红记录更新成功")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"更新失败: {str(e)}")

    def save_new_dividend_detail(self, stock_code, stock_name, amount, date, year, dialog):
        """保存新的分红详情记录"""
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的分红金额")
            return

        try:
            # 插入新记录
            self.cursor.execute("""
                                INSERT INTO dividends (stock_code, stock_name, dividend, dividend_date)
                                VALUES (?, ?, ?, ?)
                                """, (stock_code, stock_name, amount, date))
            self.conn.commit()

            # 刷新详情列表
            self.load_dividend_details(stock_code, year)

            # 刷新主界面的红利汇总表格
            self.refresh_dividend_table()

            dialog.destroy()
            messagebox.showinfo("成功", "新分红记录添加成功")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"添加失败: {str(e)}")

    # 股票代码下拉框相关功能

    def update_stock_combobox(self):
        """更新股票代码下拉框"""
        try:
            self.cursor.execute("SELECT stock_code FROM stock_codes")
            codes = [row[0] for row in self.cursor.fetchall()]

            # 更新交易记录标签页的股票代码下拉框
            self.trans_stock_code['values'] = codes

            # 更新持仓查询标签页的股票代码下拉框
            self.position_stock_code['values'] = codes

            # 更新红利标签页的股票代码下拉框
            self.div_stock_code['values'] = codes

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取股票代码失败: {str(e)}")

    def update_year_combobox(self):
        """更新年份选择器选项"""
        try:
            self.cursor.execute(
                "SELECT DISTINCT strftime('%Y', dividend_date) AS year FROM dividends ORDER BY year DESC")
            years = [row[0] for row in self.cursor.fetchall()]
            self.year_combo['values'] = years

            # 设置默认选择
            if years:
                self.year_combo.set(years[0])
            else:
                self.year_combo.set('')
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取年份失败: {str(e)}")

    # 盈亏计算方法
    def calculate_daily_profit(self, date):
        """计算指定日期的盈亏"""
        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date = ?)
                            ''', (date,))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE dividend_date = ?
                            ''', (date,))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    def calculate_monthly_profit(self, year, month):
        """计算指定月份的盈亏"""
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(int(year), int(month))[1]
        end_date = f"{year}-{month:02d}-{last_day}"

        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date BETWEEN ? AND ?)
                            ''', (start_date, end_date))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE strftime('%Y-%m', dividend_date) = ?
                            ''', (f"{year}-{month:02d}",))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    def calculate_yearly_profit(self, year):
        """计算指定年份的盈亏"""
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # 计算交易盈亏
        self.cursor.execute('''
                            SELECT SUM(
                                           CASE
                                               WHEN direction = '卖出'
                                                   THEN (amount - commission - stamp_duty - transfer_fee) - buy_cost
                                               ELSE 0
                                               END
                                   )
                            FROM (SELECT t.*,
                                         (SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                          FROM transactions AS b
                                          WHERE b.stock_code = t.stock_code
                                            AND b.direction = '买入'
                                            AND b.trade_date <= t.trade_date) AS buy_cost
                                  FROM transactions AS t
                                  WHERE trade_date BETWEEN ? AND ?)
                            ''', (start_date, end_date))
        profit = self.cursor.fetchone()[0] or 0.0

        # 计算红利
        self.cursor.execute('''
                            SELECT SUM(dividend)
                            FROM dividends
                            WHERE strftime('%Y', dividend_date) = ?
                            ''', (year,))
        dividend = self.cursor.fetchone()[0] or 0.0

        return profit + dividend

    # 资产管理功能
    def query_daily_profit(self):
        """查询日盈亏"""
        try:
            date = self.asset_date.get_date()
            profit = self.calculate_daily_profit(date)
            messagebox.showinfo("日盈亏统计", f"{date} 日盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询日盈亏失败: {str(e)}")

    def query_monthly_profit(self):
        """查询月盈亏"""
        try:
            date = self.asset_date.get_date()
            date_str = str(date)
            year, month, _ = date_str.split('-')
            profit = self.calculate_monthly_profit(year, int(month))
            messagebox.showinfo("月盈亏统计", f"{year}年{month}月盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询月盈亏失败: {str(e)}")

    def query_yearly_profit(self):
        """查询年盈亏"""
        try:
            date = self.asset_date.get_date()
            date_str = str(date)
            year = date_str.split('-')[0]
            profit = self.calculate_yearly_profit(year)
            messagebox.showinfo("年盈亏统计", f"{year}年盈亏金额: {profit:.2f}")
        except Exception as e:
            messagebox.showerror("错误", f"查询年盈亏失败: {str(e)}")

    def add_cash_flow(self, flow_type):
        """添加资金流水记录"""
        try:
            amount = simpledialog.askfloat("添加记录", f"请输入{flow_type}金额:")
            if amount is None:
                return

            flow_date = self.asset_date.get_date()

            self.cursor.execute('''
                                INSERT INTO cash_flow (amount, flow_date, type)
                                VALUES (?, ?, ?)
                                ''', (amount, flow_date, flow_type))
            self.conn.commit()
            self.refresh_cash_flow_table()
            self.refresh_asset_table()
            messagebox.showinfo("成功", f"{flow_type}记录添加成功")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")

    def delete_cash_flow(self):
        """删除资金流水记录"""
        try:
            selected = self.cash_tree.selection()
            if not selected:
                messagebox.showerror("错误", "请选择要删除的记录")
                return

            item = self.cash_tree.item(selected[0])
            flow_id = item['values'][0]

            self.cursor.execute("DELETE FROM cash_flow WHERE id = ?", (flow_id,))
            self.conn.commit()
            self.refresh_cash_flow_table()
            self.refresh_asset_table()
            messagebox.showinfo("成功", "删除成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")

    def refresh_cash_flow_table(self):
        """刷新资金流水表格"""
        # 清空表格
        for item in self.cash_tree.get_children():
            self.cash_tree.delete(item)

        # 查询并填充数据
        self.cursor.execute("SELECT id, amount, flow_date, type FROM cash_flow ORDER BY flow_date DESC")
        rows = self.cursor.fetchall()

        for row in rows:
            self.cash_tree.insert("", "end", values=row)

    def refresh_asset_table(self):
        try:
            # 清空资产表格
            for item in self.asset_tree.get_children():
                self.asset_tree.delete(item)

            # 计算现金流汇总
            self.cursor.execute("""
                                SELECT 
                                    SUM(CASE WHEN type = '入账' THEN amount ELSE 0 END) AS income,
                                    SUM(CASE WHEN type = '出账' THEN amount ELSE 0 END) AS expense,
                                    SUM(CASE WHEN type = '利润提取' THEN amount ELSE 0 END) AS profit_withdrawal
                                FROM cash_flow
                                """)
            result = self.cursor.fetchone()
            income = result[0] if result and result[0] is not None else 0.0
            expense = result[1] if result and result[1] is not None else 0.0
            profit_withdrawal = result[2] if result and result[2] is not None else 0.0

            # 计算总盈亏和持仓成本
            fifo_calculator = FIFOProfitCalculator(self.cursor)
            total_profit = 0.0

            # 获取所有持仓股票
            self.cursor.execute("""
                                SELECT DISTINCT stock_code
                                FROM transactions
                                GROUP BY stock_code
                                HAVING SUM(CASE WHEN direction = '买入' THEN quantity ELSE -quantity END) > 0
                                """)
            stocks = self.cursor.fetchall()

            # 计算每个持仓股票的盈亏和持仓成本
            for stock in stocks:
                stock_code = stock[0]

                # 获取股票名称
                self.cursor.execute("SELECT stock_name FROM stock_codes WHERE stock_code = ?", (stock_code,))
                name_result = self.cursor.fetchone()
                stock_name = name_result[0] if name_result else "未知"

                # 计算持仓数量
                self.cursor.execute("""
                                    SELECT SUM(CASE WHEN direction = '买入' THEN quantity ELSE -quantity END)
                                    FROM transactions
                                    WHERE stock_code = ?
                                    """, (stock_code,))
                position = self.cursor.fetchone()[0] or 0

                # 计算累计买入金额（包括费用）
                self.cursor.execute("""
                                    SELECT SUM(amount + commission + stamp_duty + transfer_fee)
                                    FROM transactions
                                    WHERE stock_code = ? AND direction = '买入'
                                    """, (stock_code,))
                buy_total = self.cursor.fetchone()[0] or 0.0

                # 计算累计卖出金额（扣除费用）
                self.cursor.execute("""
                                    SELECT SUM(amount - commission - stamp_duty - transfer_fee)
                                    FROM transactions
                                    WHERE stock_code = ? AND direction = '卖出'
                                    """, (stock_code,))
                sell_total = self.cursor.fetchone()[0] or 0.0

                # 计算该股票的分红总额
                self.cursor.execute("""
                                    SELECT SUM(dividend)
                                    FROM dividends
                                    WHERE stock_code = ?
                                    """, (stock_code,))
                dividend_total = self.cursor.fetchone()[0] or 0.0

                # 计算持仓成本 = (累计买入金额 - 累计卖出金额 + 累计分红金额) / 当前持仓数量
                if position > 0:
                    cost = (buy_total - sell_total + dividend_total) / position
                else:
                    cost = 0.0

                # 计算该股票的盈亏（只计算卖出部分的盈亏）
                profit = fifo_calculator.calculate_stock_profit(stock_code)
                total_profit += profit

                # 添加到表格
                self.asset_tree.insert("", "end", values=(
                    stock_code, stock_name, position, f"{cost:.2f}", f"{profit:.2f}"
                ))

            # 计算盈亏余额
            profit_balance = total_profit - profit_withdrawal

            # 更新状态栏变量
            self.total_profit_var.set(f"{total_profit:.2f}")
            self.withdrawn_profit_var.set(f"{profit_withdrawal:.2f}")
            self.profit_balance_var.set(f"{profit_balance:.2f}")
            self.income_amount_var.set(f"{income:.2f}")
            self.expense_amount_var.set(f"{expense:.2f}")

        except Exception as e:
            messagebox.showerror("错误", f"刷新资产表格失败: {str(e)}")
            traceback.print_exc()


# 运行主程序
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = StockManagementSystem(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序发生错误: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("致命错误", f"程序发生错误: {str(e)}")