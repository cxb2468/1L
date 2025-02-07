import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import PyPDF2
import threading


class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Viewer")
        self.password = "8"  # 硬编码密码
        self.mouse_position = (0, 0)  # 初始化鼠标位置

        # 创建密码输入对话框
        self.password_dialog = simpledialog.askstring("Password", "Enter password:", show="*")
        if self.password_dialog != self.password:
            messagebox.showerror("Error", "Incorrect password!")
            self.root.destroy()
            return

        # 创建按钮
        self.open_button = tk.Button(root, text="Choose a PDF file", command=self.choose_pdf)
        self.open_button.pack(pady=10)

        # 创建滚动文本框
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)
        self.text_area.pack(padx=10, pady=10)

        # 创建进度标签
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=5)

        # 创建鼠标位置标签
        # self.mouse_label = tk.Label(root, text=f"Mouse Position: ({self.mouse_position[0]}, {self.mouse_position[1]})")
        # self.mouse_label.pack(pady=5)

        # 创建遮罩层
        self.mask = tk.Frame(root, bg="white")  # white
        self.mask.place(relwidth=0, relheight=0)  # 初始位置不覆盖任何区域
        self.mask.place_forget()  # 初始隐藏遮罩层

        # 绑定鼠标移动事件
        self.root.bind("<Motion>", self.update_mouse_position)
        self.root.bind("<Leave>", self.show_mask)  # 鼠标离开窗口时显示遮罩
        self.root.bind("<Enter>", self.hide_mask)  # 鼠标进入窗口时隐藏遮罩

    def choose_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")],  # 只允许选择PDF文件
            title="Choose a PDF file"
        )
        if file_path:  # 如果用户选择了文件
            self.load_pdf_in_thread(file_path)

    def load_pdf_in_thread(self, pdf_path):
        # 启动新线程加载PDF文件
        threading.Thread(target=self.open_pdf, args=(pdf_path,), daemon=True).start()
        self.progress_label.config(text="Loading PDF...")

    def open_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)

                self.text_area.delete('1.0', tk.END)  # 清除之前的内容

                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    self.text_area.insert(tk.END, text)
                    self.text_area.insert(tk.END, '\n' + '=' * 40 + '\n')  # 页面之间的分隔符

                    # 使用after方法从线程更新GUI
                    self.root.after(0, self.update_progress_label, f"Page {page_num + 1}/{num_pages} loaded")

            self.root.after(0, self.progress_label.config, {'text': ""})

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, self.progress_label.config, {'text': ""})

    def update_progress_label(self, text):
        self.progress_label.config(text=text)

    def update_mouse_position(self, event):
        self.mouse_position = (event.x, event.y)
        # self.mouse_label.config(text=f"Mouse Position: ({self.mouse_position[0]}, {self.mouse_position[1]})")

        # 更新遮罩层位置和大小
        if self.mask.winfo_ismapped():  # 如果遮罩层可见
            self.mask.place(relx=0, rely=0, relwidth=1, relheight=1)  # 根据PDF预览区域调整遮罩层

    def show_mask(self, event):
        self.mask.place(relx=0, rely=0, relwidth=1, relheight=1)  # 覆盖PDF预览区域

    def hide_mask(self, event):
        self.mask.place_forget()  #


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()