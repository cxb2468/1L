import pyautogui
import cv2
import time
import numpy as np
import mss
import importlib.util

# 检查OCR模块是否可用
ocr_available = importlib.util.find_spec("pytesseract") is not None
if ocr_available:
    import pytesseract
    try:
        from ocr_utils import recognize_text_in_region, find_text_and_click, get_text_coordinates
        print("OCR模块加载成功")
    except ImportError:
        print("无法导入ocr_utils模块")
        ocr_available = False
else:
    print("pytesseract未安装，OCR功能不可用")


def demo_ocr():
    """
    OCR功能演示
    """
    if not ocr_available:
        print("OCR功能不可用，请确保已安装pytesseract和相关依赖")
        return
    
    print("开始OCR功能演示...")
    
    # 示例1: 识别屏幕指定区域的文字
    print("\n1. 识别屏幕指定区域的文字:")
    try:
        # 识别屏幕左上角区域的文字
        text = recognize_text_in_region(0, 0, 400, 200)
        print(f"识别结果: '{text}'")
    except Exception as e:
        print(f"识别出错: {e}")
    
    # 示例2: 查找并点击屏幕上的指定文字
    print("\n2. 查找并点击屏幕上的指定文字:")
    # 注意: 这里使用一个常见的界面文字作为示例
    # 在实际使用中，你需要替换为游戏中实际存在的文字
    target_text = "设置"  # 示例文字
    print(f"尝试查找并点击文字: '{target_text}'")
    
    # 为了安全起见，这里只查找不点击
    coords = get_text_coordinates(target_text)
    if coords:
        x, y, w, h = coords
        print(f"找到文字 '{target_text}' 在位置: ({x}, {y}, {w}, {h})")
        print("注意: 为安全起见，这里不执行实际点击操作")
        # 如果要实际点击，可以使用下面的代码:
        # pyautogui.click(x + w//2, y + h//2)
    else:
        print(f"未找到文字 '{target_text}'")


def compare_methods():
    """
    比较OCR和图像识别方法
    """
    print("\n\n比较OCR和图像识别方法:")
    print("1. 图像识别方法:")
    print("   - 优点: 识别速度快，准确率高(对于固定模板)")
    print("   - 缺点: 游戏更新后需要重新制作模板图片，维护成本高")
    print("   - 适用: 界面元素固定，不经常更新的部分")
    
    print("\n2. OCR方法:")
    print("   - 优点: 适应性强，游戏更新后无需重新制作模板")
    print("   - 缺点: 识别速度相对较慢，对图像质量要求高")
    print("   - 适用: 文字内容相对固定，界面可能更新的部分")
    
    print("\n3. 推荐方案:")
    print("   - 核心操作界面使用图像识别(稳定且快速)")
    print("   - 动态内容(如角色名、数值)使用OCR(适应性强)")
    print("   - 两种方法结合使用，发挥各自优势")


if __name__ == "__main__":
    demo_ocr()
    compare_methods()
    
    print("\n演示结束")
    print("\n要使用OCR功能，请确保:")
    print("1. 已安装pytesseract: pip install pytesseract")
    print("2. 已安装Tesseract-OCR引擎")
    print("3. 已配置pytesseract路径，例如:")
    print("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")