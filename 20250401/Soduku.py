from PIL import ImageGrab, ImageOps, ImageEnhance, Image, ImageFilter
import pytesseract
import numpy as np
import pyautogui
import time
import tkinter as tk
from threading import Thread
from functools import wraps
import cv2
import os  # 新增：导入os模块


# 网址 https://sudoku.com/

# 计时装饰器
def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 高精度计时
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"[{func.__name__}] 执行时间: {elapsed:.4f} 秒")
        return result, elapsed  # 返回结果和执行时间

    return wrapper


# 带计时功能的屏幕识别
@timer_decorator
def capture_and_recognize(left, top, right, bottom):
    width = right - left
    height = bottom - top

    # 截取屏幕
    screen = ImageGrab.grab(bbox=(left, top, right, bottom))

    # 保存截图到当前目录
    screen.save("captured_screen.png")  # 新增：保存截图

    # 初始化数独矩阵
    sudoku = np.zeros((9, 9), dtype=int)

    cell_width = width / 9
    cell_height = height / 9

    # 设置TESSDATA_PREFIX环境变量
    tessdata_dir = r'D:\Program Files\Tesseract-OCR\tessdata'  # 确保路径正确
    os.environ['TESSDATA_PREFIX'] = tessdata_dir  # 新增：设置环境变量

    for row in range(9):
        for col in range(9):
            # 截取单个格子
            box = (
                col * cell_width + 4,
                row * cell_height + 4,
                (col + 1) * cell_width - 4,
                (row + 1) * cell_height - 4,
            )
            cell = screen.crop(box)

            # 图像预处理
            cell = ImageOps.grayscale(cell)
            cell = ImageEnhance.Contrast(cell).enhance(2.0)
            cell = cell.point(lambda x: 0 if x < 200 else 255)

            # OCR识别
            text = pytesseract.image_to_string(
                cell,
                config="--psm 8 --oem 3 -c tessedit_char_whitelist=123456789 ",
                # lang="num"
            )
            sudoku[row][col] = int(text) if text.strip() else 0
    print(sudoku)
    return sudoku


# 带计时功能的数独求解
@timer_decorator
def solve_sudoku(board):
    def is_valid(row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def backtrack():
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(row, col, num):
                            board[row][col] = num
                            if backtrack():
                                return True
                            board[row][col] = 0
                    return False
        return True

    backtrack()
    return board


def auto_fill(original, solution, left, top, right, bottom):
    base_x, base_y = left, top
    cell_width = (right - left) / 9
    cell_height = (bottom - top) / 9

    for row in range(9):
        for col in range(9):
            if original[row][col] == 0:
                num = solution[row][col]
                x = base_x + col * cell_width + cell_width / 2
                y = base_y + row * cell_height + cell_height / 2

                pyautogui.click(x, y)
                pyautogui.typewrite(str(num))
                time.sleep(0.1)


class SudokuSolverGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sudoku Solver")

        # 添加输入框和标签
        tk.Label(self.window, text="Left:").grid(row=0, column=0, padx=10, pady=5)
        self.left_entry = tk.Entry(self.window)
        self.left_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.window, text="Top:").grid(row=1, column=0, padx=10, pady=5)
        self.top_entry = tk.Entry(self.window)
        self.top_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.window, text="Right:").grid(row=2, column=0, padx=10, pady=5)
        self.right_entry = tk.Entry(self.window)
        self.right_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.window, text="Bottom:").grid(row=3, column=0, padx=10, pady=5)
        self.bottom_entry = tk.Entry(self.window)
        self.bottom_entry.grid(row=3, column=1, padx=10, pady=5)

        self.btn = tk.Button(
            self.window,
            text="Start",
            command=self.start_solving,
            font=("Arial", 14),
            width=15,
            height=2,
        )
        self.btn.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

        # 初始化默认值
        self.left_entry.insert(0, "356")
        self.top_entry.insert(0, "326")
        self.right_entry.insert(0, "933")
        self.bottom_entry.insert(0, "903")

    def start_solving(self):
        print("Start capture_and_recognize")
        Thread(target=self.solve_process).start()

    def solve_process(self):
        # 获取用户输入的坐标
        left = int(self.left_entry.get())
        top = int(self.top_entry.get())
        right = int(self.right_entry.get())
        bottom = int(self.bottom_entry.get())

        # 获取识别结果和执行时间
        original, recognize_time = capture_and_recognize(left, top, right, bottom)

        # 获取求解结果和执行时间
        solution, solve_time = solve_sudoku(original.copy())

        # 打印详细耗时
        print(f"\n性能统计:")
        print(f"屏幕识别耗时: {recognize_time:.4f}s")
        print(f"数独求解耗时: {solve_time:.4f}s")
        print(f"总耗时: {recognize_time + solve_time:.4f}s\n\n")

        auto_fill(original, solution, left, top, right, bottom)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = SudokuSolverGUI()
    gui.run()