import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# 替换原来的 cv2.imshow 部分
import matplotlib.pyplot as plt

# 配置Tesseract路径（根据实际情况修改）
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_path):
    """图像预处理：灰度化、二值化、边缘检测"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return img, edges


def find_corners(edges):
    """寻找数独网格的四个角点"""
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, -1)
    return None


def order_points(points):
    """对角点进行排序（左上、左下、右下、右上）"""
    points = points.astype(float)
    rect = np.zeros((4, 2), dtype="float32")

    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]

    return rect


def perspective_transform(img, corners):
    """透视变换将数独网格转为正方形"""
    rect = order_points(corners)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    return warped


def extract_grid(warped):
    """将变换后的图像分割成9x9单元格"""
    height, width = warped.shape[:2]
    cell_size = (height // 9, width // 9)
    grid = []

    for i in range(9):
        row = []
        for j in range(9):
            x = j * cell_size[1]
            y = i * cell_size[0]
            cell = warped[y:y + cell_size[0], x:x + cell_size[1]]
            row.append(cell)
        grid.append(row)
    return grid, cell_size


def extract_digits(grid):
    """使用OCR提取每个单元格的数字"""
    board = [[0 for _ in range(9)] for _ in range(9)]

    for i in range(9):
        for j in range(9):
            cell = grid[i][j]
            gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # 裁剪边缘并应用自适应阈值
            coords = cv2.findNonZero(thresh)
            if coords is not None:
                x, y, w, h = cv2.boundingRect(coords)
                digit = thresh[y:y + h, x:x + w]
                digit = cv2.resize(digit, (28, 28), interpolation=cv2.INTER_AREA)
                digit = cv2.bitwise_not(digit)

                # 使用OCR识别数字
                text = pytesseract.image_to_string(digit, config='--psm 10 digits')
                if text.isdigit():
                    board[i][j] = int(text)
    return board


def solve_sudoku(board):
    """数独求解函数（回溯法）"""

    def is_valid(row, col, num):
        for x in range(9):
            if board[row][x] == num or board[x][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True

    def backtrack():
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if is_valid(i, j, num):
                            board[i][j] = num
                            if backtrack():
                                return True
                            board[i][j] = 0
                    return False
        return True

    return backtrack()


def fill_solution(image, corners, cell_size, solution):
    """将解写回原图"""
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype("arial.ttf", int(cell_size[0] * 0.7))

    rect = order_points(corners.astype(float))
    (tl, tr, br, bl) = rect

    for i in range(9):
        for j in range(9):
            original_num = original_board[i][j]
            if original_num == 0:
                # 计算单元格在原图中的位置
                x = int(tl[0] + j * cell_size[1] + cell_size[1] * 0.2)
                y = int(tl[1] + i * cell_size[0] + cell_size[0] * 0.2)

                digit = str(solution[i][j])
                draw.text((x, y), digit, fill=(0, 0, 255), font=font)

    return np.array(img_pil)
def print_sudoku_board1(board):
    """格式化打印数独矩阵（空值用0显示）"""
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)  # 水平分隔线
        row = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row += " |"  # 垂直分隔线
            row += f" {board[i][j]}"  # 直接显示0
        print(row.lstrip())  # 去除开头空格

def print_sudoku_board(board):
    """格式化打印数独矩阵"""
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)  # 水平分隔线
        row = ""
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row += " |"  # 垂直分隔线
            row += f" {board[i][j]}"
        print(row.lstrip())  # 去除开头空格


# 主流程
if __name__ == "__main__":
    image_path = "123.png"  # 替换为你的数独图片路径

    # 步骤1：图像处理
    original_image, edges = preprocess_image(image_path)
    corners = find_corners(edges)
    if corners is None:
        print("无法检测到数独网格")
        exit()

    warped = perspective_transform(original_image, corners)
    grid, cell_size = extract_grid(warped)
    original_board = extract_digits(grid)

    # 新增：打印识别后的原始数独矩阵
    print("识别后的原始数独矩阵：")
    print_sudoku_board1(original_board)

    # 步骤2：数独求解
    if solve_sudoku(original_board):
        print("数独已解决！")
        print("\n解答结果矩阵：")
        print_sudoku_board(original_board)  # 新增：打印数独矩阵
    else:
        print("无解")
        exit()

    # 步骤3：结果填充
    result_image = fill_solution(original_image, corners, cell_size, original_board)

    # 显示结果（使用 matplotlib）
    import matplotlib.pyplot as plt

    plt.imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    plt.title("Solved Sudoku")
    plt.axis('off')
    plt.show()

    # 保存结果
    cv2.imwrite("solved_sudoku.jpg", result_image)