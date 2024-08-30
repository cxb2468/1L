import cv2
import numpy as np
import glob
 
 
def get_plate(image_):
    global plate
    rawImage = image_.copy()
    # 去噪处理
    image_ = cv2.GaussianBlur(image_, (3, 3), 0)
    # 色彩空间转换
    image_ = cv2.cvtColor(image_, cv2.COLOR_BGR2GRAY)
    # Sobel算子
    Sobel_x = cv2.Sobel(image_, cv2.CV_16S, 1, 0)
    absX = cv2.convertScaleAbs(Sobel_x)
    image_ = absX
    # 阈值处理
    ret, image_ = cv2.threshold(image_, 0, 255, cv2.THRESH_OTSU)
    # 闭运算 先膨胀后腐蚀 车牌各个字符是分散的 让车牌构成一体
    kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
    image_ = cv2.morphologyEx(image_, cv2.MORPH_CLOSE, kernelX)
    # 开运算 先腐蚀后膨胀 去除噪声
    kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))
    image_ = cv2.morphologyEx(image_, cv2.MORPH_OPEN, kernelY)
    # 中值滤波 去除噪声
    image_ = cv2.medianBlur(image_, 15)
    # 查找轮廓
    contours, w1 = cv2.findContours(image_, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 逐个遍历 将宽度>3倍高度的轮廓确定为车牌
    for item in contours:
        rect = cv2.boundingRect(item)
        x = rect[0]
        y = rect[1]
        weight = rect[2]
        height = rect[3]
        if weight > (height * 3):
            plate = rawImage[y:y + height, x:x + weight]
    return plate
 
 
def preprocessor(image_):
    # 图像去噪灰度处理
    image_ = cv2.GaussianBlur(image_, (3, 3), 0)
    # 色彩空间转换
    gray_image = cv2.cvtColor(image_, cv2.COLOR_RGB2GRAY)
    # 阈值处理
    ret, image_ = cv2.threshold(gray_image, 0, 255, cv2.THRESH_OTSU)
    # 膨胀处理 让一个字构成一个整体
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    image_ = cv2.dilate(image_, kernel)
    return image_
 
 
def split_plate(image_):
    # 查找轮廓，各个字符的轮廓
    contours, hierarchy = cv2.findContours(image_, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    words = []
    # 遍历所有轮廓
    for item in contours:
        rect = cv2.boundingRect(item)
        words.append(rect)
    # 按照x轴坐标值排序（自左向右排序）
    words = sorted(words, key=lambda s: s[0], reverse=False)
    # 用word存放左上角起始点及长宽值
    plateChars = []
    for word in words:
        # 筛选字符的轮廓(高宽比在1.5-8之间，宽度大于3)
        if (word[3] > (word[2] * 1.5)) and (word[3] < (word[2] * 8)) and (word[2] > 3):
            plateChar = image_[word[1]:word[1] + word[3], word[0]:word[0] + word[2]]
            plateChars.append(plateChar)
    return plateChars
 
 
template_dict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
                 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H',
                 18: 'J', 19: 'K', 20: 'L', 21: 'M', 22: 'N', 23: 'P', 24: 'Q', 25: 'R',
                 26: 'S', 27: 'T', 28: 'U', 29: 'V', 30: 'W', 31: 'X', 32: 'Y', 33: 'Z',
                 34: '京', 35: '津', 36: '冀', 37: '晋', 38: '蒙', 39: '辽', 40: '吉', 41: '黑',
                 42: '沪', 43: '苏', 44: '浙', 45: '皖', 46: '闽', 47: '赣', 48: '鲁', 49: '豫',
                 50: '鄂', 51: '湘', 52: '粤', 53: '桂', 54: '琼', 55: '渝', 56: '川', 57: '贵',
                 58: '云', 59: '藏', 60: '陕', 61: '甘', 62: '青', 63: '宁', 64: '新',
                 65: '港', 66: '澳', 67: '台'}
 
 
def get_characters():
    c = []
    for i_ in range(0, 67):
        words = []
        words.extend(glob.glob(f'template/{template_dict.get(i_)}/*.*'))
        c.append(words)
    return c
 
 
def get_match_value(template, image_):
    # 读取模板图像
    templateImage = cv2.imdecode(np.fromfile(template, dtype=np.uint8), 1)
    # 模板图像色彩空间转换 BGR-->灰度
    templateImage = cv2.cvtColor(templateImage, cv2.COLOR_BGR2GRAY)
    # 模板图像阈值处理 灰度-->二值
    ret, templateImage = cv2.threshold(templateImage, 0, 255, cv2.THRESH_OTSU)
    # 获取待识别图像的尺寸
    height, width = image_.shape
    # 将模板图像调整为与待识别图像尺寸一致
    templateImage = cv2.resize(templateImage, (width, height))
    # 计算模板图像、待识别图像的模板匹配值
    result = cv2.matchTemplate(image_, templateImage, cv2.TM_CCOEFF)
    # 将计算结果返回
    return result[0][0]
 
 
def match_chars(plates, chars_):
    # 存储所有的识别结果
    results_ = []
    # 逐个遍历要识别的字符
    for i_ in plates:
        # 最佳匹配
        best_match = []
        # words 对应的是每一个字符
        for words in chars_:
            match = []
            for word in words:
                result = get_match_value(word, i_)
                match.append(result)
            best_match.append(max(match))
        i_ = best_match.index(max(best_match))
        r = template_dict[i_]
        results_.append(r)
    return results_
 
 
if __name__ == '__main__':
    # 读取原始图像
    image = cv2.imread("test_img.jpg")
    # 获取车牌
    image = get_plate(image)
    # 预处理
    image = preprocessor(image)
    # 分割车牌 将每个字符独立出来
    plate_chars = split_plate(image)
    print(plate_chars)
 
    # 获取所有模板文件
    chars = get_characters()
    # 使用模板chars逐个识别字符集plates
    results = match_chars(plate_chars, chars)
    # 将列表转换为字符串并输出识别结果
    print("".join(results))