import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import random
import json
import os
from threading import Thread
import time

class MembershipSystem:
    def __init__(self):
        self.members = {}
        self.transactions = []
        self.auto_deduction_enabled = True
        self.load_data()
        
        # 启动自动扣费线程
        self.auto_deduction_thread = Thread(target=self.auto_deduction_worker, daemon=True)
        self.auto_deduction_thread.start()
    
    def load_data(self):
        """从文件加载会员和交易数据"""
        try:
            if os.path.exists("members.json"):
                with open("members.json", "r") as f:
                    self.members = json.load(f)
            
            if os.path.exists("transactions.json"):
                with open("transactions.json", "r") as f:
                    self.transactions = json.load(f)
        except Exception as e:
            print(f"加载数据时出错: {e}")
    
    def save_data(self):
        """将会员和交易数据保存到文件"""
        try:
            with open("members.json", "w") as f:
                json.dump(self.members, f, indent=2)
            
            with open("transactions.json", "w") as f:
                json.dump(self.transactions, f, indent=2)
        except Exception as e:
            print(f"保存数据时出错: {e}")
    
    def generate_card_id(self):
        """生成唯一的会员卡ID"""
        while True:
            card_id = f"BC{random.randint(1000, 9999)}"
            if card_id not in self.members:
                return card_id
    
    def create_member(self, name, phone, initial_balance=0):
        """创建新会员"""
        card_id = self.generate_card_id()
        self.members[card_id] = {
            "name": name,
            "phone": phone,
            "balance": initial_balance,
            "status": "active",
            "join_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "last_visit": None
        }
        
        if initial_balance > 0:
            self.add_transaction(card_id, initial_balance, "initial_deposit", f"新会员开户充值")
        
        return card_id
    
    def add_transaction(self, card_id, amount, transaction_type, description):
        """添加交易记录"""
        transaction = {
            "card_id": card_id,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(transaction)
        return transaction
    
    def recharge(self, card_id, amount):
        """会员卡充值"""
        if card_id not in self.members:
            return False, "会员卡不存在"
        
        self.members[card_id]["balance"] += amount
        self.add_transaction(card_id, amount, "recharge", f"会员卡充值")
        return True, f"充值成功! 当前余额: ¥{self.members[card_id]['balance']:.2f}"
    
    def manual_deduction(self, card_id, hours):
        """手动扣费 - 按小时计费"""
        if card_id not in self.members:
            return False, "会员卡不存在"
        
        if self.members[card_id]["status"] != "active":
            return False, "会员卡已冻结"
        
        # 台球厅计费标准 (元/小时)
        rate = 30 if hours < 2 else 25  # 2小时以上享受折扣
        
        amount = hours * rate
        
        if self.members[card_id]["balance"] < amount:
            return False, f"余额不足! 需要: ¥{amount:.2f}, 当前余额: ¥{self.members[card_id]['balance']:.2f}"
        
        self.members[card_id]["balance"] -= amount
        self.members[card_id]["last_visit"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.add_transaction(
            card_id, 
            -amount, 
            "consumption", 
            f"消费 {hours} 小时 (¥{rate}/小时)"
        )
        
        return True, f"扣费成功! 消费 {hours} 小时, 金额: ¥{amount:.2f}, 余额: ¥{self.members[card_id]['balance']:.2f}"
    
    def auto_deduction(self):
        """自动扣费 - 处理包月会员"""
        today = datetime.datetime.now().date()
        results = []
        
        for card_id, member in list(self.members.items()):
            # 检查包月会员是否到期
            if member.get("membership_type") == "monthly":
                expiry_date = datetime.datetime.strptime(member["expiry_date"], "%Y-%m-%d").date()
                if today >= expiry_date:
                    # 自动续费
                    monthly_fee = 500  # 包月费用
                    if member["balance"] >= monthly_fee:
                        member["balance"] -= monthly_fee
                        new_expiry = expiry_date + datetime.timedelta(days=30)
                        member["expiry_date"] = new_expiry.strftime("%Y-%m-%d")
                        
                        self.add_transaction(
                            card_id, 
                            -monthly_fee, 
                            "auto_deduction", 
                            f"包月自动续费 (有效期至 {new_expiry})"
                        )
                        
                        results.append(f"会员 {member['name']} 自动续费成功! 有效期延长至 {new_expiry}")
                    else:
                        # 余额不足，转为普通会员
                        member["membership_type"] = "regular"
                        results.append(f"会员 {member['name']} 余额不足，已转为普通会员")
        
        return results
    
    def auto_deduction_worker(self):
        """自动扣费工作线程"""
        while self.auto_deduction_enabled:
            now = datetime.datetime.now()
            # 每天凌晨2点执行自动扣费
            if now.hour == 2 and now.minute == 0:
                results = self.auto_deduction()
                if results:
                    print(f"[{now}] 自动扣费结果:")
                    for msg in results:
                        print(f"  - {msg}")
                self.save_data()
            
            # 每分钟检查一次
            time.sleep(60)
    
    def get_member_info(self, card_id):
        """获取会员信息"""
        if card_id in self.members:
            return self.members[card_id]
        return None
    
    def get_members_by_name(self, name):
        """根据姓名获取会员信息（支持重名）"""
        result = {}
        for card_id, member in self.members.items():
            if member["name"] == name:
                result[card_id] = member
        return result
    
    def get_all_members(self):
        """获取所有会员信息"""
        return self.members
    
    def get_member_info_by_any(self, identifier):
        """根据卡号或姓名获取会员信息"""
        # 首先尝试按卡号搜索
        if identifier in self.members:
            return {identifier: self.members[identifier]}
        
        # 然后尝试按姓名搜索
        return self.get_members_by_name(identifier)
    
    def get_transactions(self, card_id, limit=10):
        """获取会员的交易记录"""
        member_transactions = [t for t in self.transactions if t["card_id"] == card_id]
        return sorted(member_transactions, key=lambda x: x["timestamp"], reverse=True)[:limit]


class MembershipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("台球厅会员卡管理系统")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # 初始化系统
        self.system = MembershipSystem()
        
        # 创建样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Success.TLabel", foreground="green")
        self.style.configure("Error.TLabel", foreground="red")
        
        # 创建标签页
        self.tab_control = ttk.Notebook(root)
        
        # 会员管理标签页
        self.tab_member = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_member, text="会员管理")
        
        # 充值标签页
        self.tab_recharge = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_recharge, text="会员充值")
        
        # 消费标签页
        self.tab_consume = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_consume, text="消费扣费")
        
        # 交易记录标签页
        self.tab_transactions = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_transactions, text="交易记录")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 初始化标签页
        self.setup_member_tab()
        self.setup_recharge_tab()
        self.setup_consume_tab()
        self.setup_transactions_tab()
        
        # 初始化一些变量
        self.current_recharge_card_id = None
        self.current_consume_card_id = None
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        self.update_status("就绪")
        
        # 退出时保存数据
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_status(self, message):
        """更新状态栏"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"[{timestamp}] {message}")
    
    def on_closing(self):
        """关闭窗口时保存数据"""
        self.system.auto_deduction_enabled = False
        self.system.save_data()
        self.root.destroy()
    
    def setup_member_tab(self):
        """设置会员管理标签页"""
        frame = ttk.LabelFrame(self.tab_member, text="会员信息")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 搜索区域
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=15)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_member())  # 回车键触发搜索
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self.search_member)
        search_btn.pack(side="left", padx=5)
        
        # 添加按姓名搜索的选项
        ttk.Label(search_frame, text="姓名:").pack(side="left", padx=5)
        self.search_name_entry = ttk.Entry(search_frame, width=15)
        self.search_name_entry.pack(side="left", padx=5)
        self.search_name_entry.bind("<Return>", lambda event: self.search_member_by_name())  # 回车键触发搜索
        
        search_name_btn = ttk.Button(search_frame, text="按姓名搜索", command=self.search_member_by_name)
        search_name_btn.pack(side="left", padx=5)
        
        # 重置按钮
        reset_btn = ttk.Button(search_frame, text="重置", command=self.reset_member_search)
        reset_btn.pack(side="left", padx=5)
        
        # 会员列表区域
        list_frame = ttk.LabelFrame(frame, text="会员列表")
        list_frame.pack(fill="both", padx=5, pady=5, expand=True)
        
        # 会员列表表格
        columns = ("card_id", "name", "phone", "status", "balance", "join_date", "last_visit")
        self.member_tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=8
        )
        
        # 设置列标题
        self.member_tree.heading("card_id", text="卡号")
        self.member_tree.heading("name", text="姓名")
        self.member_tree.heading("phone", text="电话")
        self.member_tree.heading("status", text="状态")
        self.member_tree.heading("balance", text="余额")
        self.member_tree.heading("join_date", text="加入日期")
        self.member_tree.heading("last_visit", text="最后消费")
        
        # 设置列宽
        self.member_tree.column("card_id", width=100)
        self.member_tree.column("name", width=80)
        self.member_tree.column("phone", width=100)
        self.member_tree.column("status", width=60)
        self.member_tree.column("balance", width=80)
        self.member_tree.column("join_date", width=100)
        self.member_tree.column("last_visit", width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.member_tree.yview)
        self.member_tree.configure(yscrollcommand=scrollbar.set)
        
        self.member_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", padx=5, pady=5)
        
        # 绑定双击事件以查看会员详细信息
        self.member_tree.bind("<Double-1>", self.on_member_select)
        
        # 分页控制
        pagination_frame = ttk.Frame(list_frame)
        pagination_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        self.page_var = tk.StringVar(value="1")
        self.total_pages_var = tk.StringVar(value="1")
        self.page_size_var = tk.StringVar(value="20")  # 默认每页显示20条记录
        
        ttk.Label(pagination_frame, text="每页:").pack(side="left", padx=5)
        page_size_combo = ttk.Combobox(pagination_frame, textvariable=self.page_size_var, width=5, state="readonly")
        page_size_combo['values'] = ('10', '20', '50', '100')
        page_size_combo.pack(side="left", padx=5)
        page_size_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_member_list())
        
        ttk.Label(pagination_frame, text="第").pack(side="left", padx=5)
        self.page_entry = ttk.Entry(pagination_frame, textvariable=self.page_var, width=5)
        self.page_entry.pack(side="left", padx=2)
        self.page_entry.bind("<Return>", lambda event: self.go_to_page())
        
        ttk.Label(pagination_frame, text="页，共").pack(side="left", padx=2)
        ttk.Label(pagination_frame, textvariable=self.total_pages_var).pack(side="left", padx=2)
        ttk.Label(pagination_frame, text="页").pack(side="left", padx=2)
        
        prev_btn = ttk.Button(pagination_frame, text="上一页", command=self.prev_page)
        prev_btn.pack(side="left", padx=5)
        
        next_btn = ttk.Button(pagination_frame, text="下一页", command=self.next_page)
        next_btn.pack(side="left", padx=5)
        
        go_btn = ttk.Button(pagination_frame, text="跳转", command=self.go_to_page)
        go_btn.pack(side="left", padx=5)
        
        # 刷新会员列表
        self.current_page = 1
        self.refresh_member_list()
        
        # 会员信息显示
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="both", padx=5, pady=5, expand=True)
        
        labels = ["卡号:", "姓名:", "电话:", "状态:", "余额:", "加入日期:", "最后消费:"]
        self.info_vars = {}
        
        for i, label in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            var = tk.StringVar()
            ttk.Label(info_frame, textvariable=var).grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
            self.info_vars[label.strip(":")] = var
        
        # 创建新会员
        new_frame = ttk.LabelFrame(frame, text="创建新会员")
        new_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(new_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5)
        self.new_name = ttk.Entry(new_frame, width=20)
        self.new_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(new_frame, text="电话:").grid(row=0, column=2, padx=5, pady=5)
        self.new_phone = ttk.Entry(new_frame, width=20)
        self.new_phone.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(new_frame, text="初始金额:").grid(row=0, column=4, padx=5, pady=5)
        self.new_balance = ttk.Entry(new_frame, width=10)
        self.new_balance.grid(row=0, column=5, padx=5, pady=5)
        self.new_balance.insert(0, "100")
        
        create_btn = ttk.Button(new_frame, text="创建会员", command=self.create_member)
        create_btn.grid(row=0, column=6, padx=5, pady=5)
    
    def refresh_member_list(self):
        """刷新会员列表（带分页）"""
        # 清空现有数据
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        # 获取所有会员数据
        all_members = list(self.system.members.items())
        total_members = len(all_members)
        
        # 计算分页
        page_size = int(self.page_size_var.get())
        total_pages = max(1, (total_members + page_size - 1) // page_size)
        
        # 更新页面信息
        self.current_page = max(1, min(self.current_page, total_pages if total_pages > 0 else 1))
        self.page_var.set(str(self.current_page))
        self.total_pages_var.set(str(total_pages))
        
        # 计算当前页的会员数据
        start_idx = (self.current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_members)
        current_members = all_members[start_idx:end_idx]
        
        # 添加数据到表格
        for card_id, member in current_members:
            # 格式化余额
            balance_str = f"¥{member['balance']:.2f}"
            # 格式化最后消费时间
            last_visit = member.get("last_visit", "无记录")
            
            # 添加数据到表格
            self.member_tree.insert("", "end", values=(
                card_id,
                member["name"],
                member["phone"],
                member["status"],
                balance_str,
                member["join_date"],
                last_visit
            ))
    
    def on_member_select(self, event):
        """双击会员列表项时的事件处理"""
        selection = self.member_tree.selection()
        if selection:
            item = self.member_tree.item(selection[0])
            card_id = item["values"][0]  # 卡号是第一列
            
            # 在搜索框中填入卡号并搜索
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, card_id)
            self.search_member()
    
    def search_member(self):
        """搜索会员信息（按卡号）"""
        card_id = self.search_entry.get().strip()
        name = self.search_name_entry.get().strip()
        
        # 如果没有输入任何内容，显示所有会员
        if not card_id and not name:
            self.refresh_member_list()
            self.update_status("显示所有会员")
            return
        
        # 优先使用卡号搜索，如果没有卡号则使用姓名搜索
        if card_id:
            members = self.system.get_member_info_by_any(card_id)
        elif name:
            members = self.system.get_members_by_name(name)
        else:
            self.update_status("请输入会员卡号或姓名")
            return
        
        if members:
            # 如果找到多个会员（按姓名搜索时可能有重名）
            if len(members) == 1:
                # 单个会员，显示详细信息
                card_id, member = list(members.items())[0]
                self.info_vars["卡号"].set(card_id)
                self.info_vars["姓名"].set(member["name"])
                self.info_vars["电话"].set(member["phone"])
                self.info_vars["状态"].set(member["status"])
                self.info_vars["余额"].set(f"¥{member['balance']:.2f}")
                self.info_vars["加入日期"].set(member["join_date"])
                self.info_vars["最后消费"].set(member.get("last_visit", "无记录"))
                self.update_status(f"找到会员: {member['name']}")
            else:
                # 多个会员，清空详细信息并显示在列表中
                self.info_vars["卡号"].set("")
                self.info_vars["姓名"].set("")
                self.info_vars["电话"].set("")
                self.info_vars["状态"].set("")
                self.info_vars["余额"].set("")
                self.info_vars["加入日期"].set("")
                self.info_vars["最后消费"].set("")
                
                # 在列表中高亮显示这些会员
                self.highlight_members(members)
                self.update_status(f"找到 {len(members)} 个会员: {', '.join([m['name'] for m in members.values()])}")
        else:
            self.update_status(f"未找到会员: {card_id if card_id else name}")
    
    def search_member_by_name(self):
        """按姓名搜索会员"""
        name = self.search_name_entry.get().strip()
        if not name:
            self.refresh_member_list()  # 如果没有输入姓名，显示所有会员
            self.update_status("显示所有会员")
            return
        
        members = self.system.get_members_by_name(name)
        if members:
            # 清空详细信息
            self.info_vars["卡号"].set("")
            self.info_vars["姓名"].set("")
            self.info_vars["电话"].set("")
            self.info_vars["状态"].set("")
            self.info_vars["余额"].set("")
            self.info_vars["加入日期"].set("")
            self.info_vars["最后消费"].set("")
            
            # 在列表中高亮显示这些会员
            self.highlight_members(members)
            self.update_status(f"找到 {len(members)} 个姓名为 {name} 的会员")
        else:
            self.update_status(f"未找到姓名为 {name} 的会员")
    
    def highlight_members(self, members):
        """在会员列表中高亮显示指定的会员"""
        # 清空现有数据
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        # 添加指定会员到列表
        for card_id, member in members.items():
            # 格式化余额
            balance_str = f"¥{member['balance']:.2f}"
            # 格式化最后消费时间
            last_visit = member.get("last_visit", "无记录")
            
            # 添加数据到表格
            self.member_tree.insert("", "end", values=(
                card_id,
                member["name"],
                member["phone"],
                member["status"],
                balance_str,
                member["join_date"],
                last_visit
            ))
        
        # 重新绑定双击事件以处理重名情况
        self.member_tree.unbind("<Double-1>")
        self.member_tree.bind("<Double-1>", self.on_member_select)
    
    def next_page(self):
        """下一页"""
        total_pages = int(self.total_pages_var.get())
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_member_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_member_list()
    
    def go_to_page(self):
        """跳转到指定页"""
        try:
            page = int(self.page_entry.get())
            total_pages = int(self.total_pages_var.get())
            if 1 <= page <= total_pages:
                self.current_page = page
                self.refresh_member_list()
            else:
                self.update_status(f"页码超出范围 (1-{total_pages})")
        except ValueError:
            self.update_status("请输入有效的页码")
    
    def reset_member_search(self):
        """重置搜索，清空搜索框并刷新会员列表"""
        self.search_entry.delete(0, tk.END)
        self.search_name_entry.delete(0, tk.END)
        self.refresh_member_list()
        # 清空详细信息
        for key in self.info_vars:
            self.info_vars[key].set("")
        self.update_status("已重置，显示所有会员")
    
    def create_member(self):
        """创建新会员"""
        name = self.new_name.get().strip()
        phone = self.new_phone.get().strip()
        balance = self.new_balance.get().strip()
        
        if not name:
            self.update_status("请输入姓名")
            return
        
        if not phone:
            self.update_status("请输入电话")
            return
        
        try:
            balance = float(balance)
            if balance < 0:
                raise ValueError
        except ValueError:
            self.update_status("请输入有效的金额")
            return
        
        card_id = self.system.create_member(name, phone, balance)
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, card_id)
        self.search_member()
        self.refresh_member_list()  # 刷新会员列表
        self.update_status(f"创建会员成功! 卡号: {card_id}")
    
    def setup_recharge_tab(self):
        """设置会员充值标签页"""
        frame = ttk.LabelFrame(self.tab_recharge, text="会员充值")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 卡号/姓名输入
        card_frame = ttk.Frame(frame)
        card_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(card_frame, text="会员卡号:").pack(side="left", padx=5)
        self.recharge_card_entry = ttk.Entry(card_frame, width=15)
        self.recharge_card_entry.pack(side="left", padx=5)
        
        ttk.Label(card_frame, text="或姓名:").pack(side="left", padx=5)
        self.recharge_name_entry = ttk.Entry(card_frame, width=15)
        self.recharge_name_entry.pack(side="left", padx=5)
        
        card_search_btn = ttk.Button(card_frame, text="搜索", command=self.search_recharge_member)
        card_search_btn.pack(side="left", padx=5)
        
        # 重置按钮
        reset_btn = ttk.Button(card_frame, text="重置", command=self.reset_recharge_search)
        reset_btn.pack(side="left", padx=5)
        
        # 会员信息显示
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.recharge_name_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.recharge_name_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(info_frame, text="当前余额:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.recharge_balance_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.recharge_balance_var).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # 充值金额
        amount_frame = ttk.Frame(frame)
        amount_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(amount_frame, text="充值金额:").pack(side="left", padx=5)
        self.amount_entry = ttk.Entry(amount_frame, width=15)
        self.amount_entry.pack(side="left", padx=5)
        
        # 充值按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        amounts = [50, 100, 200, 500]
        for amount in amounts:
            btn = ttk.Button(
                btn_frame, 
                text=f"¥{amount}", 
                command=lambda amt=amount: self.amount_entry.insert(tk.END, str(amt))
            )
            btn.pack(side="left", padx=5)
        
        recharge_btn = ttk.Button(btn_frame, text="确认充值", command=self.do_recharge)
        recharge_btn.pack(side="right", padx=5)
        
        # 充值结果
        self.recharge_result = tk.StringVar()
        ttk.Label(frame, textvariable=self.recharge_result, style="Success.TLabel").pack(pady=5)
    
    def search_recharge_member(self):
        """搜索充值会员（支持卡号或姓名搜索）"""
        card_id = self.recharge_card_entry.get().strip()
        name = self.recharge_name_entry.get().strip()
        
        # 如果没有输入任何内容，清空信息
        if not card_id and not name:
            self.recharge_name_var.set("")
            self.recharge_balance_var.set("")
            self.current_recharge_card_id = None
            self.update_status("请输入会员卡号或姓名")
            return
        
        # 优先使用卡号搜索
        if card_id:
            members = self.system.get_member_info_by_any(card_id)
        elif name:
            members = self.system.get_members_by_name(name)
        else:
            self.update_status("请输入会员卡号或姓名")
            return
        
        if members:
            # 如果找到多个会员（按姓名搜索时可能有重名）
            if len(members) == 1:
                # 单个会员，显示详细信息
                card_id, member = list(members.items())[0]
                self.recharge_name_var.set(member["name"])
                self.recharge_balance_var.set(f"¥{member['balance']:.2f}")
                # 保存找到的卡号用于后续充值操作
                self.current_recharge_card_id = card_id
                self.update_status(f"找到会员: {member['name']}")
            else:
                # 多个会员，让用户选择
                self.recharge_name_var.set("")
                self.recharge_balance_var.set("")
                self.current_recharge_card_id = None
                # 可以弹窗让用户选择具体是哪个会员
                names = [m['name'] for m in members.values()]
                self.update_status(f"找到多个姓名为 {name} 的会员: {', '.join(names)}，请使用卡号精确搜索")
        else:
            self.recharge_name_var.set("")
            self.recharge_balance_var.set("")
            self.current_recharge_card_id = None
            if card_id:
                self.update_status(f"未找到会员卡: {card_id}")
            else:
                self.update_status(f"未找到姓名为 {name} 的会员")
    
    def reset_recharge_search(self):
        """重置充值搜索"""
        self.recharge_card_entry.delete(0, tk.END)
        self.recharge_name_entry.delete(0, tk.END)
        self.recharge_name_var.set("")
        self.recharge_balance_var.set("")
        self.current_recharge_card_id = None
        self.update_status("已重置充值搜索")
    
    def do_recharge(self):
        """执行充值操作"""
        card_id = getattr(self, 'current_recharge_card_id', None)
        if not card_id:
            # 如果没有通过搜索获取卡号，尝试直接使用输入的卡号
            card_id = self.recharge_card_entry.get().strip()
            if not card_id:
                self.update_status("请先搜索会员")
                return
        
        amount_str = self.amount_entry.get().strip()
        
        if not amount_str:
            self.update_status("请输入充值金额")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.update_status("请输入有效的金额")
            return
        
        success, message = self.system.recharge(card_id, amount)
        if success:
            self.recharge_result.set(message)
            self.search_recharge_member()
            self.refresh_member_list()  # 刷新会员列表
            self.update_status(message)
        else:
            messagebox.showerror("充值失败", message)
            self.update_status(f"充值失败: {message}")
    
    def setup_consume_tab(self):
        """设置消费扣费标签页"""
        frame = ttk.LabelFrame(self.tab_consume, text="消费扣费")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 卡号/姓名输入
        card_frame = ttk.Frame(frame)
        card_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(card_frame, text="会员卡号:").pack(side="left", padx=5)
        self.consume_card_entry = ttk.Entry(card_frame, width=15)
        self.consume_card_entry.pack(side="left", padx=5)
        
        ttk.Label(card_frame, text="或姓名:").pack(side="left", padx=5)
        self.consume_name_entry = ttk.Entry(card_frame, width=15)
        self.consume_name_entry.pack(side="left", padx=5)
        
        card_search_btn = ttk.Button(card_frame, text="搜索", command=self.search_consume_member)
        card_search_btn.pack(side="left", padx=5)
        
        # 重置按钮
        reset_btn = ttk.Button(card_frame, text="重置", command=self.reset_consume_search)
        reset_btn.pack(side="left", padx=5)
        
        # 会员信息显示
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.consume_name_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.consume_name_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(info_frame, text="当前余额:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.consume_balance_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.consume_balance_var).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # 消费时间
        time_frame = ttk.Frame(frame)
        time_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(time_frame, text="消费时间(小时):").pack(side="left", padx=5)
        self.hours_entry = ttk.Entry(time_frame, width=10)
        self.hours_entry.pack(side="left", padx=5)
        self.hours_entry.insert(0, "1")
        
        # 消费按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        hours_options = [0.5, 1, 1.5, 2, 3, 4]
        for hours in hours_options:
            btn = ttk.Button(
                btn_frame, 
                text=f"{hours}小时", 
                command=lambda h=hours: self.hours_entry.insert(tk.END, str(h))
            )
            btn.pack(side="left", padx=5)
        
        consume_btn = ttk.Button(btn_frame, text="确认消费", command=self.do_consume)
        consume_btn.pack(side="right", padx=5)
        
        # 消费结果
        self.consume_result = tk.StringVar()
        ttk.Label(frame, textvariable=self.consume_result, style="Success.TLabel").pack(pady=5)
    
    def search_consume_member(self):
        """搜索消费会员（支持卡号或姓名搜索）"""
        card_id = self.consume_card_entry.get().strip()
        name = self.consume_name_entry.get().strip()
        
        # 如果没有输入任何内容，清空信息
        if not card_id and not name:
            self.consume_name_var.set("")
            self.consume_balance_var.set("")
            self.current_consume_card_id = None
            self.update_status("请输入会员卡号或姓名")
            return
        
        # 优先使用卡号搜索
        if card_id:
            members = self.system.get_member_info_by_any(card_id)
        elif name:
            members = self.system.get_members_by_name(name)
        else:
            self.update_status("请输入会员卡号或姓名")
            return
        
        if members:
            # 如果找到多个会员（按姓名搜索时可能有重名）
            if len(members) == 1:
                # 单个会员，显示详细信息
                card_id, member = list(members.items())[0]
                self.consume_name_var.set(member["name"])
                self.consume_balance_var.set(f"¥{member['balance']:.2f}")
                # 保存找到的卡号用于后续消费操作
                self.current_consume_card_id = card_id
                self.update_status(f"找到会员: {member['name']}")
            else:
                # 多个会员，让用户选择
                self.consume_name_var.set("")
                self.consume_balance_var.set("")
                self.current_consume_card_id = None
                # 可以弹窗让用户选择具体是哪个会员
                names = [m['name'] for m in members.values()]
                self.update_status(f"找到多个姓名为 {name} 的会员: {', '.join(names)}，请使用卡号精确搜索")
        else:
            self.consume_name_var.set("")
            self.consume_balance_var.set("")
            self.current_consume_card_id = None
            if card_id:
                self.update_status(f"未找到会员卡: {card_id}")
            else:
                self.update_status(f"未找到姓名为 {name} 的会员")
    
    def reset_consume_search(self):
        """重置消费搜索"""
        self.consume_card_entry.delete(0, tk.END)
        self.consume_name_entry.delete(0, tk.END)
        self.consume_name_var.set("")
        self.consume_balance_var.set("")
        self.current_consume_card_id = None
        self.update_status("已重置消费搜索")
    
    def do_consume(self):
        """执行消费操作"""
        card_id = getattr(self, 'current_consume_card_id', None)
        if not card_id:
            # 如果没有通过搜索获取卡号，尝试直接使用输入的卡号
            card_id = self.consume_card_entry.get().strip()
            if not card_id:
                self.update_status("请先搜索会员")
                return
        
        hours_str = self.hours_entry.get().strip()
        
        if not hours_str:
            self.update_status("请输入消费时间")
            return
        
        try:
            hours = float(hours_str)
            if hours <= 0:
                raise ValueError
        except ValueError:
            self.update_status("请输入有效的时间")
            return
        
        success, message = self.system.manual_deduction(card_id, hours)
        if success:
            self.consume_result.set(message)
            self.search_consume_member()
            self.refresh_member_list()  # 刷新会员列表
            self.update_status(message)
        else:
            messagebox.showerror("消费失败", message)
            self.update_status(f"消费失败: {message}")
    
    def setup_transactions_tab(self):
        """设置交易记录标签页"""
        frame = ttk.LabelFrame(self.tab_transactions, text="交易记录查询")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 卡号/姓名输入
        card_frame = ttk.Frame(frame)
        card_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(card_frame, text="会员卡号:").pack(side="left", padx=5)
        self.trans_card_entry = ttk.Entry(card_frame, width=15)
        self.trans_card_entry.pack(side="left", padx=5)
        
        ttk.Label(card_frame, text="或姓名:").pack(side="left", padx=5)
        self.trans_name_entry = ttk.Entry(card_frame, width=15)
        self.trans_name_entry.pack(side="left", padx=5)
        
        search_btn = ttk.Button(card_frame, text="查询", command=self.show_transactions)
        search_btn.pack(side="left", padx=5)
        
        # 重置按钮
        reset_btn = ttk.Button(card_frame, text="重置", command=self.reset_transactions_search)
        reset_btn.pack(side="left", padx=5)
        
        # 交易记录表格
        columns = ("timestamp", "type", "amount", "description")
        self.trans_tree = ttk.Treeview(
            frame, 
            columns=columns, 
            show="headings", 
            height=10
        )
        
        # 设置列标题
        self.trans_tree.heading("timestamp", text="时间")
        self.trans_tree.heading("type", text="类型")
        self.trans_tree.heading("amount", text="金额")
        self.trans_tree.heading("description", text="描述")
        
        # 设置列宽
        self.trans_tree.column("timestamp", width=150)
        self.trans_tree.column("type", width=80)
        self.trans_tree.column("amount", width=100)
        self.trans_tree.column("description", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trans_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", padx=5, pady=5)
    
    def show_transactions(self):
        """显示交易记录"""
        card_id = self.trans_card_entry.get().strip()
        name = self.trans_name_entry.get().strip()
        
        # 如果没有输入任何内容，清空交易记录
        if not card_id and not name:
            # 清空现有数据
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            self.update_status("请输入会员卡号或姓名")
            return
        
        # 优先使用卡号搜索
        if card_id:
            members = self.system.get_member_info_by_any(card_id)
        elif name:
            members = self.system.get_members_by_name(name)
        else:
            self.update_status("请输入会员卡号或姓名")
            return
        
        # 清空现有数据
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        if not members:
            if card_id:
                self.update_status(f"没有找到会员卡: {card_id}")
            else:
                self.update_status(f"没有找到姓名为 {name} 的会员")
            return
        
        # 如果找到多个会员（按姓名搜索时可能有重名）
        if len(members) > 1:
            # 对每个会员显示交易记录
            all_transactions = []
            for member_card_id in members.keys():
                member_transactions = self.system.get_transactions(member_card_id)
                all_transactions.extend(member_transactions)
            
            # 按时间排序
            all_transactions = sorted(all_transactions, key=lambda x: x["timestamp"], reverse=True)
            
            if all_transactions:
                # 添加数据到表格
                for trans in all_transactions:
                    amount = trans["amount"]
                    # 根据金额正负设置颜色
                    amount_text = f"+¥{amount:.2f}" if amount > 0 else f"¥{amount:.2f}"
                    self.trans_tree.insert("", "end", values=(
                        trans["timestamp"],
                        trans["type"],
                        amount_text,
                        trans["description"]
                    ))
                
                self.update_status(f"显示 {len(members)} 个姓名为 {name} 的会员的 {len(all_transactions)} 条交易记录")
            else:
                self.update_status(f"没有找到姓名为 {name} 的会员的交易记录")
        else:
            # 单个会员，显示其交易记录
            card_id, member = list(members.items())[0]
            transactions = self.system.get_transactions(card_id)
            
            if transactions:
                # 添加数据到表格
                for trans in transactions:
                    amount = trans["amount"]
                    # 根据金额正负设置颜色
                    amount_text = f"+¥{amount:.2f}" if amount > 0 else f"¥{amount:.2f}"
                    self.trans_tree.insert("", "end", values=(
                        trans["timestamp"],
                        trans["type"],
                        amount_text,
                        trans["description"]
                    ))
                
                self.update_status(f"显示会员 {member['name']} ({card_id}) 的 {len(transactions)} 条交易记录")
            else:
                self.update_status(f"会员 {member['name']} ({card_id}) 没有交易记录")
    
    def reset_transactions_search(self):
        """重置交易记录搜索"""
        self.trans_card_entry.delete(0, tk.END)
        self.trans_name_entry.delete(0, tk.END)
        # 清空交易记录表格
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        self.update_status("已重置交易记录搜索")


if __name__ == "__main__":
    root = tk.Tk()
    app = MembershipApp(root)
    root.mainloop()