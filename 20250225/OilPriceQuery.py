import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import re
import time
import os
from functools import lru_cache


class OilPriceCrawler:
    def __init__(self):
        self.data = []
        self.headers = ["调整时间", "92号汽油", "95号汽油", "98号汽油", "0号柴油"]
        self.url = "http://youjia.10260.com/jiangsu/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'http://youjia.10260.com/'
        })
        # 市场分析数据
        self.market_analysis = {
            'trend': "江苏市场，原油收盘下跌，但新一轮变化率正向开端，主营单位报价以稳为主，消息面指引不稳，下游接货心态谨慎，预计近日汽柴行情走势窄幅波动。",
            'sinopec': {
                'diesel': "0#车柴国Ⅵ7260元/吨",
                'gas92': "E92#汽油国Ⅵ7610元/吨",
                'gas95': "E95#汽油国Ⅵ7810元/吨",
                'discount': "汽柴可惠"
            },
            'petrochina': {
                'diesel': "0#车柴国Ⅵ7259元/吨",
                'gas92': "E92#汽油国Ⅵ8000元/吨",
                'gas95': "E95#汽油国Ⅵ8200元/吨",
                'discount': "汽柴可惠"
            }
        }

    def get_market_analysis(self):
        """生成格式化市场分析报告"""
        analysis = [
            "【市场最新动态】",
            self.market_analysis['trend'],
            "",
            "【主力单位挂牌价】",
            "中石化：",
            f"  柴油：{self.market_analysis['sinopec']['diesel']}",
            f"  92号：{self.market_analysis['sinopec']['gas92']}",
            f"  95号：{self.market_analysis['sinopec']['gas95']}",
            f"  优惠：{self.market_analysis['sinopec']['discount']}",
            "",
            "中石油：",
            f"  柴油：{self.market_analysis['petrochina']['diesel']}",
            f"  92号：{self.market_analysis['petrochina']['gas92']}",
            f"  95号：{self.market_analysis['petrochina']['gas95']}",
            f"  优惠：{self.market_analysis['petrochina']['discount']}"
        ]
        return "\n".join(analysis)


    def fetch_data(self):
        try:
            response = self.session.get(self.url, timeout=20)
            response.encoding = 'utf-8'

            # 多引擎协同解析
            table_records = self._parse_with_bs4(response.text)
            script_records = self._parse_script_data(response.text)
            fallback_records = self._parse_fallback(response.text)

            # 数据聚合与清洗
            combined = self._merge_records(table_records + script_records + fallback_records)
            self.data = [self.headers] + combined
            return True

        except Exception as e:
            messagebox.showerror("错误", f"数据获取失败: {str(e)}")
            return False


    def _parse_with_bs4(self, html):
        soup = BeautifulSoup(html, 'lxml')
        records = []

        modern_table = soup.find('table', class_=re.compile(r'price-table|data-list'))
        if modern_table:
            records.extend(self._parse_standard_table(modern_table))

        legacy_table = soup.find('table', cellpadding="3")
        if legacy_table:
            records.extend(self._parse_legacy_table(legacy_table))

        return records


    def _parse_standard_table(self, table):
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(cells) >= 5 and re.match(r'\d{4}-\d+-\d+', cells[-1]):
                rows.append(self._create_record(cells[-1], cells[:4]))
        return rows


    def _parse_legacy_table(self, table):
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all('font')]
            if len(cells) >= 5 and re.search(r'汽油|柴油', cells[0]):
                date_match = re.search(r'\d{4}-\d+-\d+', ' '.join(cells))
                if date_match:
                    rows.append(self._create_record(date_match.group(), cells[:4]))
        return rows


    def _parse_script_data(self, html):
        records = []
        pattern = re.compile(
            r'\{.*?date:\s*["\'](\d{4}-\d+-\d+)["\'].*?'
            r'(?:92|#92)[^:]*?:\s*(\d+\.\d+).*?'
            r'(?:95|#95)[^:]*?:\s*(\d+\.\d+).*?'
            r'(?:98|#98)[^:]*?:\s*(\d+\.\d+).*?'
            r'(?:0号柴油|diesel)[^:]*?:\s*(\d+\.\d+).*?\}',
            re.DOTALL
        )

        for match in re.finditer(pattern, html):
            records.append(self._create_record(match.group(1), match.groups()[1:]))

        return records


    def _parse_fallback(self, html):
        records = []
        master_pattern = re.compile(
            r'(?P<date>\d{4}-\d{1,2}-\d{1,2})[\s\S]*?'
            r'(?P<gas92>\d+\.\d+)\D+?'
            r'(?P<gas95>\d+\.\d+)\D+?'
            r'(?P<gas98>\d+\.\d+)\D+?'
            r'(?P<diesel>\d+\.\d+)',
            re.MULTILINE | re.IGNORECASE
        )

        for match in master_pattern.finditer(html):
            records.append([
                self._format_date(match.group('date')),
                match.group('gas92'),
                match.group('gas95'),
                match.group('gas98'),
                match.group('diesel')
            ])

        return records


    def _create_record(self, date_str, prices):
        date_fmt = self._format_date(date_str)
        if not date_fmt or len(prices) != 4:
            return None

        return [
            date_fmt,
            *[self._clean_price(p) for p in prices]
        ]


    @lru_cache(maxsize=100)
    def _format_date(self, date_str):
        try:
            date_str = re.sub(r'[年月]', '-', date_str)
            date_str = re.sub(r'日', '', date_str)
            parts = re.split(r'[-/]', date_str)
            if len(parts) != 3:
                return None

            year = parts[0].zfill(4)
            month = parts[1].zfill(2)
            day = parts[2].zfill(2)
            return f"{year}-{month}-{day}"
        except:
            return None


    def _clean_price(self, price_str):
        cleaned = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return f"{float(cleaned):.2f}"
        except:
            return "0.00"


    def _merge_records(self, records):
        date_map = {}
        for record in sorted(records, key=lambda x: x[0], reverse=True):
            if record and len(record) == 5:
                date = record[0]
                if date not in date_map:
                    date_map[date] = record
        return sorted(date_map.values(), key=lambda x: x[0], reverse=True)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("油价专业分析系统 v5.2")
        self.geometry("1280x900")
        self.crawler = OilPriceCrawler()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        # 主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Button(toolbar, text="刷新数据", command=self._refresh).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="导出报告", command=self._export).pack(side=tk.RIGHT)

        # 市场分析面板
        analysis_frame = ttk.LabelFrame(main_frame, text="实时市场分析")
        analysis_frame.pack(fill=tk.X, pady=5)

        self.analysis_text = tk.Text(
            analysis_frame,
            height=8,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            padx=10,
            pady=10
        )
        self.analysis_text.insert(tk.END, self.crawler.get_market_analysis())
        self.analysis_text.configure(state='disabled')
        self.analysis_text.pack(fill=tk.BOTH)

        # 数据表格
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.crawler.headers,
            show="headings",
            selectmode="extended"
        )

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        for col in self.crawler.headers:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # 状态栏
        self.status = ttk.Label(main_frame, text="系统就绪", anchor=tk.W)
        self.status.pack(fill=tk.X, pady=5)

    def _load_data(self):
        def task():
            self.status.config(text="数据采集中...")
            start = time.time()

            if self.crawler.fetch_data():
                self._display_data()
                elapsed = time.time() - start
                self.status.config(text=f"数据更新成功 | 记录数：{len(self.crawler.data) - 1} | 耗时：{elapsed:.2f}秒")
            else:
                self.status.config(text="数据加载失败")

        Thread(target=task, daemon=True).start()

    def _display_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.crawler.data[1:]:
            self.tree.insert("", tk.END, values=row)

    def _refresh(self):
        self._load_data()
        self.analysis_text.configure(state='normal')
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, self.crawler.get_market_analysis())
        self.analysis_text.configure(state='disabled')

    def _export(self):
        if len(self.crawler.data) < 2:
            messagebox.showwarning("警告", "没有可导出的数据")
            return

        try:
            # 历史价格数据
            price_df = pd.DataFrame(self.crawler.data[1:], columns=self.crawler.headers)
            price_df['调整时间'] = pd.to_datetime(price_df['调整时间'])

            # 市场分析数据
            analysis_lines = self.crawler.get_market_analysis().split('\n')
            analysis_df = pd.DataFrame({
                '分析内容': analysis_lines,
                '时间戳': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            file_path = os.path.abspath("江苏油价综合分析报告.xlsx")
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                price_df.to_excel(writer, sheet_name='历史价格', index=False)
                analysis_df.to_excel(writer, sheet_name='市场分析', index=False)

            messagebox.showinfo("导出成功",
                                f"文件已保存到：\n{file_path}\n\n"
                                f"包含：\n- 历史价格记录 {len(price_df)} 条\n"
                                f"- 市场分析条目 {len(analysis_df)} 项")
        except Exception as e:
            messagebox.showerror("导出错误", f"文件保存失败：{str(e)}")



if __name__ == "__main__":
    app = Application()
    app.mainloop()



