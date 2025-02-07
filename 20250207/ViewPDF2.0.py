import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import threading
import fitz
from PIL import Image, ImageTk
import io


class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Viewer")
        self.password = "8"  # 硬编码密码
        self.mouse_position = (0, 0)
        self.image_references = []  # 保存图片引用防止被回收

        # 密码验证
        self.password_dialog = simpledialog.askstring("Password", "Enter password:", show="*")
        if self.password_dialog != self.password:
            messagebox.showerror("Error", "Incorrect password!")
            self.root.destroy()
            return

        # 界面组件
        self.open_button = tk.Button(root, text="Choose a PDF file", command=self.choose_pdf)
        self.open_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15)
        self.text_area.pack(padx=10, pady=10)

        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=5)

        # 遮罩层
        self.mask = tk.Frame(root, bg="white")
        self.mask.place(relwidth=0, relheight=0)
        self.mask.place_forget()

        # 事件绑定
        self.root.bind("<Motion>", self.update_mouse_position)
        self.root.bind("<Leave>", self.show_mask)
        self.root.bind("<Enter>", self.hide_mask)

    def choose_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")],
            title="Choose a PDF file"
        )
        if file_path:
            self.load_pdf_in_thread(file_path)

    def load_pdf_in_thread(self, pdf_path):
        threading.Thread(target=self.open_pdf, args=(pdf_path,), daemon=True).start()
        self.progress_label.config(text="Loading PDF...")

    def open_pdf(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            num_pages = len(doc)

            # 清空之前的内容和图片引用
            self.root.after(0, self.clear_content)

            for page_num in range(num_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                images = self.extract_images_from_page(doc, page)

                # 将当前页内容添加到GUI
                self.root.after(0, self.insert_page_content, text, images)
                self.root.after(0, self.update_progress_label, f"Page {page_num + 1}/{num_pages} loaded")

            self.root.after(0, self.progress_label.config, {'text': ""})
            doc.close()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, self.progress_label.config, {'text': ""})

    def extract_images_from_page(self, doc, page):
        images = []
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]

            # 转换图像尺寸
            pil_image = Image.open(io.BytesIO(image_data))
            pil_image.thumbnail((400, 400))  # 调整图片尺寸
            tk_image = ImageTk.PhotoImage(pil_image)
            images.append(tk_image)
        return images

    def clear_content(self):
        self.text_area.delete('1.0', tk.END)
        self.image_references.clear()

    def insert_page_content(self, text, images):
        self.text_area.insert(tk.END, text + "\n")
        for img in images:
            self.image_references.append(img)  # 保持引用
            self.text_area.image_create(tk.END, image=img)
            self.text_area.insert(tk.END, "\n")
        self.text_area.insert(tk.END, "\n" + "=" * 60 + "\n\n")
        self.text_area.see(tk.END)  # 滚动到最新内容

    def update_progress_label(self, text):
        self.progress_label.config(text=text)

    def update_mouse_position(self, event):
        self.mouse_position = (event.x, event.y)
        if self.mask.winfo_ismapped():
            self.mask.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_mask(self, event):
        self.mask.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide_mask(self, event):
        self.mask.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()