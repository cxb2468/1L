import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import pandas as pd
from datetime import datetime

# 软件调用三个api，以下内容将先展示api，接着是py源码
#
# Api:
# 1.查询品牌金店当日金价(部分品牌，非全国所有品牌金店)
# 接口地址：https://free.xwteam.cn/doc/140 返回格式：JSON  请求方式：GET  请求参数：https://free.xwteam.cn/api/gold/brand
# 2.今日黄金价格
# 接口地址：https://tools.mgtv100.com/external/v1/pear/goldPrice 返回格式：JSON  请求方式：GET  请求参数：https://tools.mgtv100.com/external/v1/pear/goldPrice
# 3.可以查国内十大金店 国际 还有国内的
# 接口地址：https://api.lolimi.cn/API/huangj/api.php 返回格式：json  请求方式：GET  请求参数：https://api.lolimi.cn/API/huangj/api.php

class GoldPriceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("实时贵金属行情")
        self.root.geometry("1400x800")
        # 样式配置
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('微软雅黑', 11, 'bold'))
        self.style.configure("Treeview", font=('宋体', 10), rowheight=28)
        self.style.configure("TButton", font=('微软雅黑', 10))

        # 主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # 控制面板
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=8)

        # 刷新按钮
        self.refresh_btn = ttk.Button(
            self.control_frame,
            text="立即刷新数据",
            command=self.refresh_data
        )
        self.refresh_btn.pack(side=tk.LEFT)

        # 导出按钮
        self.export_btn = ttk.Button(
            self.control_frame,
            text="导出Excel",
            command=self.export_data,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # 状态标签
        self.status_label = ttk.Label(
            self.control_frame,
            text="就绪",
            font=('微软雅黑', 9),
            foreground="#666"
        )
        self.status_label.pack(side=tk.RIGHT)

        # 数据展示区
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建标签页
        self.create_tab("国内现货", ["品种名称", "买入价(元/克)", "卖出价(元/克)", "当日最高", "当日最低", "涨跌幅", "交易状态"])
        self.create_tab("上海交易所", ["品种名称", "买入价(元/克)", "卖出价(元/克)", "当日最高", "当日最低", "涨跌幅", "交易状态"])
        self.create_tab("国际市场", ["品种名称", "买入价(美元/盎司)", "卖出价(美元/盎司)", "当日最高", "当日最低", "涨跌幅", "交易状态"])
        self.create_tab("品牌金店", ["品牌名称", "黄金价格(元/克)", "金条价格(元/克)", "单位", "报价时间"])

        # 页脚信息
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.footer = ttk.Label(
            footer_frame,
            text="数据来源：上海黄金交易所、伦敦金银市场协会、中国黄金协会 | 更新时间：实时同步",
            font=('微软雅黑', 8),
            foreground="#999"
        )
        self.footer.pack(side=tk.LEFT, anchor=tk.W)

        self.author_label = ttk.Label(
            footer_frame,
            text="作者：Stars313  吾爱破解：www.52pojie.cn",
            font=('微软雅黑', 8),
            foreground="#999",
            padding=(0,0,10,0)
        )
        self.author_label.pack(side=tk.RIGHT, anchor=tk.E)

        # 数据存储
        self.current_data = {
            "国内现货": {"items": [], "unit": "", "status": 0},
            "上海交易所": {"items": [], "unit": "", "status": 0},
            "国际市场": {"items": [], "unit": "", "status": 0},
            "品牌金店": []
        }

        # 初始化数据
        self.refresh_data()

    def create_tab(self, tab_name, columns):
        """创建带表格的标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=tab_name)

        # 创建表格
        tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # 配置列参数
        column_config = {
            "品种名称": {"width": 180, "anchor": tk.W},
            "品牌名称": {"width": 150, "anchor": tk.W},
            "买入价(元/克)": {"width": 120, "anchor": tk.E},
            "卖出价(元/克)": {"width": 120, "anchor": tk.E},
            "买入价(美元/盎司)": {"width": 140, "anchor": tk.E},
            "卖出价(美元/盎司)": {"width": 140, "anchor": tk.E},
            "当日最高": {"width": 110, "anchor": tk.E},
            "当日最低": {"width": 110, "anchor": tk.E},
            "涨跌幅": {"width": 90, "anchor": tk.CENTER},
            "交易状态": {"width": 80, "anchor": tk.CENTER},
            "黄金价格(元/克)": {"width": 130, "anchor": tk.E},
            "金条价格(元/克)": {"width": 130, "anchor": tk.E},
            "单位": {"width": 80, "anchor": tk.CENTER},
            "报价时间": {"width": 120, "anchor": tk.CENTER}
        }

        # 配置列属性
        for col in columns:
            cfg = column_config.get(col, {"width": 100, "anchor": tk.CENTER})
            tree.heading(col, text=col)
            tree.column(
                col,
                width=cfg["width"],
                anchor=cfg["anchor"],
                minwidth=cfg.get("minwidth", 80)
            )

        # 滚动条
        vsb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tab, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # 布局
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # 保存表格引用
        setattr(self, f"{tab_name}_tree", tree)

    def refresh_data(self):
        """刷新所有数据"""
        self.status_label.config(text="正在获取最新行情...")
        self.export_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            # 获取实时交易数据
            gold_response = requests.get("https://free.xwteam.cn/api/gold/trade", timeout=10)
            gold_data = gold_response.json()

            # 获取品牌金店数据
            brand_response = requests.get("https://api.lolimi.cn/API/huangj/api.php", timeout=10)
            brand_data = brand_response.json()

            # 处理交易数据
            if gold_data.get("code") == 200:
                self.update_market_data(gold_data["data"])
            else:
                self.show_error(f"交易数据接口异常: {gold_data.get('msg', '未知错误')}")

            # 处理品牌数据
            if brand_data.get("code") == 200:
                self.update_brand_data(brand_data["国内十大金店"])
            else:
                self.show_error(f"品牌数据接口异常: {brand_data.get('msg', '未知错误')}")

            self.status_label.config(text="数据更新成功", foreground="green")
            self.export_btn.config(state=tk.NORMAL)

        except requests.exceptions.RequestException as e:
            self.show_error(f"网络连接错误: {str(e)}")
            self.status_label.config(text="数据更新失败", foreground="red")
        except Exception as e:
            self.show_error(f"系统错误: {str(e)}")
            self.status_label.config(text="数据更新失败", foreground="red")

    def update_market_data(self, data):
        """更新市场交易数据"""
        # 国内现货行情
        self.update_trade_data("国内现货_tree", data["LF"], "元/克", data["OpenMark"])
        # 上海交易所
        self.update_trade_data("上海交易所_tree", data["SH"], "元/克", data["OpenMark"])
        # 国际市场
        self.update_trade_data("国际市场_tree", data["GJ"], "美元/盎司", data["OpenMark"])

        # 更新页脚时间
        update_time = datetime.strptime(data["UpTime"], "%Y-%m-%d %H:%M:%S")
        self.footer.config(
            text=f"数据来源：上海黄金交易所、伦敦金银市场协会、中国黄金协会 | 更新时间：{update_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def update_trade_data(self, tree_name, items, unit_prefix, market_status):
        """更新交易数据表格"""
        tree = getattr(self, tree_name)
        tree.delete(*tree.get_children())

        # 存储原始数据
        tab_name = tree_name.replace("_tree", "")
        self.current_data[tab_name] = {
            "items": items,
            "unit": unit_prefix,
            "status": market_status
        }

        for item in items:
            try:
                change_rate = ((item["SP"] - item["BP"]) / item["BP"]) * 100
            except ZeroDivisionError:
                change_rate = 0.0

            values = [
                f"{item['Name']} ({self.get_exchange_symbol(item['Symbol'])})",
                f"{item['BP']:.3f}" if unit_prefix == "元/克" else f"${item['BP']:.2f}",
                f"{item['SP']:.3f}" if unit_prefix == "元/克" else f"${item['SP']:.2f}",
                f"{item['High']:.3f}" if unit_prefix == "元/克" else f"${item['High']:.2f}",
                f"{item['Low']:.3f}" if unit_prefix == "元/克" else f"${item['Low']:.2f}",
                f"{'↑' if change_rate >=0 else '↓'}{abs(change_rate):.2f}%",
                "交易中" if market_status == 1 else "休市中"
            ]

            if "USD" in item["Symbol"]:
                values[1] = f"{item['BP']:.4f}"
                values[2] = f"{item['SP']:.4f}"

            tree.insert("", tk.END, values=values)

    def update_brand_data(self, brands):
        """更新品牌金店数据"""
        tree = self.品牌金店_tree
        tree.delete(*tree.get_children())

        # 存储原始数据
        self.current_data["品牌金店"] = brands

        for brand in brands:
            # 格式化报价时间
            try:
                report_date = datetime.strptime(brand["报价时间"], "%Y-%m-%d").strftime("%Y/%m/%d")
            except:
                report_date = brand["报价时间"]

            values = [
                brand["品牌"],
                brand["黄金价格"],
                brand["金条价格"],
                brand["单位"],
                report_date
            ]
            tree.insert("", tk.END, values=values)

    def get_exchange_symbol(self, symbol):
        """获取交易所标识"""
        exchange_map = {
            "SH_": "上金所",
            "GJ_": "LME",
            "LF_": "现货市场",
            "HKAu": "港交所",
            "AU9999JS": "珠宝行"
        }
        for prefix in exchange_map:
            if symbol.startswith(prefix):
                return exchange_map[prefix]
        return "场外市场"

    def export_data(self):
        """Excel导出功能"""
        try:
            # 检查数据是否为空
            if not any([len(v["items"]) if isinstance(v, dict) else len(v) for v in self.current_data.values()]):
                messagebox.showwarning("导出失败", "请先获取最新数据再执行导出操作")
                return

            # 弹出保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel 文件", "*.xlsx"), ("All Files", "*.*")],
                title="保存为"
            )
            if not file_path:
                return

            # 创建Excel写入器
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 导出交易数据
                for tab in ["国内现货", "上海交易所", "国际市场"]:
                    data = self.current_data[tab]
                    df = pd.DataFrame([{
                        "品种名称": item["Name"],
                        "交易所": self.get_exchange_symbol(item["Symbol"]),
                        "买入价": item["BP"],
                        "卖出价": item["SP"],
                        "最高价": item["High"],
                        "最低价": item["Low"],
                        "单位": data["unit"],
                        "交易状态": "交易中" if data["status"] == 1 else "休市中"
                    } for item in data["items"]])
                    df.to_excel(writer, sheet_name=tab, index=False)

                # 导出品牌数据
                brand_df = pd.DataFrame(self.current_data["品牌金店"])
                if not brand_df.empty:
                    brand_df["报价时间"] = pd.to_datetime(brand_df["报价时间"])
                    brand_df.to_excel(writer, sheet_name="品牌金店", index=False)

            messagebox.showinfo("导出成功", f"数据已成功导出到：\n{file_path}")
            self.status_label.config(text="导出成功", foreground="green")

        except PermissionError:
            messagebox.showerror("导出失败", "文件正在使用中，请关闭文件后重试")
        except Exception as e:
            messagebox.showerror("导出失败", f"发生未知错误：{str(e)}")

    def show_error(self, message):
        """显示错误提示"""
        messagebox.showerror(
            "系统提示",
            f"{message}\n请检查：\n1. 网络连接\n2. 接口可用性\n3. 系统时间是否正确",
            icon="warning"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = GoldPriceApp(root)
    root.mainloop()