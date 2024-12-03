import tkinter as tk
from tkinter import filedialog, ttk
import threading
import pdfplumber
import openpyxl
from openpyxl import Workbook
import sys

from PIL import Image, ImageTk


def extract_tables(pdf, ws, progress_var, total_pages, base_progress=0, progress_step=1):
    for i, page in enumerate(pdf.pages):
        if page.extract_tables():
            for table in page.extract_tables():
                for row in table:
                    ws.append(row)
        current_progress = base_progress + (i + 1) / total_pages * progress_step
        progress_var.set(current_progress)


def extract_images(pdf, images_folder, progress_var, total_pages, base_progress=0, progress_step=1, pdf_filename=''):
    for i, page in enumerate(pdf.pages):
        for image_index, image in enumerate(page.images):
            x0, top, x1, bottom = image["x0"], image["top"], image["x1"], image["bottom"]
            cropped_image = page.within_bbox((x0, top, x1, bottom))
            if cropped_image:
                img = cropped_image.to_image(resolution=300)
                img_filename = f"{images_folder}/{pdf_filename}_page_{i + 1}_{image_index + 1}.png"

                img.save(img_filename)
                print(img_filename)
        current_progress = base_progress + (i + 1) / total_pages * progress_step
        print(current_progress)


def extract_from_pdf(pdf_paths, excel_path, images_folder, progress_var, status_var, extract_tables_var,
                     extract_images_var):
    try:
        total_pdfs = len(pdf_paths)
        progress_step = 100 / total_pdfs
        for j, pdf_path in enumerate(pdf_paths):
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

                if extract_tables_var.get() == 1:
                    wb = Workbook()
                    ws = wb.active
                    extract_tables(pdf, ws, progress_var, total_pages, base_progress=j * progress_step,
                                   progress_step=progress_step)
                    wb.save(excel_path.replace('.xlsx', f'_{j + 1}.xlsx'))

                if extract_images_var.get() == 1:
                    pdf_filename = pdf_path.split("/")[-1].replace('.pdf', '')
                    extract_images(pdf, images_folder, progress_var, total_pages, base_progress=j * progress_step,
                                   progress_step=progress_step, pdf_filename=pdf_filename)

        print("提取完成！")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        progress_var.set(0)


def open_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if file_paths:
        pdf_paths_var.set(list(file_paths))
        print(f'已选择{file_paths}作为PDF文件来处理！！！')


def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        excel_path_var.set(file_path)
        print(f'已选择{file_path}作为Excel文件的保存表格!!!')


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        images_folder_var.set(folder_path)
        print(f'已选择{folder_path}作为图片文件保存位置！！！')


def run_extraction():
    pdf_paths = pdf_paths_var.get()
    excel_path = excel_path_var.get()
    images_folder = images_folder_var.get()
    pdf_paths = eval(pdf_paths)

    if pdf_paths and (excel_path or images_folder):
        print("正在提取...")
        threading.Thread(target=extract_from_pdf, args=(
        pdf_paths, excel_path, images_folder, progress_var, status_var, extract_tables_var, extract_images_var)).start()


def print_to_display(content):
    display_box.insert(tk.END, content + '\n')
    display_box.see(tk.END)


# 创建主窗口
root = tk.Tk()

root.title("PDF 表格与图片提取器")

x_1 = int(root.winfo_screenwidth() / 3 - root.winfo_reqwidth() / 3)
y_1 = int(root.winfo_screenheight() / 3 - root.winfo_reqheight() / 3)

root.geometry(f"680x480+{x_1}+{y_1}")
root.configure(bg='#F5F5F5')

try:
    background_image = Image.open("background_data_1.png")
    background_image = background_image.resize((700, 480), Image.Resampling.LANCZOS)
    background_image = ImageTk.PhotoImage(background_image)
    canvas_main_bank = tk.Canvas(root, width=700, height=480)
    canvas_main_bank.pack(fill="both", expand=True)
    canvas_main_bank.create_image(0, 0, image=background_image, anchor="nw")
except:
    pass

title_label = tk.Label(root, text="PDF 表格与图片提取器", font=("Arial", 18))
title_label.place(x=230, y=5)

pdf_paths_var = tk.StringVar()
excel_path_var = tk.StringVar()
images_folder_var = tk.StringVar()
status_var = tk.StringVar()
progress_var = tk.DoubleVar()
extract_tables_var = tk.IntVar(value=1)
extract_images_var = tk.IntVar(value=1)

# 选择PDF文件:
label_pdf = tk.Label(root, text="选择PDF文件:")
label_pdf.place(x=60, y=60)  # 假设 x=10, y=5 作为起始点

pdf_entry = tk.Entry(root, textvariable=pdf_paths_var, width=50)
pdf_entry.place(x=180, y=60)  # 假设 x=100 作为输入框的起始点

button_browse = tk.Button(root, text="浏览", command=open_files)
button_browse.place(x=540, y=60)  # 假设 x=220 作为按钮的起始点

# 保存为Excel文件:
label_excel = tk.Label(root, text="保存为Excel文件:")
label_excel.place(x=60, y=100)  # y 坐标增加，以适应新行

excel_entry = tk.Entry(root, textvariable=excel_path_var, width=50)
excel_entry.place(x=180, y=100)

button_save = tk.Button(root, text="浏览", command=save_file)
button_save.place(x=540, y=100)

# 选择图片保存文件夹:
label_folder = tk.Label(root, text="选择图片保存文件夹:")
label_folder.place(x=60, y=140)

images_entry = tk.Entry(root, textvariable=images_folder_var, width=50)
images_entry.place(x=180, y=140)

button_select = tk.Button(root, text="浏览", command=select_folder)
button_select.place(x=540, y=140)

# 提取选项
check_tables = tk.Checkbutton(root, text="提取表格", variable=extract_tables_var)
check_tables.place(x=160, y=180)

check_images = tk.Checkbutton(root, text="提取图片", variable=extract_images_var)
check_images.place(x=260, y=180)

# 开始提取按钮
button_start = tk.Button(root, text="开始提取", command=run_extraction, bg="green")
button_start.place(x=400, y=180)  # 根据需要调整位置

status_label = tk.Label(root, textvariable=status_var)
status_label.place(x=200, y=220)

# 进度条
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.place(x=200, y=220, width=280)  # 假设宽度为280

# 滚动条
scrollbar = tk.Scrollbar(root)
scrollbar.place(x=560, y=260, relheight=0.33, anchor=tk.N)
# 文本输出框
display_box = tk.Text(root, yscrollcommand=scrollbar.set, height=12, width=70, bd=0)
display_box.place(x=60, y=260)

scrollbar.config(command=display_box.yview)

root.mainloop()