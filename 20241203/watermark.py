import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import time


def add_watermark(source_image_path, watermark_path, output_folder_path, position, opacity, watermark_scale_percent):
    try:
        # 获取原始图片文件名（包含扩展名）
        source_image_name = os.path.basename(source_image_path)
        file_name, file_extension = os.path.splitext(source_image_name)

        # 构建输出文件名，在原始文件名后添加_时间戳后缀
        # 获取当前时间的时间元组
        current_time = time.localtime()
        # 将时间元组格式化为字符串，比如 20241202103000 这样的格式（表示2024年12月2日10时30分0秒）
        time_str = time.strftime("%Y%m%d%H%M%S", current_time)
        output_image_name = file_name + "_" + time_str + file_extension

        # 构建完整的输出文件路径
        output_path = os.path.join(output_folder_path, output_image_name)

        # 打开原始图片
        image = Image.open(source_image_path)
        image_width, image_height = image.size

        # 打开水印图片并确保其为RGBA模式
        watermark_image = Image.open(watermark_path)
        if watermark_image.mode != 'RGBA':
            watermark_image = watermark_image.convert('RGBA')
        watermark_width, watermark_height = watermark_image.size

        scale_percent = watermark_scale_percent / 100  # 将百分比转换为小数
        new_watermark_width = int(watermark_width * scale_percent)
        new_watermark_height = int(watermark_height * scale_percent)
        resized_watermark = watermark_image.resize((new_watermark_width, new_watermark_height))
        print(f"水印图片已缩放到: {new_watermark_width}x{new_watermark_height} 像素")

        # 根据选择的位置调整水印位置
        if position == "左上":
            paste_position = (0, 0)
        elif position == "右上":
            paste_position = (image_width - new_watermark_width, 0)
        elif position == "左下":
            paste_position = (0, image_height - new_watermark_height)
        elif position == "右下":
            paste_position = (image_width - new_watermark_width, image_height - new_watermark_height)
        else:
            paste_position = (0, 0)

        # 处理透明度
        try:
            if opacity < 100:
                alpha = resized_watermark.split()[3]
                alpha = alpha.point(lambda p: p * opacity // 100)
                resized_watermark.putalpha(alpha)
        except Exception as e:
            print("Error in transparency processing:", e)
            messagebox.showerror("透明度处理错误", "在处理透明度时出现错误，请检查水印图像。")

        # 添加水印
        image.paste(resized_watermark, paste_position, resized_watermark)

        # 保存结果图片
        image.save(output_path, quality=85)  # 压缩质量为85%
        print(f"保存添加水印后的图片到: {output_path}")
        messagebox.showinfo("完成", "水印已成功添加！")
    except Exception as e:
        print("Error in adding watermark:", e)
        messagebox.showerror("错误", "发生错误: " + str(e))


def browse_source_image():
    file_selected = filedialog.askopenfilename()
    if file_selected:
        source_image_entry.delete(0, tk.END)
        source_image_entry.insert(0, file_selected)
        apply_watermark_preview()


def browse_watermark_image():
    file_selected = filedialog.askopenfilename()
    if file_selected:
        watermark_entry.delete(0, tk.END)
        watermark_entry.insert(0, file_selected)
        watermark_image = preprocess_watermark_image(file_selected)
        if watermark_image:
            apply_watermark_preview()


def browse_output_image():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_selected)


def add_watermark_process():
    source_image_path = source_image_entry.get()
    watermark_path = watermark_entry.get()
    output_folder_path = output_entry.get()
    position = position_var.get()
    opacity = opacity_var.get().rstrip('%')
    opacity = int(opacity)
    watermark_scale_percent = scale_var.get().rstrip('%')
    watermark_scale_percent = int(watermark_scale_percent)

    if not source_image_path or not watermark_path or not output_folder_path:
        messagebox.showwarning("警告", "请确保所有字段都已填写。")
        return

    add_watermark(source_image_path, watermark_path, output_folder_path, position, opacity, watermark_scale_percent)


def apply_watermark_preview():
    source_image_path = source_image_entry.get()
    watermark_path = watermark_entry.get()
    position = position_var.get()
    opacity = opacity_var.get().rstrip('%')
    opacity = int(opacity)
    watermark_scale_percent = scale_var.get().rstrip('%')
    watermark_scale_percent = int(watermark_scale_percent)

    if not source_image_path or not watermark_path:
        return

    # 创建加载弹窗
    loading_window = tk.Toplevel(root)
    loading_window.title("加载中")
    loading_window.geometry("50x50")
    loading_label = tk.Label(loading_window, text="正在生成水印预览，请稍候...")
    loading_label.pack(pady=10)
    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=150, mode="indeterminate",
                                   variable=progress_var)
    progress_bar.pack(pady=5)
    progress_bar.start(10)  # 启动进度条动画，这里设置每10毫秒更新一次

    root.update_idletasks()  # 立即更新界面，确保加载弹窗显示出来

    try:
        # 打开原始图片
        source_image = Image.open(source_image_path)
        source_width, source_height = source_image.size

        # 打开水印图片并确保其为RGBA模式
        watermark_image = Image.open(watermark_path)
        if watermark_image.mode != 'RGBA':
            watermark_image = watermark_image.convert('RGBA')
        watermark_width, watermark_height = watermark_image.size

        scale_percent = watermark_scale_percent / 100
        new_watermark_width = int(watermark_width * scale_percent)
        new_watermark_height = int(watermark_height * scale_percent)
        resized_watermark = watermark_image.resize((new_watermark_width, new_watermark_height))

        # 处理透明度
        try:
            if opacity < 100:
                alpha = resized_watermark.split()[3]
                alpha = alpha.point(lambda p: p * opacity // 100)
                resized_watermark.putalpha(alpha)
        except Exception as e:
            print("Error in transparency processing:", e)
            messagebox.showerror("透明度处理错误", "在处理透明度时出现错误，请检查水印图像。")

        # 根据选择的位置调整水印位置
        if position == "左上":
            paste_position = (0, 0)
        elif position == "右上":
            paste_position = (source_width - new_watermark_width, 0)
        elif position == "左下":
            paste_position = (0, source_height - new_watermark_height)
        elif position == "右下":
            paste_position = (source_width - new_watermark_width, source_height - new_watermark_height)
        else:
            paste_position = (0, 0)

        # 创建带有水印的预览图像
        preview_image = source_image.copy()
        preview_image.paste(resized_watermark, paste_position, resized_watermark)

        # 设置固定的预览框尺寸
        target_width = 300
        target_height = 250

        # 获取原始图片宽高比
        width_ratio = preview_image.width / target_width
        height_ratio = preview_image.height / target_height

        # 根据宽高比计算缩放后的尺寸，保持图片比例不变
        if width_ratio > height_ratio:
            new_width = target_width
            new_height = int(preview_image.height / width_ratio)
        else:
            new_height = target_height
            new_width = int(preview_image.width / height_ratio)

        # 缩放图片
        preview_image = preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 计算在预览框中居中显示的偏移量
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2

        # 创建一个新的白色背景的图片（尺寸为预览框大小）
        final_preview_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        final_preview_image.paste(preview_image, (offset_x, offset_y))

        # 转换为Tkinter可以显示的格式
        preview_photo = ImageTk.PhotoImage(final_preview_image)
        preview_canvas.create_image(0, 0, anchor='nw', image=preview_photo)
        preview_canvas.image = preview_photo

        # 关闭加载弹窗
        loading_window.destroy()
    except Exception as e:
        print("Error in preview:", e)
        messagebox.showerror("预览错误", "无法显示水印预览: " + str(e))
        # 如果出现错误也关闭加载弹窗
        loading_window.destroy()


def on_position_change(event):
    apply_watermark_preview()


def on_opacity_change(event):
    apply_watermark_preview()


def on_scale_change(event):
    apply_watermark_preview()


def preprocess_watermark_image(watermark_path):
    try:
        watermark_image = Image.open(watermark_path)
        if watermark_image.mode != 'RGBA':
            watermark_image = watermark_image.convert('RGBA')
        # 可以添加更多的预处理操作，如检查图像数据完整性等
        return watermark_image
    except Exception as e:
        print("Error in preprocessing watermark image:", e)
        messagebox.showerror("水印图像预处理错误", "在处理水印图像时出现错误，请选择正确的水印图像。")
        return None


def about():
    messagebox.showinfo("关于", "这是一个简单的用python制作的添加水印工具。\nBy：52破解小林子Vip\n版本: 1.0")


def exit_app():
    root.quit()


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    root.title("水印添加工具 By：小林子Vip")
    root.geometry("500x700")
    root.resizable(False, False)

    # 设置主窗口居中
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 待加水印图片选择
source_image_frame = tk.Frame(root)
source_image_frame.pack(pady=10, padx=20, fill="x")

source_image_label = tk.Label(source_image_frame, text="待加水印图片:")
source_image_label.pack(side="left")

source_image_entry = tk.Entry(source_image_frame, width=40)
source_image_entry.pack(side="left", padx=5)

source_image_browse_button = tk.Button(source_image_frame, text="浏览", command=browse_source_image)
source_image_browse_button.pack(side="left")

# 水印图片选择
watermark_frame = tk.Frame(root)
watermark_frame.pack(pady=10, padx=20, fill="x")

watermark_label = tk.Label(watermark_frame, text="水印图片:")
watermark_label.pack(side="left")

watermark_entry = tk.Entry(watermark_frame, width=40)
watermark_entry.pack(side="left", padx=5)

watermark_browse_button = tk.Button(watermark_frame, text="浏览", command=browse_watermark_image)
watermark_browse_button.pack(side="left")

# 输出图片选择
output_frame = tk.Frame(root)
output_frame.pack(pady=10, padx=20, fill="x")

output_label = tk.Label(output_frame, text="输出文件夹:")
output_label.pack(side="left")

output_entry = tk.Entry(output_frame, width=40)
output_entry.pack(side="left", padx=5)

output_browse_button = tk.Button(output_frame, text="浏览", command=browse_output_image)
output_browse_button.pack(side="left")

# 水印位置选择
position_frame = tk.Frame(root)
position_frame.pack(pady=10, padx=20, fill="x")

position_label = tk.Label(position_frame, text="水印位置:")
position_label.pack(side="left")

position_var = tk.StringVar()
position_option = ttk.Combobox(
    position_frame,
    textvariable=position_var,
    values=["左上", "右上", "左下", "右下"],
    width=10,
    state="readonly",
)
position_option.current(0)
position_option.pack(side="left", padx=5)
position_option.bind("<<ComboboxSelected>>", on_position_change)

# 水印透明度选择
opacity_frame = tk.Frame(root)
opacity_frame.pack(pady=10, padx=20, fill="x")

opacity_label = tk.Label(opacity_frame, text="水印透明度:")
opacity_label.pack(side="left")

opacity_var = tk.StringVar()
opacity_option = ttk.Combobox(
    opacity_frame,
    textvariable=opacity_var,
    values=["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"],
    width=10,
    state="readonly",
)
opacity_option.current(10)  # 默认选择100%
opacity_option.pack(side="left", padx=5)
opacity_option.bind("<<ComboboxSelected>>", on_opacity_change)

# 水印缩放比例选择
scale_frame = tk.Frame(root)
scale_frame.pack(pady=10, padx=20, fill="x")

scale_label = tk.Label(scale_frame, text="水印缩放比例:")
scale_label.pack(side="left")

scale_var = tk.StringVar()
scale_option = ttk.Combobox(
    scale_frame,
    textvariable=scale_var,
    values=["3%", "5%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "150%", "200%", "250%",
            "300%"],
    width=10,
    state="readonly",
)
scale_option.current(2)  # 默认选择10%
scale_option.pack(side="left", padx=5)
scale_option.bind("<<ComboboxSelected>>", on_scale_change)

# 添加进度条
progress_frame = tk.Frame(root)
progress_frame.pack(pady=10, padx=20, fill="x")

progress_label = tk.Label(progress_frame, text="处理进度:")
progress_label.pack(side="left")

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(
    progress_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var
)
progress_bar.pack(side="left", padx=5)

# 添加水印预览区域
preview_frame = tk.Frame(root)
preview_frame.pack(pady=10, padx=20, fill="x")

preview_label = tk.Label(preview_frame, text="水印预览:")
preview_label.pack(side="left")

preview_canvas = tk.Canvas(preview_frame, width=300, height=250, bg="white")
preview_canvas.pack(side="left", padx=5)

# 开始添加水印按钮
start_button = tk.Button(root, text="开始添加水印", command=add_watermark_process)
start_button.pack(pady=20)

# 创建菜单栏
menu_bar = tk.Menu(root)

# 文件菜单
"""
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="打开待加水印图片", command=browse_source_image)
file_menu.add_command(label="选择水印图片", command=browse_watermark_image)
file_menu.add_command(label="选择输出文件夹", command=browse_output_image)
file_menu.add_separator()
file_menu.add_command(label="退出", command=exit_app)
menu_bar.add_cascade(label="文件", menu=file_menu)
"""
# 关于菜单
about_menu = tk.Menu(menu_bar, tearoff=0)
about_menu.add_command(label="关于本工具", command=about)
menu_bar.add_cascade(label="关于", menu=about_menu)

# 将菜单栏配置到根窗口上
root.config(menu=menu_bar)

# 运行主循环
root.mainloop()