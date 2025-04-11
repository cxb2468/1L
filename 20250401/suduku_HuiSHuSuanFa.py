def solve_sudoku(board):
    """
    解数独的优化回溯算法
    :param board: 9x9二维列表，0表示空格
    :return: 解后的数独矩阵（修改原列表）
    """
    def get_candidates(row, col):
        """获取(row, col)位置的候选数"""
        candidates = set(range(1, 10))
        # 去除同行、同列、同九宫格的已填数字
        for i in range(9):
            if board[row][i] in candidates:
                candidates.remove(board[row][i])
            if board[i][col] in candidates:
                candidates.remove(board[i][col])
        # 处理九宫格
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] in candidates:
                    candidates.discard(board[i][j])
        return candidates

    def find_next_cell():
        """找到候选数最少的空格（启发式选择）"""
        min_candidates = None
        min_row, min_col = -1, -1
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    candidates = get_candidates(row, col)
                    if min_candidates is None or len(candidates) < len(min_candidates):
                        min_candidates = candidates
                        min_row, min_col = row, col
                    # 若候选数为0，直接返回（死路）
                    if not candidates:
                        return (row, col)
        return (min_row, min_col) if min_row != -1 else (-1, -1)

    def solve():
        row, col = find_next_cell()
        if row == -1 and col == -1:
            return True  # 全部填满，成功
        if not get_candidates(row, col):  # 无候选数，失败
            return False
        # 递归尝试候选数
        for num in get_candidates(row, col):
            board[row][col] = num
            if solve():
                return True
            board[row][col] = 0  # 回溯
        return False

    return solve()

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

# 求解并输出结果
if solve_sudoku(unsolved):
    for row in unsolved:
        print(row)
else:
    print("无解！")