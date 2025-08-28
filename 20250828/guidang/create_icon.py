# -*- coding: utf-8 -*-
"""
创建应用程序图标
生成用于exe打包的图标文件
"""

from PIL import Image, ImageDraw
import os

def create_app_icon(output_path: str = "app_icon.ico"):
    """创建应用程序图标
    
    Args:
        output_path: 输出图标文件路径
    """
    try:
        # 创建多个尺寸的图标
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        
        for size in sizes:
            # 创建图像
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 计算比例
            scale = size / 64.0
            
            # 绘制文件夹图标
            folder_color = '#4A90E2'  # 蓝色
            doc_color = '#FFFFFF'     # 白色
            border_color = '#2C5282'  # 深蓝色
            
            # 文件夹底部
            folder_left = int(10 * scale)
            folder_top = int(25 * scale)
            folder_right = int(54 * scale)
            folder_bottom = int(50 * scale)
            
            draw.rectangle(
                [folder_left, folder_top, folder_right, folder_bottom],
                fill=folder_color,
                outline=border_color,
                width=max(1, int(2 * scale))
            )
            
            # 文件夹标签
            tab_left = int(10 * scale)
            tab_top = int(20 * scale)
            tab_right = int(30 * scale)
            tab_bottom = int(25 * scale)
            
            draw.rectangle(
                [tab_left, tab_top, tab_right, tab_bottom],
                fill=folder_color,
                outline=border_color,
                width=max(1, int(2 * scale))
            )
            
            # 文档图标1
            doc1_left = int(20 * scale)
            doc1_top = int(30 * scale)
            doc1_right = int(35 * scale)
            doc1_bottom = int(45 * scale)
            
            draw.rectangle(
                [doc1_left, doc1_top, doc1_right, doc1_bottom],
                fill=doc_color,
                outline=border_color,
                width=max(1, int(1 * scale))
            )
            
            # 文档图标2
            doc2_left = int(25 * scale)
            doc2_top = int(35 * scale)
            doc2_right = int(45 * scale)
            doc2_bottom = int(50 * scale)
            
            draw.rectangle(
                [doc2_left, doc2_top, doc2_right, doc2_bottom],
                fill=doc_color,
                outline=border_color,
                width=max(1, int(1 * scale))
            )
            
            # 添加一些装饰线条（表示文档内容）
            if size >= 32:
                line_width = max(1, int(1 * scale))
                
                # 文档1的线条
                for i in range(2):
                    y = doc1_top + int((3 + i * 3) * scale)
                    draw.line(
                        [doc1_left + int(2 * scale), y, doc1_right - int(2 * scale), y],
                        fill=border_color,
                        width=line_width
                    )
                
                # 文档2的线条
                for i in range(2):
                    y = doc2_top + int((3 + i * 3) * scale)
                    draw.line(
                        [doc2_left + int(2 * scale), y, doc2_right - int(2 * scale), y],
                        fill=border_color,
                        width=line_width
                    )
            
            images.append(image)
        
        # 保存为ICO文件
        images[0].save(
            output_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        print(f"图标已创建: {output_path}")
        return True
        
    except Exception as e:
        print(f"创建图标失败: {str(e)}")
        return False

def create_png_icon(output_path: str = "app_icon.png", size: int = 256):
    """创建PNG格式的图标
    
    Args:
        output_path: 输出图标文件路径
        size: 图标尺寸
    """
    try:
        # 创建图像
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 计算比例
        scale = size / 64.0
        
        # 绘制渐变背景圆形
        center = size // 2
        radius = int(30 * scale)
        
        # 创建渐变效果
        for r in range(radius, 0, -1):
            alpha = int(255 * (radius - r) / radius * 0.1)
            color = (74, 144, 226, alpha)
            draw.ellipse(
                [center - r, center - r, center + r, center + r],
                fill=color
            )
        
        # 绘制主要图标内容
        folder_color = '#4A90E2'
        doc_color = '#FFFFFF'
        border_color = '#2C5282'
        
        # 文件夹底部
        folder_left = int(10 * scale)
        folder_top = int(25 * scale)
        folder_right = int(54 * scale)
        folder_bottom = int(50 * scale)
        
        draw.rectangle(
            [folder_left, folder_top, folder_right, folder_bottom],
            fill=folder_color,
            outline=border_color,
            width=max(1, int(2 * scale))
        )
        
        # 文件夹标签
        tab_left = int(10 * scale)
        tab_top = int(20 * scale)
        tab_right = int(30 * scale)
        tab_bottom = int(25 * scale)
        
        draw.rectangle(
            [tab_left, tab_top, tab_right, tab_bottom],
            fill=folder_color,
            outline=border_color,
            width=max(1, int(2 * scale))
        )
        
        # 文档图标
        docs = [
            (20, 30, 35, 45),  # 文档1
            (25, 35, 45, 50),  # 文档2
        ]
        
        for doc_left, doc_top, doc_right, doc_bottom in docs:
            doc_left = int(doc_left * scale)
            doc_top = int(doc_top * scale)
            doc_right = int(doc_right * scale)
            doc_bottom = int(doc_bottom * scale)
            
            draw.rectangle(
                [doc_left, doc_top, doc_right, doc_bottom],
                fill=doc_color,
                outline=border_color,
                width=max(1, int(1 * scale))
            )
            
            # 添加文档内容线条
            if size >= 64:
                line_width = max(1, int(1 * scale))
                for i in range(min(3, (doc_bottom - doc_top) // int(4 * scale))):
                    y = doc_top + int((3 + i * 4) * scale)
                    if y < doc_bottom - int(2 * scale):
                        draw.line(
                            [doc_left + int(2 * scale), y, doc_right - int(2 * scale), y],
                            fill=border_color,
                            width=line_width
                        )
        
        # 保存PNG文件
        image.save(output_path, format='PNG')
        print(f"PNG图标已创建: {output_path}")
        return True
        
    except Exception as e:
        print(f"创建PNG图标失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 创建图标文件
    print("正在创建应用程序图标...")
    
    # 创建ICO格式图标（用于exe）
    create_app_icon("app_icon.ico")
    
    # 创建PNG格式图标（用于其他用途）
    create_png_icon("app_icon.png", 256)
    
    print("图标创建完成！")