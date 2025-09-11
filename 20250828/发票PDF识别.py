import pdfplumber
import pandas as pd
import openpyxl
import tkinter as tk
import datetime
from tkinter import filedialog
import os
import re
from pdfplumber.utils import rect_to_edges


class ExtraInfo():
    def invoice_info(self, pdf_folder):
        data = []
        for filename in os.listdir(pdf_folder):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, filename)
                with pdfplumber.open(pdf_path) as pdf:
                    first_page = pdf.pages[0]
                    text_old = first_page.extract_text()
                    text = text_old.replace("（", "(").replace("）", ")").replace("：", ":").replace("￥", "&#165;")
                    text_area_product = first_page.crop(bbox=(12, 144, 178, 270)).extract_text()
                    print("正在处理 " + pdf_path + " 文件")
                    product_no_tab = text_area_product.replace("\n", "")
                    invoice_name = filename
                    pattern_product = re.compile(r"(\*.*)(合\x20?计)").search(product_no_tab)
                    # print(pattern_product)
                    pattern_invoice_kind = re.compile(r"\w+发票\x20?(\(\w+发票\))?").search(text)
                    pattern_name_1 = re.compile(r"(名\x20?称:\x20?)(\w{2,})").findall(text)
                    pattern_name_2 = re.compile(r"(\b[\u4e00-\u9fa5+公司]\b)").findall(text)
                    pattern_invoice_code = re.compile(r"[发票|票据|开票代码]\s?:\s?(\d+)").search(text)
                    pattern_invoice_number = re.compile(r"[发票|票据|开票号码]\s?:\s?(\d+)?").search(text)
                    pattern_all_number = re.compile(r"\d{5,}").findall(text)
                    pattern_invoice_date = re.compile(
                        r"[开票|订单日期：\x20?(20\d{2})\x20?年\x20?(\d{2})\x20?月\x20?(\d{2})\x20?日]")
                    pattern_invoice_date_1 = re.compile(r"(20\d{2})\x20?年\x20?(\d{2})\x20?月\x20?(\d{2})\x20?日")
                    pattern_invoice_date_2 = re.compile(r"(20\d{2})\x20(\d{2})\x20(\d{2})")
                    pattern_taxpayer_number_1 = re.compile(r"(纳税人识别号:\x20?)([0-9A-Z]{18})").findall(text)
                    pattern_taxpayer_number_2 = re.compile(r"\b([0-9A-Z]{18})\b").findall(text)
                    # 优化金额和税额的正则表达式，增加更多匹配模式
                    pattern_money = re.compile(r"(?:合\s*计|金\s*额)\s*[:：]?\s*&#165;?\s*(\d+\.\d{2})").search(text)
                    pattern_tax = re.compile(r"(?:税\s*额|税\s*额\s*合计)\s*[:：]?\s*&#165;?\s*(\d+\.\d{2})").search(text)
                    pattern_total_money = re.compile(r"(?:价税合计|小写金额|总金额)\s*[:：]?\s*&#165;?\s*(\d+\.\d{2})").search(text)
                    # 改进税率提取正则表达式
                    pattern_tax_rate = re.compile(r"(?:税率|税\s*率)\s*[:：]?\s*(\d+%)|不征税").search(text)
                    # invoice_stuff = re.compile(r"(\*[\u4e00-\u9fa5]+\*[\s\S]*)(合\s?计\s?[￥&#165;]\d+\.\d{2})").findall(text)
                    invoice_stuff = re.compile(
                        r"(\*[\u4e00-\u9fa5+\*[\s\S]*)((合\x20?计\x20)?&#165;(\d+\.\d{2}))").findall(text)
                    if pattern_invoice_kind:
                        invoice_kind = pattern_invoice_kind.group()
                    else:
                        invoice_kind = ""
                    if pattern_name_1:
                        try:
                            supplier = pattern_name_1[-1][1]
                        except IndexError:
                            supplier = ""
                        try:
                            customer = pattern_name_1[0][1]
                        except IndexError:
                            customer = ""
                    elif pattern_name_2:
                        try:
                            supplier = pattern_name_2[-1]
                        except IndexError:
                            supplier = ""
                        try:
                            customer = pattern_name_2[-2]
                        except IndexError:
                            customer = ""
                    else:
                        supplier = ""
                        customer = ""
                    if pattern_invoice_code:
                        invoice_code = pattern_invoice_code.group(1)
                    elif re.search(r"[开票|发票|票据代码]", text):
                        try:
                            invoice_code = pattern_all_number[0]
                        except IndexError:
                            invoice_code = ""
                    else:
                        invoice_code = ""
                    if pattern_invoice_number:
                        invoice_number = pattern_invoice_number.group(1)
                    elif re.search(r"[开票|发票|票据号码]", text):
                        try:
                            invoice_number = pattern_all_number[1]
                        except IndexError:
                            invoice_number = ""
                    else:
                        invoice_number = ""
                    match_date = None
                    if pattern_invoice_date.search(text):
                        match_date = pattern_invoice_date.search(text)
                    elif pattern_invoice_date_1.search(text):
                        match_date = pattern_invoice_date_1.search(text)
                    elif pattern_invoice_date_2.search(text):
                        match_date = pattern_invoice_date_2.search(text)
                    else:
                        match_date = None
                    if match_date:
                        try:
                            # 安全地提取日期组，防止IndexError
                            groups = match_date.groups()
                            if len(groups) >= 3:
                                invoice_date = groups[0] + "年" + groups[1] + "月" + groups[2] + "日"
                            else:
                                invoice_date = ""
                        except (IndexError, AttributeError):
                            invoice_date = ""
                    else:
                        invoice_date = ""
                    if pattern_taxpayer_number_1:
                        try:
                            supplier_number = pattern_taxpayer_number_1[-1][1]
                        except IndexError:
                            supplier_number = ""
                        try:
                            customer_number = pattern_taxpayer_number_1[0][1]
                        except IndexError:
                            customer_number = ""
                    elif pattern_taxpayer_number_2:
                        try:
                            supplier_number = pattern_taxpayer_number_2[-1]
                        except IndexError:
                            supplier_number = ""
                        try:
                            customer_number = pattern_taxpayer_number_2[-2]
                        except IndexError:
                            customer_number = ""
                    else:
                        supplier_number = ""
                        customer_number = ""
                    
                    # 优化金额和税额提取逻辑
                    if pattern_money:
                        money = pattern_money.group(1)
                    else:
                        # 尝试其他方式提取金额合计
                        money_match = re.search(r"(?:合\s*计|金\s*额)[:：]?\s*￥?\s*(\d+\.?\d*)", text)
                        money = money_match.group(1) if money_match else ""
                        
                    if pattern_tax:
                        tax = pattern_tax.group(1)
                    else:
                        # 尝试其他方式提取税额
                        tax_match = re.search(r"(?:税\s*额|税\s*额\s*合计)[:：]?\s*￥?\s*(\d+\.?\d*)", text)
                        tax = tax_match.group(1) if tax_match else ""
                        
                    # 如果没有单独提取到税额，尝试从pattern_money中提取
                    if not tax and pattern_money:
                        tax = pattern_money.group(1)
                        
                    if pattern_tax_rate:
                        tax_rate = pattern_tax_rate.group(1) if pattern_tax_rate.group(1) else pattern_tax_rate.group()
                    else:
                        # 尝试其他方式提取税率
                        tax_rate_match = re.search(r"(?:税率|税\s*率)[:：]?\s*(\d+(?:\.\d+)?%)", text)
                        tax_rate = tax_rate_match.group(1) if tax_rate_match else ""
                        
                    if pattern_total_money:
                        total_money = pattern_total_money.group(1)
                    else:
                        # 尝试其他方式提取价税合计
                        total_money_match = re.search(r"(?:价税合计|小写金额|总金额)[:：]?\s*￥?\s*(\d+\.?\d*)", text)
                        total_money = total_money_match.group(1) if total_money_match else ""
                        
                    if pattern_product:
                        product = pattern_product.group(1)
                    else:
                        product = ""

                    data.append({
                        "文件名称": filename,
                        "发票类别": invoice_kind,
                        "发票号码": invoice_number,
                        "发票代码": invoice_code,
                        "开票日期": invoice_date,
                        "购买方名称": customer,
                        "购买方纳税人识别号": customer_number,
                        "税率": tax_rate,
                        "金额合计": money,
                        "税额合计": tax,
                        "价税合计": total_money,
                        "销售方名称": supplier,
                        "销售方纳税人识别号": supplier_number,
                        "商品": product
                    })
        return data

    def pdf_to_excel(self, output_excel, pdf_folder):
        data = self.invoice_info(pdf_folder)
        df = pd.DataFrame(data)
        df.to_excel(output_excel, index=False)


class PopUp():
    def __init__(self) -> None:
        self.folder_path = ""
        self.save_path = ""
        self.root = tk.Tk()
        self.folder_label = tk.Label(self.root, text="请选择PDF文件夹")
        self.folder_label.pack(padx=5, pady=5)
        self.save_label = tk.Label(self.root, text="请选择保存位置")
        self.save_label.pack(padx=5, pady=5)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=f"PDF文件夹: {self.folder_path}")

    def browse_save(self):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
        default_filename = f"PdfInvoice{formatted_datetime}.xlsx"
        self.save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")]
        )
        if self.save_path:
            self.save_label.config(text=f"保存位置: {self.save_path}")

    def pop_up(self):
        self.root.title("发票统计专用V1.0 2025-04-10")
        self.root.geometry("500x200")

        browse_button = tk.Button(self.root, text="选择PDF文件夹", command=self.browse_folder)
        browse_button.pack(padx=5, pady=5)

        save_button = tk.Button(self.root, text="选择保存位置", command=self.browse_save)
        save_button.pack(padx=5, pady=5)
        upload_button = tk.Button(self.root, text="开始处理", command=self.root.destroy)
        upload_button.pack(padx=5, pady=5)

        self.root.mainloop()
        return self.folder_path, self.save_path


if __name__ == '__main__':
    pop = PopUp()
    dir, save_path = pop.pop_up()

    if dir and save_path:
        extra = ExtraInfo()
        extra.pdf_to_excel(save_path, dir)
    else:
        print("未选择文件夹或保存位置,程序退出")