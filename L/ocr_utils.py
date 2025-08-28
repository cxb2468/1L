import cv2
import numpy as np
import pytesseract
import mss
from PIL import Image
import pyautogui


def capture_screen_region(left, top, width, height):
    """
    截取屏幕指定区域
    
    Args:
        left (int): 截图区域左上角x坐标
        top (int): 截图区域左上角y坐标
        width (int): 截图区域宽度
        height (int): 截图区域高度
    
    Returns:
        numpy.ndarray: 截图的BGR图像数组
    """
    monitor = {"top": top, "left": left, "width": width, "height": height}
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = np.array(sct.grab(monitor))
        # 转换为OpenCV格式(BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img


def preprocess_for_ocr(image):
    """
    对图像进行预处理以提高OCR识别准确率
    
    Args:
        image (numpy.ndarray): 输入图像
    
    Returns:
        numpy.ndarray: 预处理后的图像
    """
    # 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用高斯模糊以减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 应用阈值处理
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh


def recognize_text_in_region(left, top, width, height, lang='chi_sim+eng'):
    """
    识别屏幕指定区域中的文字
    
    Args:
        left (int): 区域左上角x坐标
        top (int): 区域左上角y坐标
        width (int): 区域宽度
        height (int): 区域高度
        lang (str): OCR识别语言，默认为简体中文+英文
    
    Returns:
        str: 识别出的文字
    """
    # 截取屏幕区域
    img = capture_screen_region(left, top, width, height)
    
    # 预处理图像
    processed_img = preprocess_for_ocr(img)
    
    # 使用pytesseract进行OCR识别
    text = pytesseract.image_to_string(processed_img, lang=lang)
    
    # 清理识别结果
    text = text.strip()
    
    return text


def find_text_and_click(text_to_find, search_area=(0, 0, 1920, 1080), lang='chi_sim+eng'):
    """
    在屏幕上查找指定文字并点击
    
    Args:
        text_to_find (str): 要查找的文字
        search_area (tuple): 搜索区域 (left, top, width, height)
        lang (str): OCR识别语言
    
    Returns:
        bool: 是否找到并点击了文字
    """
    # 这是一个简化的实现，实际应用中可能需要更复杂的文字定位逻辑
    left, top, width, height = search_area
    img = capture_screen_region(left, top, width, height)
    
    # 预处理图像
    processed_img = preprocess_for_ocr(img)
    
    # 获取OCR数据，包括文字位置信息
    data = pytesseract.image_to_data(processed_img, lang=lang, output_type=pytesseract.Output.DICT)
    
    # 查找匹配的文字
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:  # 置信度大于60%
            if text_to_find in data['text'][i]:
                # 计算文字在屏幕上的中心坐标
                x = data['left'][i] + left
                y = data['top'][i] + top
                w = data['width'][i]
                h = data['height'][i]
                
                # 点击文字中心
                center_x = x + w // 2
                center_y = y + h // 2
                pyautogui.click(center_x, center_y)
                
                return True
    
    return False


def get_text_coordinates(text_to_find, search_area=(0, 0, 1920, 1080), lang='chi_sim+eng'):
    """
    获取屏幕上指定文字的坐标
    
    Args:
        text_to_find (str): 要查找的文字
        search_area (tuple): 搜索区域 (left, top, width, height)
        lang (str): OCR识别语言
    
    Returns:
        tuple: 文字区域的 (left, top, width, height) 或 None（未找到）
    """
    left, top, width, height = search_area
    img = capture_screen_region(left, top, width, height)
    
    # 预处理图像
    processed_img = preprocess_for_ocr(img)
    
    # 获取OCR数据，包括文字位置信息
    data = pytesseract.image_to_data(processed_img, lang=lang, output_type=pytesseract.Output.DICT)
    
    # 查找匹配的文字
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:  # 置信度大于60%
            if text_to_find in data['text'][i]:
                # 返回文字区域坐标（相对于屏幕）
                x = data['left'][i] + left
                y = data['top'][i] + top
                w = data['width'][i]
                h = data['height'][i]
                
                return (x, y, w, h)
    
    return None