import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image


def extract_face(image_path, output_folder):
    # 加载图像
    image = cv2.imread(image_path)

    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 加载人脸检测器
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # 如果检测到人脸
    if len(faces) > 0:
        # 假设身份证上只有一个人脸，取第一个
        (x, y, w, h) = faces[0]

        # 提取人脸区域
        face = image[y:y + h, x:x + w]

        # 保存人脸图像
        face_filename = os.path.join(output_folder, os.path.basename(image_path))
        cv2.imwrite(face_filename, face)

        return True
    else:
        return False


def batch_extract_faces(input_folder, output_folder):
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有图像文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, filename)
            if extract_face(image_path, output_folder):
                print(f"Extracted face from {filename}")
            else:
                print(f"No face detected in {filename}")


def select_input_folder():
    folder = filedialog.askdirectory()
    input_folder_var.set(folder)


def select_output_folder():
    folder = filedialog.askdirectory()
    output_folder_var.set(folder)


def start_extraction():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output folders.")
        return

    batch_extract_faces(input_folder, output_folder)
    messagebox.showinfo("Done", "Face extraction completed!")


# 创建主窗口
root = tk.Tk()
root.title("身份证人像批量提取工具")

# 输入文件夹选择
input_folder_var = tk.StringVar()
tk.Label(root, text="输入文件夹:").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(root, textvariable=input_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="选择", command=select_input_folder).grid(row=0, column=2, padx=5, pady=5)

# 输出文件夹选择
output_folder_var = tk.StringVar()
tk.Label(root, text="输出文件夹:").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="选择", command=select_output_folder).grid(row=1, column=2, padx=5, pady=5)

# 开始按钮
tk.Button(root, text="开始提取", command=start_extraction).grid(row=2, column=1, padx=5, pady=20)

# 运行主循环
root.mainloop()