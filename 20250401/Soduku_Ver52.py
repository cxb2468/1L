from PIL import ImageGrab, ImageOps, ImageEnhance
import pytesseract
import numpy as np
import pyautogui
import time
import tkinter as tk
from threading import Thread
from functools import wraps


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
def capture_and_recognize():
    # 屏幕截图坐标
    left, top = 356, 326
    right, bottom = 933, 903
    width = right - left
    height = bottom - top

    # 截取屏幕
    screen = ImageGrab.grab(bbox=(left, top, right, bottom))

    # 初始化数独矩阵
    sudoku = np.zeros((9, 9), dtype=int)

    cell_width = width / 9
    cell_height = height / 9

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
                config="--psm 10 --oem 3 -c tessedit_char_whitelist=123456789 ",
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


def auto_fill(original, solution):
    base_x, base_y = 356, 326
    cell_width = (933 - 356) / 9
    cell_height = (903 - 326) / 9

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

        self.btn = tk.Button(
            self.window,
            text="Start",
            command=self.start_solving,
            font=("Arial", 14),
            width=15,
            height=2,
        )
        self.btn.pack(padx=20, pady=20)

    def start_solving(self):
        print("Strart capture_and_recognize")
        Thread(target=self.solve_process).start()

    # 修改后的GUI处理逻辑

    def solve_process(self):
        # 获取识别结果和执行时间
        original, recognize_time = capture_and_recognize()

        # 获取求解结果和执行时间
        solution, solve_time = solve_sudoku(original.copy())

        # 打印详细耗时
        print(f"\n性能统计:")
        print(f"屏幕识别耗时: {recognize_time:.4f}s")
        print(f"数独求解耗时: {solve_time:.4f}s")
        print(f"总耗时: {recognize_time + solve_time:.4f}s\n\n")

        auto_fill(original, solution)

    # def solve_process(self):
    #    original = capture_and_recognize()
    #    solution = solve_sudoku(original.copy())
    #    auto_fill(original, solution)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = SudokuSolverGUI()
    gui.run()