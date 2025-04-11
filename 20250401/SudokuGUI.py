from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
)
from PyQt5.QtCore import QTimer, Qt
import sys

# 示例：定义一个未解的数独题目
unsolved = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

class SudokuGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数独游戏")
        self.setGeometry(100, 100, 600, 600)

        # 主布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # 数独网格
        self.grid_layout = QGridLayout()
        self.cells = [[QLineEdit() for _ in range(9)] for _ in range(9)]
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.setFixedSize(50, 50)
                cell.setAlignment(Qt.AlignCenter)
                cell.setMaxLength(1)
                self.grid_layout.addWidget(cell, row, col)
        self.layout.addLayout(self.grid_layout)

        # 初始化数独题目
        self.load_sudoku(unsolved)

        # 按钮布局
        self.button_layout = QVBoxLayout()

        # 增加一个文本框用于显示按钮的返回值
        self.result_label = QLabel("点击按钮显示返回值")
        self.result_label.setFixedSize(200, 50)
        self.button_layout.addWidget(self.result_label)

        # 数字按钮 1-9
        self.number_buttons = []
        number_grid = QGridLayout()  # 创建一个新的网格布局用于数字按钮
        numbers = [(0, 0, 1), (0, 1, 2), (0, 2, 3),
                   (1, 0, 4), (1, 1, 5), (1, 2, 6),
                   (2, 0, 7), (2, 1, 8), (2, 2, 9)]
        for row, col, num in numbers:
            btn = QPushButton(str(num))
            btn.setFixedSize(50, 50)
            btn.clicked.connect(lambda _, n=num: self.set_number(n))
            self.number_buttons.append(btn)
            number_grid.addWidget(btn, row, col)

        self.button_layout.addLayout(number_grid)  # 将数字按钮网格布局添加到主按钮布局中

        # Start 按钮
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(100, 50)
        self.start_button.clicked.connect(lambda: self.on_button_click("Start"))
        self.button_layout.addWidget(self.start_button)

        # 重置按钮
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedSize(100, 50)
        self.reset_button.clicked.connect(lambda: self.on_button_click("重置"))
        self.button_layout.addWidget(self.reset_button)

        # 解答按钮
        self.solve_button = QPushButton("解答")
        self.solve_button.setFixedSize(100, 50)
        self.solve_button.clicked.connect(lambda: self.on_button_click("解答"))
        self.button_layout.addWidget(self.solve_button)

        # 计时器标签
        self.timer_label = QLabel("时间: 00:00")
        self.timer_label.setFixedSize(100, 50)
        self.button_layout.addWidget(self.timer_label)

        self.layout.addLayout(self.button_layout)

        # 初始化计时器
        self.timer = QTimer()
        self.elapsed_time = 0
        self.timer.timeout.connect(self.update_timer)

    def load_sudoku(self, board):
        """加载数独题目"""
        for row in range(9):
            for col in range(9):
                if board[row][col] != 0:
                    self.cells[row][col].setText(str(board[row][col]))
                    self.cells[row][col].setReadOnly(True)  # 设置为只读，防止修改初始题目
                else:
                    self.cells[row][col].clear()
                    self.cells[row][col].setReadOnly(False)  # 清除并设置为可编辑

    def on_button_click(self, button_name):
        """处理按钮点击事件并显示返回值"""
        self.result_label.setText(f"点击了 {button_name} 按钮")

    def set_number(self, number):
        """设置当前选中单元格的数字"""
        cell_found = False  # 标记是否找到聚焦的单元格
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].hasFocus():
                    if not self.cells[row][col].isReadOnly():  # 确保单元格不是只读的
                        self.cells[row][col].setText(str(number))
                        self.result_label.setText(f"在 ({row}, {col}) 设置了数字 {number}")
                        cell_found = True
                    break
        if not cell_found:
            self.result_label.setText("未选中任何单元格，请先点击一个单元格")

    def start_timer(self):
        """启动计时器"""
        self.elapsed_time = 0
        self.timer.start(1000)  # 每秒触发一次

    def update_timer(self):
        """更新计时器显示"""
        self.elapsed_time += 1
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        self.timer_label.setText(f"时间: {minutes:02}:{seconds:02}")

    def reset_sudoku(self):
        """重置数独题目到初始状态"""
        self.load_sudoku(unsolved)

    def solve_sudoku(self):
        """调用数独求解算法并回填结果"""
        board = [[int(cell.text()) if cell.text() else 0 for cell in row] for row in self.cells]
        solution = self.solve_sudoku_algorithm(board)
        if solution:
            for row in range(9):
                for col in range(9):
                    self.cells[row][col].setText(str(solution[row][col]))

    def solve_sudoku_algorithm(self, board):
        """数独求解算法（简单实现）"""
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

        if backtrack():
            return board
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SudokuGUI()
    window.show()
    sys.exit(app.exec_())