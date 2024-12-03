import os
import re
import xlwt
import base64
import requests
import tkinter as tk
import configparser
import pyperclip
import time
import sys
from tkinter import filedialog, messagebox
from tkinter.font import Font
from tkinter import ttk  # 导入ttk模块，用于创建表格
from send2trash import send2trash
import glob
import shutil
from tkinter.ttk import Progressbar
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 全局变量，存储 API 和 SECRET 键
API_KEY = ""
SECRET_KEY = ""

# 全局变量，存储表格窗口
table_window = None
table_view = None
tree = None
global root
config_filename = 'config.ini'
rename_rules = {}
selected_fields = []
global_data = []
folder_path = None
# 全局变量，存储发票张数和价税合计总额
invoice_count = 0
total_amount = 0.0
label_invoice_count = None
label_total_amount = None
# 全局变量，存储目录路径显示标签
label_folder_path = None
global stop_requested
global file_processed_count
stop_requested = False


def main():
    global API_KEY, SECRET_KEY, selected_fields, root, label_invoice_count, label_total_amount
    global folder_path  # 确保声明folder_path为全局变量
    API_KEY, SECRET_KEY, selected_fields = load_config()
    root = tk.Tk()
    root.title('发票数据处理程序')

    # 计算窗口大小为屏幕大小的60%
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.6)
    window_height = int(screen_height * 0.6)

    # 计算窗口居中的位置坐标
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)

    # 设置窗口的初始大小和位置
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # 第一段：设置按钮和打开文件夹按钮
    # 设置按钮和打开文件夹按钮的容器
    top_buttons_frame = tk.Frame(root)
    top_buttons_frame.pack(fill='x', padx=20, pady=5)

    # "设置"按钮对齐容器左侧
    btn_settings = tk.Button(top_buttons_frame, text='设置', command=open_settings)
    btn_settings.pack(side=tk.LEFT, padx=5, fill='y')

    # 中间的弹性空间，使用一个不可见的Frame
    spacer_frame = tk.Frame(top_buttons_frame)
    spacer_frame.pack(side=tk.LEFT, expand=True, fill='both')

    # 在 "选择文件夹" 按钮左边添加一个标签用于显示选择的文件夹路径
    global label_folder_path
    label_folder_path = tk.Label(top_buttons_frame, text='请选择文件夹', fg='blue')
    label_folder_path.pack(side=tk.LEFT, padx=(0, 10))

    # "选择文件夹"按钮对齐容器右侧
    btn_open_folder = tk.Button(top_buttons_frame, text='选择文件夹', command=open_folder)
    btn_open_folder.pack(side=tk.RIGHT, fill='y')
    # 第二段：创建表格窗口的地方
    invoice_table_frame = tk.LabelFrame(root, text="发票数据")
    invoice_table_frame.pack(fill="both", expand="yes", padx=20)

    # 创建表格
    setup_tree_view(invoice_table_frame, selected_fields)

    # 总计信息框架
    total_info_frame = tk.Frame(root)
    total_info_frame.pack(fill='x', padx=20, pady=5)

    label_invoice_count = tk.Label(total_info_frame, text="发票张数: 0")
    label_invoice_count.pack(side=tk.LEFT, padx=10)

    label_total_amount = tk.Label(total_info_frame, text="价税合计总额: 0.00")
    label_total_amount.pack(side=tk.LEFT, padx=10)

    # 管理数据的按钮容器
    data_management_frame = tk.Frame(root)
    data_management_frame.pack(fill='x', padx=20, pady=5)

    # 查找重复发票按钮
    add_find_duplicates_button(data_management_frame)
    btn_rename_files = tk.Button(data_management_frame, text='重命名文件', command=lambda: rename_files(tree))
    btn_rename_files.pack(side=tk.LEFT, padx=5)
    # “打开当前文件夹”按钮对齐容器右侧
    btn_open_current_folder = tk.Button(data_management_frame, text='打开当前文件夹', command=open_current_folder)
    btn_open_current_folder.pack(side=tk.LEFT, padx=(0, 5), fill='y')  # 注意左边界距设置为0，靠近上一个按钮
    # “复制总金额” 按钮
    btn_copy_total_amount = tk.Button(data_management_frame, text='复制总金额', command=copy_total_amount_to_clipboard)
    btn_copy_total_amount.pack(side=tk.LEFT, padx=10)

    btn_export_all = tk.Button(data_management_frame, text='导出所有数据',
                               command=lambda: export_data(tree, selected_only=False))
    btn_export_all.pack(side=tk.LEFT, padx=5)

    # 开始提取按钮的容器
    start_extraction_frame = tk.Frame(root)
    start_extraction_frame.pack(fill='x', padx=20, pady=5)

    btn_start_extraction = tk.Button(start_extraction_frame, text='开始提取', command=lambda: start_extraction(tree))
    btn_start_extraction.pack(side=tk.RIGHT, padx=5)

    root.mainloop()


def find_duplicates(tree):
    global global_data
    # 用于储存已经处理过的发票号码
    processed_invoices = set()
    # 用于储存重复的发票条目
    duplicates = []

    for row_data in global_data:
        invoice_num = row_data[selected_fields.index('发票号码')]

        if invoice_num in processed_invoices:
            duplicates.append(row_data)
        else:
            processed_invoices.add(invoice_num)

    if duplicates:
        show_duplicates(duplicates)
    else:
        messagebox.showinfo("完成", "没有发现重复的发票。")


def delete_selected_duplicates(duplicates_tree, duplicates_window, new_folder_name='重复的发票'):
    global global_data, invoice_count, total_amount
    selected_items = duplicates_tree.selection()

    rows_to_remove = []
    files_to_move = []

    for item in selected_items:
        item_data = duplicates_tree.item(item, "values")
        rows_to_remove.append(list(item_data))

        # 添加文件路径到列表中
        files_to_move.append(item_data[-1])

        # 获取待处理的文件的第一个，获取其路径，并在这个路径的基础目录下创建新的文件夹
    file_path_first = files_to_move[0]
    directory = os.path.dirname(file_path_first)
    new_folder = os.path.join(directory, new_folder_name)

    # 如果新文件夹不存在，则创建新文件夹
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    # 将发票文件移至新文件夹
    for file_path in files_to_move:
        try:
            # 将所有的 \ 替换为 /
            file_path = file_path.replace('\\', '/')

            # 定义新的文件路径
            new_path = os.path.join(new_folder, os.path.basename(file_path))

            # 移动文件到新的文件路径
            shutil.move(file_path, new_path)
        except Exception as e:
            print(f"无法移动文件 {file_path}到 {new_path}：{str(e)}")
            continue
    # 删除内存中的发票数据并更新UI
    for row in rows_to_remove:
        global_data = [data_row for data_row in global_data if data_row != row]
        for item in tree.get_children():
            if list(tree.item(item, "values")) == row:
                tree.delete(item)
                break  # 匹配后退出循环

    invoice_count = len(global_data)
    total_amount = sum(
        float(row[selected_fields.index('价税合计')]) for row in global_data if row[selected_fields.index('价税合计')])

    # 刷新界面上的发票张数和价税合计总额
    update_total_info()

    # 关闭弹出窗口
    duplicates_window.destroy()

    # 显示删除完成的提示信息
    messagebox.showinfo("删除成功", "选中的重复发票已经删除。")


def export_selected_duplicates(duplicates_tree):
    selected_items = duplicates_tree.selection()
    data_to_export = [duplicates_tree.item(item, 'values') for item in selected_items]

    if not data_to_export:
        messagebox.showwarning("警告", "没有选中的重复发票来导出！")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".xls")
    if output_file:
        extract_data_to_excel(output_file, data_to_export)


# 显示重复发票并提供操作的函数
def show_duplicates(duplicates):
    duplicates_window = tk.Toplevel()
    duplicates_window.title("重复发票列表")

    # 创建树形视图
    duplicates_tree = ttk.Treeview(duplicates_window, columns=tree['columns'], show='headings')

    # 为树形视图创建滚动条
    scrollbar = ttk.Scrollbar(duplicates_window, orient="vertical", command=duplicates_tree.yview)
    duplicates_tree.configure(yscrollcommand=scrollbar.set)

    # 将滚动条放置在树形视图的右侧
    scrollbar.pack(side="right", fill="y")

    # 将树形视图本身放置在窗口的顶部
    duplicates_tree.pack(side="top", fill="both", expand=True)

    for col in tree['columns']:
        duplicates_tree.heading(col, text=col)
        duplicates_tree.column(col, width=tk.font.Font().measure(col.title()))

    # 插入重复发票数据到树形视图
    for row_data in duplicates:
        duplicates_tree.insert("", "end", values=row_data)

    # 创建一个新框架放置在树形视图下方用来存放操作按钮
    buttons_frame = tk.Frame(duplicates_window)
    buttons_frame.pack(fill='x', pady=5)

    btn_delete_selected = tk.Button(buttons_frame, text="删除选中的重复发票",
                                    command=lambda: delete_selected_duplicates(duplicates_tree, duplicates_window))
    btn_delete_selected.pack(side=tk.LEFT, padx=5)

    btn_export_selected = tk.Button(buttons_frame, text="导出选中的重复发票",
                                    command=lambda: export_selected_duplicates(duplicates_tree))
    btn_export_selected.pack(side=tk.LEFT, padx=5)

    # 设置窗口居中
    center_window(duplicates_window)
    # 在指定的控件框架内添加新按钮


def add_find_duplicates_button(frame):
    btn_find_duplicates = tk.Button(frame, text='查找重复发票', command=lambda: find_duplicates(tree))
    btn_find_duplicates.pack(side=tk.LEFT, padx=5)


def center_window(win):
    # 窗口更新，以便获取准确的窗口大小信息
    win.update_idletasks()
    # 获取屏幕宽度和高度
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    # 获取窗口的尺寸和位置
    width = win.winfo_width()
    height = win.winfo_height()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    # 设置窗口的位置
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def update_total_info():
    global invoice_count, total_amount, label_invoice_count, label_total_amount
    label_invoice_count.config(text=f"发票张数: {invoice_count}")
    label_total_amount.config(text=f"价税合计总额: {total_amount:.2f}")


def open_file(event):
    item = tree.selection()[0]
    filepath = tree.item(item, "values")[-1]  # 文件路径在最后一列
    os.startfile(filepath)  # 使用默认应用打开文件


def setup_tree_view(container, selected_fields):
    global tree

    columns = tuple(selected_fields) + ('文件路径',)

    tree = ttk.Treeview(container, columns=columns, show='headings')
    tree.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")

    tree.configure(yscrollcommand=scrollbar.set)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=tk.font.Font().measure(col.title()))
    tree.bind("<Double-1>", open_file)

    # 创建右键菜单
    menu = tk.Menu(tree, tearoff=0)
    menu.add_command(label="重命名", command=lambda: rename_files(tree))  # 重命名命令
    menu.add_command(label="导出", command=lambda: export_data(tree))  # 导出命令
    menu.add_command(label="删除", command=lambda: delete_item(tree))  # 删除命令

    # 在treeview上绑定右键菜单
    def popup(event):
        menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", popup)


# delete_item函数可能看起来类似于这样
def delete_item(tree):
    global invoice_count, total_amount, global_data
    selected_items = tree.selection()
    for item in selected_items:
        # 从TreeView项目获取数据
        row_data = tree.item(item, 'values')
        # 迭代global_data寻找匹配的列表项
        for data_row in global_data:
            if all(data == row for data, row in zip(data_row, row_data)):
                # 如果找到了匹配的项，从global_data中移除
                global_data.remove(data_row)
                break  # 匹配后退出循环
        # 移除TreeView中的项
        tree.delete(item)
        invoice_count -= 1
        try:
            # 更新总金额
            total_amount -= float(row_data[selected_fields.index('价税合计')])
        except ValueError as e:
            messagebox.showerror("错误", f"在更新总金额时发生错误: {e}")

    # 刷新界面上的发票张数和价税合计总额
    update_total_info()


def save_config(api_key, secret_key):
    config = configparser.ConfigParser()
    # 先读取原有的配置
    config.read(config_filename)
    # 在原有配置基础上，更新或创建新的section
    if 'API_Keys' not in config.sections():
        config.add_section('API_Keys')
    config.set('API_Keys', 'API_KEY', api_key)
    config.set('API_Keys', 'SECRET_KEY', secret_key)

    with open(config_filename, 'w') as configfile:
        config.write(configfile)


def load_config():
    global API_KEY, SECRET_KEY, selected_fields
    config = configparser.ConfigParser()
    config.read(config_filename)
    API_KEY = config['DEFAULT'].get('API_KEY', '')
    SECRET_KEY = config['DEFAULT'].get('SECRET_KEY', '')

    # 检查配置是否含有 FIELDS section，并读取选中的字段
    if 'FIELDS' in config and 'selected_fields' in config['FIELDS']:
        selected_fields = [field.strip() for field in config['FIELDS']['selected_fields'].split(',') if field]
    else:
        # 如果没有 FIELDS 部分或没有selected_fields，设为默认字段
        selected_fields = [
            '发票号码', '数电票号', '发票种类', '货物名称', '规格型号', '单位',
            '数量', '单价', '税率', '价税合计', '销售方名称',
            '销售方税号', '购买方名称', '购买方税号', '开票日期', '消费类型'
        ]

    return API_KEY, SECRET_KEY, selected_fields


# 新增函数，用于保存ABBREVIATIONS到配置文件中
def save_abbreviations(entries, config_section, config):
    abbreviations = ','.join(f"{full.get()}:{abbr.get()}" for full, abbr in entries if full.get() and abbr.get())
    if not config.has_section('ABBREVIATIONS'):
        config.add_section('ABBREVIATIONS')
    config.set('ABBREVIATIONS', config_section, abbreviations)
    with open(config_filename, 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("成功", f"{config_section.capitalize()} 简称设置已保存。")


def create_abbreviation_setting_frame(container, title, count):
    frame = tk.LabelFrame(container, text=title)
    frame.pack(fill='x', expand=True, padx=10, pady=5)
    entries = []
    for _ in range(count):
        entry_frame = tk.Frame(frame)
        entry_frame.pack(fill='x', expand=True)
        tk.Label(entry_frame, text='原文').pack(side='left', padx=5)
        full = tk.Entry(entry_frame)
        full.pack(side='left', padx=5, fill='x', expand=True)
        tk.Label(entry_frame, text='简称').pack(side='left', padx=5)
        abbr = tk.Entry(entry_frame)
        abbr.pack(side='left', padx=5, fill='x', expand=True)
        entries.append((full, abbr))
    return entries


def load_abbreviations(config_section, config, entries):
    if config.has_option('ABBREVIATIONS', config_section):
        abbreviations = config.get('ABBREVIATIONS', config_section)
        abbreviation_pairs = (pair.split(':') for pair in abbreviations.split(',') if ':' in pair)
        # 请先清空所有输入框
        for full_entry, abbr_entry in entries:
            full_entry.delete(0, tk.END)
            abbr_entry.delete(0, tk.END)
        # 之后再插入新数据
        for (full, abbr), (full_entry, abbr_entry) in zip(abbreviation_pairs, entries):
            full_entry.insert(0, full)
            abbr_entry.insert(0, abbr)


def insert_field_into_entry(entry, field):
    current_text = entry.get()
    field_placeholder = "{" + field + "}"
    # 如果当前已经有文本，加入空格后再添加字段占位符
    if current_text:
        field_placeholder = "_" + field_placeholder
    entry.insert(tk.END, field_placeholder)


# 保存配置文件中的规则
def save_rename_rule(entry_widget):
    rule = entry_widget.get()
    config = configparser.ConfigParser()
    config.read(config_filename)
    config['RenameRule'] = {'rule': rule}
    with open(config_filename, 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo('保存成功', '字段重命名规则已保存至 config.ini。')


# 读取配置文件以获取规则
def load_rename_rule(entry_widget):
    config = configparser.ConfigParser()
    config.read(config_filename)  # 读取配置文件
    if 'RenameRule' in config and 'rule' in config['RenameRule']:
        entry_widget.insert(0, config['RenameRule']['rule'])  # 将读取的规则设置在 entry_widget 中


def rename_files(tree):
    rename_window = tk.Toplevel()
    rename_window.title('重命名文件设置')
    all_fieldnames = [
        '发票号码', '数电票号', '发票种类', '货物名称', '规格型号', '单位',
        '数量', '单价', '税率', '价税合计', '销售方名称',
        '销售方税号', '购买方名称', '购买方税号', '开票日期', '消费类型'
    ]

    config = configparser.ConfigParser()
    config.read(config_filename)

    seller_entries = create_abbreviation_setting_frame(rename_window, "销售方简称设置", 5)
    btn_save_seller = tk.Button(rename_window, text='保存销售方简称设置',
                                command=lambda: save_abbreviations(seller_entries, 'seller', config))
    btn_save_seller.pack(pady=5)
    buyer_entries = create_abbreviation_setting_frame(rename_window, "购买方简称设置", 5)

    # 加载已保存的设置
    load_abbreviations('seller', config, seller_entries)
    load_abbreviations('buyer', config, buyer_entries)

    btn_save_buyer = tk.Button(rename_window, text='保存购买方简称设置',
                               command=lambda: save_abbreviations(buyer_entries, 'buyer', config))
    btn_save_buyer.pack(pady=5)

    # 重命名规则设置的框架
    frame_rename_rule = tk.LabelFrame(rename_window, text="文件重命名规则", padx=5, pady=5)
    frame_rename_rule.pack(padx=10, pady=10, fill="x")

    label_rename_rule = tk.Label(frame_rename_rule, text='设置重命名模板:')
    label_rename_rule.grid(row=0, column=0, sticky='w')

    entry_rename_rule = tk.Entry(frame_rename_rule)
    entry_rename_rule.grid(row=0, column=1, sticky='ew')

    # 创建一个包含两行的字段按钮框架
    fields_frame = tk.Frame(frame_rename_rule)
    fields_frame.grid(row=1, column=0, columnspan=2, pady=5)

    # 分配按钮到两行
    half_length = len(all_fieldnames) // 2

    # 上半部分的按钮
    top_fields_frame = tk.Frame(fields_frame)
    top_fields_frame.pack(fill='x')
    for field in all_fieldnames[:half_length]:
        btn_field = tk.Button(top_fields_frame, text=field,
                              command=lambda f=field: insert_field_into_entry(entry_rename_rule, f))
        btn_field.pack(side=tk.LEFT, padx=2, pady=2)

    # 下半部分的按钮
    bottom_fields_frame = tk.Frame(fields_frame)
    bottom_fields_frame.pack(fill='x')
    for field in all_fieldnames[half_length:]:
        btn_field = tk.Button(bottom_fields_frame, text=field,
                              command=lambda f=field: insert_field_into_entry(entry_rename_rule, f))
        btn_field.pack(side=tk.LEFT, padx=2, pady=2)

    # Load和Save按钮
    frame_buttons = tk.Frame(frame_rename_rule)
    frame_buttons.grid(row=2, column=0, columnspan=2, pady=5)

    # 保存规则按钮
    save_rule_button = tk.Button(frame_rename_rule, text="保存规则", command=lambda: save_rename_rule(entry_rename_rule))
    save_rule_button.grid(row=2, column=0, columnspan=2, pady=5)

    # 在这里自动加载规则到entry_rename_rule
    load_rename_rule(entry_rename_rule)

    # Expand entry widget to fill the frame's width
    frame_rename_rule.columnconfigure(1, weight=1)

    btn_rename = tk.Button(rename_window, text='确认重命名',
                           command=lambda: perform_rename(tree, entry_rename_rule.get(), config))
    btn_rename.pack(pady=10)

    center_window(rename_window)
    rename_window.grab_set()
    rename_window.wait_window()


def get_abbreviations_dict(config_section, config):
    abbreviations_dict = {}
    if config.has_option('ABBREVIATIONS', config_section):
        abbreviations = config.get('ABBREVIATIONS', config_section)
        splits = (pair.split(':') for pair in abbreviations.split(',') if ':' in pair)
        abbreviations_dict = {full: abbr for full, abbr in splits}
    return abbreviations_dict


def clean_filename(filename):
    return re.sub(r'[?|*|:|<|>|"|/|\\]', '_', filename)


def perform_rename(tree, rename_rule, config):
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("错误", "没有选中任何记录！")
        return

    # 获取简称的映射，如果没有，则返回空字典
    seller_abbreviations_dict = get_abbreviations_dict('seller', config)
    buyer_abbreviations_dict = get_abbreviations_dict('buyer', config)

    for item in selected_items:
        # 获取选择项中的数据，包括文件路径
        item_data = list(tree.item(item, 'values'))  # 转换成 list
        invoice_data = dict(zip(selected_fields, item_data[:-1]))  # 最后一个值是文件路径，需要分开处理
        old_file_path = item_data[-1]  # 取得文件路径
        file_extension = os.path.splitext(old_file_path)[1]

        if '销售方名称' in invoice_data:
            invoice_data['销售方名称'] = seller_abbreviations_dict.get(invoice_data['销售方名称'], invoice_data['销售方名称'])
        if '购买方名称' in invoice_data:
            invoice_data['购买方名称'] = buyer_abbreviations_dict.get(invoice_data['购买方名称'], invoice_data['购买方名称'])

        try:
            new_filename = rename_rule.format(**invoice_data) + file_extension
            new_filename = clean_filename(new_filename)  # 清理文件名
        except KeyError as e:
            messagebox.showerror("错误", f"重命名规则有误: 无法识别的字段 {e}")
            continue

        new_file_path = os.path.join(os.path.dirname(old_file_path), new_filename)
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
        else:
            messagebox.showerror("错误", f"文件 {old_file_path} 不存在。")
            continue

        item_data[-1] = new_file_path  # 更新文件路径
        tree.item(item, values=tuple(item_data))  # 更新树形的项目

    messagebox.showinfo("成功", "所选文件已重命名完成。")


def open_folder():
    global folder_path, label_folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        # 选定文件夹后，更新标签显示为 "当前目录：路径"
        label_folder_path.config(text="当前目录：" + folder_path)
        print("Selected folder: " + folder_path)
    else:
        # 未选择文件夹，显示 "请选择目录"
        label_folder_path.config(text="请选择目录")


def extract_data_to_excel(output_file, data):
    global selected_fields, invoice_count, total_amount

    print(f"创建输出文件: {output_file}")

    # 创建 workbook 和 sheet
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('发票数据')

    # 写入标题到表格
    for col, fieldname in enumerate(selected_fields + ['文件路径']):
        worksheet.write(0, col, fieldname)
    print("Excel表格创建成功")

    # 写入行数据到Excel
    for row_num, row in enumerate(data, 1):
        for col_num, cell_value in enumerate(row):
            worksheet.write(row_num, col_num, cell_value)

    # 写入总计的信息到最后一行的前四个单元格
    last_row_index = len(data) + 2
    worksheet.write(last_row_index, 0, "发票张数")
    worksheet.write(last_row_index, 1, invoice_count)
    worksheet.write(last_row_index, 2, "金额总计")
    worksheet.write(last_row_index, 3, total_amount)

    # 保存工作簿
    workbook.save(output_file)
    print(f"工作簿已保存至：{output_file}")
    messagebox.showinfo("完成", "发票数据已成功提取到Excel文件中。")


def copy_total_amount_to_clipboard():
    pyperclip.copy(f"{total_amount:.2f}")


def export_data(tree, selected_only=False):
    print("开始导出...")
    if not global_data:
        print("没有需要导出的数据！")
        return

    # 只导出选中的记录
    if selected_only:
        selected_items = tree.selection()
        if not selected_items:
            print("没有选中的项目可以导出！")
            return
        data_to_export = [tree.item(item)['values'] for item in selected_items]
    # 导出所有记录
    else:
        data_to_export = global_data

        # 使用价税合计总额作为默认文件名
    default_filename = f"发票总额_{total_amount:.2f}.xls"
    # 转换为安全的文件名（移除任何可能导致问题的字符）
    default_filename = re.sub(r'[?|*|:|<|>|"|/|\\]', '_', default_filename)

    output_file = filedialog.asksaveasfilename(defaultextension=".xls", initialfile=default_filename)
    if output_file:
        extract_data_to_excel(output_file, data_to_export)


# 新的函数用来打开当前选择的目录
def open_current_folder():
    global folder_path
    if 'folder_path' in globals() and folder_path and os.path.exists(folder_path):
        if sys.platform == "win32":  # Windows
            os.startfile(folder_path)
        elif sys.platform == "darwin":  # MacOS
            subprocess.call(["open", folder_path])
        else:  # Linux and other OS
            subprocess.call(["xdg-open", folder_path])
    else:
        messagebox.showinfo("提示", "请先选择一个有效的文件夹路径。")


def process_file(file_path, root, filename, file_types, access_token):
    time.sleep(0.6)
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in file_types:
        print(f"不支持的文件类型: {filename}")
        return None, None
    print(f"正在处理文件: {filename}")
    payload, file_type = construct_payload(root, filename)
    if payload:
        print(f"成功构建payload：{file_type}")
        invoice_data = send_request(payload, file_type, access_token)
        return invoice_data, file_path
    else:
        print(f"文件 {filename} 不支持或读取文件时发生错误。")
        return None, None


def start_extraction(tree):
    global folder_path, selected_fields, global_data, invoice_count, total_amount, label_invoice_count, label_total_amount, file_processed_count
    # 重置全局数据变量和统计信息
    global_data = []  # 清空全局数据列表
    invoice_count = 0  # 重置发票计数
    total_amount = 0.0  # 重置总金额
    file_processed_count = 0

    # 更新UI显示的总计信息
    update_total_info()
    # 清空树形控件中的所有项目
    for item in tree.get_children():
        tree.delete(item)
    # 定义支持的文件类型后缀
    file_types = {
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.bmp': 'image',
        '.pdf': 'pdf_file',
        '.ofd': 'ofd_file'
    }

    print("开始提取...")
    if not folder_path:
        messagebox.showwarning("警告", "请首先选择一个文件夹!")
        print("文件夹未选择！")
        return

    print(f"选定的文件夹: {folder_path}")

    access_token = get_access_token()

    print("显示控制窗口")
    # 这里创建控制窗口
    control_window, label_processed_count = show_control_window()

    stop_requested = False  # 初始化为False
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = set()
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                print(f"提交文件 {filename} 进行处理。")

                # 在提交任务之前更新文件计数器

                future = executor.submit(process_file, os.path.join(root, filename), root, filename, file_types,
                                         access_token)
                futures.add(future)

        for future in as_completed(futures):
            invoice_data, file_path = future.result()
            if stop_requested:
                break

            if invoice_data:
                # 更新总计数据
                invoice_count += 1  # 每次找到一张发票，发票数加1
                amount = invoice_data.get('价税合计', '')
                try:
                    total_amount += float(amount)  # 试图将金额转换成浮点数并累加到总额
                except ValueError:
                    print(f"价税合计 '{amount}' 不能转换为浮点数")
                # 更新并显示总计信息
                update_total_info()
                row = [invoice_data.get(field, '') for field in selected_fields] + [file_path]
                tree.insert("", "end", values=row)
                global_data.append(row)
            else:
                print("从API获取发票数据失败。")
            # 在每次循环结束时，更新已处理文件数
            file_processed_count += 1
            print(f"文件 {filename} 处理完成。")
            update_control_window(control_window, label_processed_count)

    print("文件处理完毕，关闭控制窗口。")
    control_window.destroy()


def update_control_window(control_window, label_processed_count):
    global file_processed_count
    print(f"更新控制窗口，已处理 {file_processed_count} 个文件。")
    label_processed_count['text'] = f"已处理文件数: {file_processed_count}"
    control_window.update_idletasks()


def show_control_window():
    control_window = tk.Toplevel()
    control_window.title('提示')

    # 获取屏幕宽度和高度
    screen_width = control_window.winfo_screenwidth()
    screen_height = control_window.winfo_screenheight()

    # 设置窗口宽度和高度
    window_width = 300
    window_height = 30  # 你可能需要调整这个高度来更好地适应元素

    # 计算窗口的x和y坐标来使其居中
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    # 设置窗口的几何形状以及位置
    control_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # 创建一个frame容器，将其放置在屏幕的上方和下方，扩展以填充额外空间
    frame = tk.Frame(control_window)
    frame.pack(expand=True)  # expand选项允许frame扩展填充任何额外的空间

    label_processed_count = tk.Label(frame, text=f"已处理文件数: {file_processed_count}")
    label_processed_count.pack()  # pack without pady to center in frame

    # 更新窗口，确保所有元素都被适当的展示
    control_window.update()

    return control_window, label_processed_count


def stop_processing():
    global stop_requested, control_window
    stop_requested = True


def construct_payload(folder_path, filename):
    # 定义支持的文件类型后缀
    file_types = {
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.bmp': 'image',
        '.pdf': 'pdf_file',
        '.ofd': 'ofd_file'
    }

    # 获取文件的后缀名
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension in file_types:
        file_path = os.path.join(folder_path, filename)
        try:
            base64_content = get_file_content_as_base64(file_path)
        except Exception as e:
            print(f"读取文件 {file_path} 发生错误: {e}")
            return None, None

        # 根据文件类型构建payload
        payload_key = file_types[file_extension]
        return {payload_key: base64_content}, payload_key
    else:
        return None, None


def get_file_content_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf8")


def send_request(payload, file_type, access_token):
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice?access_token={access_token}"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        response_json = response.json()
        words_result = response_json.get('words_result', {})

        # 结合提取的发票数据
        invoice_data = {
            '发票号码': words_result.get('InvoiceNum', ''),
            '数电票号': words_result.get('InvoiceNumDigit', ''),
            '发票种类': words_result.get('InvoiceType', ''),
            '货物名称': ';'.join([item['word'] for item in words_result.get('CommodityName', [])]),
            '规格型号': ';'.join([item['word'] for item in words_result.get('CommodityType', [])]),
            '单位': ';'.join([item['word'] for item in words_result.get('CommodityUnit', [])]),
            '数量': ';'.join([item['word'] for item in words_result.get('CommodityNum', [])]),
            '单价': ';'.join([item['word'] for item in words_result.get('CommodityPrice', [])]),
            '税率': ';'.join([item['word'] for item in words_result.get('CommodityTaxRate', [])]),
            '价税合计': words_result.get('AmountInFiguers', ''),
            '销售方名称': words_result.get('SellerName', ''),
            '销售方税号': words_result.get('SellerRegisterNum', ''),
            '购买方名称': words_result.get('PurchaserName', ''),
            '购买方税号': words_result.get('PurchaserRegisterNum', ''),
            '开票日期': words_result.get('InvoiceDate', ''),
            '消费类型': words_result.get('ServiceType', ''),
        }

        return invoice_data
    else:
        print(f"Error: {response.text}")
        return None


def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json().get("access_token", None)
    else:
        print(f"Error getting access token: {response.text}")
        return None


def open_settings():
    global selected_fields  # 使用全局变量
    settings_window = tk.Toplevel()
    settings_window.title('设置')

    # 用来容纳API_KEY和SECRET_KEY的Frame
    credentials_frame = tk.Frame(settings_window)
    credentials_frame.pack(padx=5, pady=5)

    # API_KEY label and entry
    label_api_key = tk.Label(credentials_frame, text='API_KEY:')
    label_api_key.grid(row=0, column=0, sticky='w', padx=5, pady=5)

    entry_api_key = tk.Entry(credentials_frame)
    entry_api_key.insert(0, API_KEY)  # 插入 API_KEY
    entry_api_key.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

    # SECRET_KEY label and entry
    label_secret_key = tk.Label(credentials_frame, text='SECRET_KEY:')
    label_secret_key.grid(row=1, column=0, sticky='w', padx=5, pady=5)

    entry_secret_key = tk.Entry(credentials_frame)
    entry_secret_key.insert(0, SECRET_KEY)  # 插入 SECRET_KEY
    entry_secret_key.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

    # 使第二列的输入框对齐并填满横向空间
    credentials_frame.columnconfigure(1, weight=1)

    # 选择导出字段的框架，使用LabelFrame
    frame_select_fields = tk.LabelFrame(settings_window, text="选择要导出的字段", padx=5, pady=5)
    frame_select_fields.pack(padx=10, pady=10, fill='x')

    # 之前存储勾选框的Frame现在将被嵌套在LabelFrame中
    frame_fields = tk.Frame(frame_select_fields)
    frame_fields.pack()

    # 字段列表和之前保持不变
    all_fieldnames = [
        '发票号码', '数电票号', '发票种类', '货物名称', '规格型号', '单位',
        '数量', '单价', '税率', '价税合计', '销售方名称',
        '销售方税号', '购买方名称', '购买方税号', '开票日期', '消费类型'
    ]

    # 存储所有复选框变量，同之前的逻辑
    checkbox_vars = {}
    for index, field in enumerate(all_fieldnames):
        var = tk.BooleanVar(value=field in selected_fields)
        checkbox = tk.Checkbutton(frame_fields, text=field, variable=var)
        checkbox.grid(row=index // 4, column=index % 4, sticky='w')
        checkbox_vars[field] = var

    # 之前的get_selected_fields函数保持不变
    def get_selected_fields():
        return [field for field, var in checkbox_vars.items() if var.get()]

    # Save button 创建了保存按钮并定义了它的行为
    button_save_settings = tk.Button(settings_window, text='保存设置', command=lambda: save_settings(
        entry_api_key.get(), entry_secret_key.get(),
        get_selected_fields(), settings_window))
    button_save_settings.pack(pady=5)

    # 保持设置窗口在上层
    center_window(settings_window)
    settings_window.grab_set()
    settings_window.wait_window()


def save_settings(api_key, secret_key, selected_fields_, window):
    global API_KEY, SECRET_KEY, selected_fields
    API_KEY = api_key
    SECRET_KEY = secret_key
    selected_fields = selected_fields_  # 更新全局变量
    save_config(API_KEY, SECRET_KEY)

    # 获取用户选择的字段并更新配置文件
    config = configparser.ConfigParser()
    config.read(config_filename)
    config['FIELDS'] = {'selected_fields': ','.join(selected_fields)}
    with open(config_filename, 'w') as configfile:
        config.write(configfile)

    messagebox.showinfo("设置已保存", "新的 API_KEY、SECRET_KEY 和选择的字段已保存。程序将重启以应用新设置。")
    window.destroy()
    root.destroy()

    # 重新启动程序
    python = sys.executable
    os.execl(python, python, *sys.argv)


if __name__ == '__main__':
    main()