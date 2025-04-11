
def capture_and_recognize(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用边缘检测找到数独网格
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    # 找到最大的矩形框作为数独区域
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)

    # 裁剪出数独区域
    sudoku_region = gray[y:y+h, x:x+w]

    # 去除灰色分隔线干扰
    _, binary = cv2.threshold(sudoku_region, 127, 255, cv2.THRESH_BINARY_INV)  # {{ 添加二值化处理 }}
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # {{ 添加形态学开运算 }}

    # 初始化数独矩阵
    sudoku = np.zeros((9, 9), dtype=int)

    cell_width = w // 9
    cell_height = h // 9

    for row in range(9):
        for col in range(9):
            # 截取单个格子
            box = (
                col * cell_width,
                row * cell_height,
                (col + 1) * cell_width,
                (row + 1) * cell_height,
            )
            cell = Image.fromarray(opening[box[1]:box[3], box[0]:box[2]])  # {{ 使用处理后的图像 }}

            # 图像预处理
            cell = ImageOps.grayscale(cell)
            # 增强对比度
            cell = ImageEnhance.Contrast(cell).enhance(3.0)  # {{ 提高对比度 }}
            cell = cell.point(lambda x: 0 if x < 200 else 255)

            # 给单元格添加边界填充
            cell = ImageOps.expand(cell, border=5, fill='white')  # {{ 添加边界填充 }}

            # OCR识别
            text = pytesseract.image_to_string(
                cell,
                config="--psm 10 --oem 3 -c tessedit_char_whitelist=123456789",
            ).strip()
            sudoku[row][col] = int(text) if text else 0

    return sudoku


if __name__ == '__main__':
    sudoku = capture_and_recognize('123.png')
    print(sudoku)