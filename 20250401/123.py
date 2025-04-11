
# 使用DLX算法替代回溯法（需安装dlxsudoku）
from dlxsudoku import Sudoku

def solve_sudoku(board):
    sudoku = Sudoku(board.tolist())
    sudoku.solve()
    return np.array(sudoku.board)













from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
)
from PyQt5.QtCore import QTimer
import sys


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

        # 按钮布局
        self.button_layout = QVBoxLayout()

        # 数字按钮 1-9
        self.number_buttons = []
        for num in range(1, 10):
            btn = QPushButton(str(num))
            btn.setFixedSize(50, 50)
            btn.clicked.connect(lambda _, n=num: self.set_number(n))
            self.number_buttons.append(btn)
            self.button_layout.addWidget(btn)

        # Start 按钮
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(100, 50)
        self.start_button.clicked.connect(self.start_timer)
        self.button_layout.addWidget(self.start_button)

        # 解答按钮
        self.solve_button = QPushButton("解答")
        self.solve_button.setFixedSize(100, 50)
        self.solve_button.clicked.connect(self.solve_sudoku)
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

    def set_number(self, number):
        """设置当前选中单元格的数字"""
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].hasFocus():
                    self.cells[row][col].setText(str(number))

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
