# -*- coding: utf-8 -*-
"""
@file    : auto.py
@AuThor  : 爱喝水的木子
@Email   : leebigshan@gmail.com
@Time    : 2026/1/26 10:55
@desc    :
"""
import subprocess
import os
import sys  # 添加sys模块导入
import tempfile
import time
import shutil
from datetime import datetime
from typing import List, Tuple  # 添加类型导入

import requests
import asyncio
import edge_tts

def get_date_str() -> str:
    """
    获取当前日期的字符串格式（YYYY-MM-DD）

    Returns:
        str: 格式化后的日期字符串，例如 "2026-01-26"
    """
    return datetime.now().strftime('%Y-%m-%d')

async def text_to_speech(
        text: str,
        output_file: str = "tts_output.mp3",
        voice: str = "zh-CN-XiaoyiNeural",
        rate: str = "+0%",
        volume: str = "+0%"
) -> None:
    """
    使用edge_tts将文本转为语音并保存为MP3文件，包含自动重试机制

    Args:
        text: 要转换的文本内容（支持中英文，过长文本建议分段）
        output_file: 输出音频文件路径（默认tts_output.mp3）
        voice: 语音类型（默认中文晓伊 zh-CN-XiaoyiNeural）
        rate: 语速调整（+0%为正常，+50%加快，-50%减慢，必须带%符号）
        volume: 音量调整（+0%为正常，范围-100%到+100%，必须带%符号）

    Raises:
        Exception: 重试5次后仍失败会打印错误并终止当前转换
    """
    max_retry = 5  # 最大重试次数
    retry_count = 0

    while retry_count < max_retry:
        try:
            retry_count += 1
            # 创建TTS通信对象，配置语音参数
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume
            )
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # 将音频流保存到文件
            await communicate.save(output_file)
            print(f"✅ 音频已成功保存到：{output_file}")
            time.sleep(1)  # 缩短等待时间，避免不必要的延迟
            break  # 成功后退出重试循环

        except Exception as e:
            error_msg = f"❌ 第{retry_count}次生成音频失败：{str(e)}"
            print(error_msg)
            if retry_count >= max_retry:
                print(f"❌ 重试{max_retry}次仍失败，跳过当前文本转换")
                raise Exception(error_msg)  # 抛出异常让上层处理
            time.sleep(2)  # 重试前等待2秒，避免频繁请求

async def list_voices() -> None:
    """
    获取并打印所有支持的中文语音列表，方便选择语音参数

    Notes:
        输出格式：语音名称（ShortName）、性别、地区
    """
    try:
        voices = await edge_tts.list_voices()
        # 筛选中文语音并提取关键信息
        chinese_voices = []
        for v in voices:
            # 检查字典键是否存在
            if "Locale" in v and "zh-" in v["Locale"]:
                voice_info = {
                    "ShortName": v.get("ShortName", ""),
                    "Gender": v.get("Gender", ""),
                    "Region": v.get("Locale", "")
                }
                chinese_voices.append(voice_info)

        print("\n===== 支持的中文语音列表 =====")
        for idx, voice in enumerate(chinese_voices, 1):
            print(f"{idx}. 语音名称：{voice['ShortName']} | 性别：{voice['Gender']} | 地区：{voice['Region']}")
        print("==============================\n")

    except Exception as e:
        print(f"❌ 获取语音列表失败：{str(e)}")

def get_image(url: str, save_path: str) -> None:
    """
    从指定URL下载图片并保存到本地

    Args:
        url: 图片的网络URL地址
        save_path: 图片保存的本地路径

    Raises:
        requests.exceptions.RequestException: 网络请求失败时抛出
        IOError: 文件写入失败时抛出
    """
    if not url:
        raise ValueError("❌ 图片URL为空，无法下载")

    try:
        # 设置超时时间，避免无限等待
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP响应状态码

        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        # 写入图片文件
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"✅ 图片已成功保存到：{save_path}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ 下载图片失败（网络错误）：{str(e)}")
    except IOError as e:
        raise Exception(f"❌ 保存图片失败（文件错误）：{str(e)}")

def get_news_data(api_url: str = "https://60.020417.xyz/v2/60s") -> Tuple[List[str], str]:
    """
    从指定API接口获取新闻文本列表和图片URL

    Args:
        api_url: 数据接口的URL地址

    Returns:
        tuple: (新闻文本列表, 图片URL)

    Raises:
        requests.exceptions.RequestException: 接口请求失败
        KeyError: 接口返回数据格式不符合预期
        ValueError: 返回的新闻数据为空
    """
    try:
        # 发送GET请求获取数据，设置超时
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        result = response.json()

        # 提取核心数据
        data = result.get('data', {})
        news_text_list = data.get('news', [])
        image_url = data.get('image', '')

        # 数据校验
        if not isinstance(news_text_list, list) or len(news_text_list) == 0:
            raise ValueError("❌ 接口返回的新闻列表为空或格式错误")
        if not image_url:
            raise ValueError("❌ 接口返回的图片URL为空")

        print(f"✅ 成功获取{len(news_text_list)}条新闻数据")
        return news_text_list, image_url

    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ 接口请求失败：{str(e)}")
    except KeyError as e:
        raise Exception(f"❌ 接口返回数据格式错误，缺少字段：{str(e)}")

def get_result(img_path: str, audio_dir_save: str) -> int:
    """
    主流程：获取新闻数据、下载图片、生成音频文件

    Args:
        img_path: 图片保存的完整路径
        audio_dir_save: 音频文件保存的目录路径

    Returns:
        int: 生成的音频文件数量

    Raises:
        Exception: 任意步骤失败时抛出
    """
    try:
        # 1. 获取新闻数据和图片URL
        news_list, image_url = get_news_data()

        # 2. 下载图片
        get_image(image_url, img_path)

        # 3. 生成音频文件
        audio_count = create_audio(news_list, audio_dir_save)

        return audio_count

    except Exception as e:
        print(f"❌ 处理数据失败：{str(e)}")
        raise  # 重新抛出异常，让上层处理

def create_audio(news_list: List[str], save_audio_dir: str) -> int:
    """
    将新闻列表中的每条文本转为音频文件，保存到指定目录

    Args:
        news_list: 新闻文本列表
        save_audio_dir: 音频文件保存目录

    Returns:
        int: 成功生成的音频文件数量

    Raises:
        Exception: 音频转换失败时抛出
    """
    # 确保保存目录存在
    os.makedirs(save_audio_dir, exist_ok=True)

    # 清空目录原有文件（避免旧文件干扰）
    for file in os.listdir(save_audio_dir):
        file_path = os.path.join(save_audio_dir, file)
        if os.path.isfile(file_path) and file_path.endswith('.mp3'):
            os.remove(file_path)

    # 1. 打印支持的语音列表（仅首次运行时展示）
    try:
        asyncio.run(list_voices())
    except Exception:
        # 忽略语音列表获取的错误，不影响主要功能
        print("⚠️ 获取语音列表时出现一些问题，继续执行...")

    # 2. 逐条转换文本为音频
    success_count = 0
    for idx, text in enumerate(news_list):
        try:
            audio_file_path = os.path.join(save_audio_dir, f"{idx}.mp3")
            asyncio.run(text_to_speech(
                text=text,
                output_file=audio_file_path,
                voice="zh-CN-XiaoyiNeural",  # 晓伊女声
                rate="-10%",  # 语速减慢10%
                volume="+20%"  # 音量增大20%
            ))
            success_count += 1
        except Exception as e:
            print(f"❌ 跳过第{idx}条新闻的音频转换：{str(e)}")
            continue

    print(f"✅ 共生成{success_count}个音频文件（总计{len(news_list)}条新闻）")
    return success_count

def merge_audio_files(
        audio_files: List[str],
        output_file: str,
        ffmpeg_path: str = "ffmpeg"
) -> None:
    """
    使用ffmpeg合并多个音频文件为一个完整的音频文件（无损合并）

    Args:
        audio_files: 待合并的音频文件路径列表（按合并顺序排列）
        output_file: 合并后的输出音频文件路径（建议MP3格式）
        ffmpeg_path: ffmpeg可执行文件路径，默认使用系统环境变量中的ffmpeg

    Raises:
        FileNotFoundError: 输入音频文件不存在或ffmpeg未找到
        RuntimeError: ffmpeg执行失败
    """
    # 检查是否安装了ffmpeg，如果没有则提示用户安装
    if shutil.which(ffmpeg_path) is None:
        print(f"⚠️ 未找到ffmpeg，将无法合并音频文件。请安装ffmpeg以获得最佳体验。")
        print("安装ffmpeg方法：")
        print("Windows用户可以从 https://www.gyan.dev/ffmpeg/builds/ 下载并添加到PATH")
        print("或者使用Chocolatey: choco install ffmpeg")
        print("macOS用户可以使用: brew install ffmpeg")
        print("Linux用户可以使用: sudo apt install ffmpeg 或相应包管理器")
        
        # 如果找不到ffmpeg，仅提示用户而不尝试其他方法
        print(f"⚠️ 由于缺少ffmpeg，音频文件已保存在单独的文件中，位于: {os.path.dirname(output_file)}")
        print(f"💡 提示：请安装ffmpeg后再运行程序以自动合并音频")
        return
    
    # 前置校验
    if not audio_files:
        raise ValueError("❌ 待合并的音频文件列表为空")

    # 检查输入文件是否存在
    for audio_file in audio_files:
        audio_file = os.path.abspath(audio_file)
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"❌ 音频文件不存在：{audio_file}")

    # 创建临时文件，存储待合并的音频文件列表（ffmpeg要求的格式）
    with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.txt',
            encoding='utf-8'
    ) as temp_f:
        temp_file_path = temp_f.name
        # 写入文件路径（每行格式：file '绝对路径'）
        for audio_file in audio_files:
            abs_path = os.path.abspath(audio_file)
            temp_f.write(f"file '{abs_path}'\n")

    try:
        # 构建ffmpeg命令
        cmd = [
            ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_file_path,
            '-c', 'copy',
            '-y',  # 覆盖已存在的输出文件
            output_file
        ]

        # 执行ffmpeg命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # 检查执行结果
        if result.returncode != 0:
            raise RuntimeError(f"❌ 音频合并失败：{result.stderr}")

        print(f"✅ 音频合并成功！输出文件：{output_file}")

    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def image_audio_to_video(
        image_path: str,
        audio_path: str,
        output_video_path: str,
        ffmpeg_path: str = "ffmpeg"
) -> None:
    """
    将单张图片和音频合并为视频，视频时长与音频保持一致

    Args:
        image_path: 图片文件路径（支持JPG/PNG/BMP等格式）
        audio_path: 音频文件路径（支持MP3/WAV/M4A等格式）
        output_video_path: 输出视频文件路径（建议MP4格式）
        ffmpeg_path: ffmpeg可执行文件路径

    Raises:
        FileNotFoundError: 输入文件不存在或ffmpeg未找到
        RuntimeError: ffmpeg执行失败
    """
    # 前置校验
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 图片文件不存在：{image_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"❌ 音频文件不存在：{audio_path}")
    if shutil.which(ffmpeg_path) is None:
        raise FileNotFoundError(f"❌ 未找到ffmpeg，请检查路径：{ffmpeg_path}")

    # 确保输出目录存在
    output_dir = os.path.dirname(output_video_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 构建ffmpeg命令
    cmd = [
        ffmpeg_path,
        '-loop', '1',  # 循环播放图片
        '-i', image_path,  # 输入图片
        '-i', audio_path,  # 输入音频
        '-shortest',  # 视频时长等于音频时长
        '-pix_fmt', 'yuv420p',  # 兼容所有播放器的像素格式
        '-c:v', 'libx264',  # H.264视频编码（MP4标准）
        '-c:a', 'copy',  # 音频流直接复制（无损）
        '-y',  # 覆盖已有文件
        output_video_path
    ]

    try:
        # 执行ffmpeg命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            raise RuntimeError(f"❌ 视频生成失败：{result.stderr}")

        print(f"✅ 视频生成成功！输出文件：{output_video_path}")

    except Exception as e:
        print(f"❌ 处理视频时出错：{str(e)}")
        raise

# 主执行逻辑
if __name__ == "__main__":
    try:
        # 修复事件循环问题 - 在Windows上正确处理异步事件循环
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 1. 初始化路径
            date_str = get_date_str()
            base_dir = date_str
            os.makedirs(base_dir, exist_ok=True)  # 改为exist_ok=True，避免重复创建报错

            img_save_path = os.path.join(base_dir, f"{date_str}.jpg")
            audio_dir = os.path.join(base_dir, 'audio')

            # 2. 获取数据并生成音频
            audio_number = get_result(img_save_path, audio_dir)

            if audio_number == 0:
                raise Exception("❌ 未生成任何音频文件，终止流程")

            # 3. 合并音频
            audio_merge_path = os.path.join(base_dir, "merge.mp3")
            audio_files_list = [
                os.path.join(audio_dir, f"{i}.mp3")
                for i in range(audio_number)
                if os.path.exists(os.path.join(audio_dir, f"{i}.mp3"))  # 只合并存在的文件
            ]

            # 检查是否有音频文件需要合并
            if audio_files_list:
                merge_audio_files(audio_files_list, audio_merge_path)
            else:
                print("⚠️ 没有找到需要合并的音频文件")

            # 4. 生成视频
            merge_result_video = os.path.join(base_dir, f"{date_str}_finally.mp4")
            if os.path.exists(audio_merge_path):  # 只有在合并音频存在时才生成视频
                image_audio_to_video(img_save_path, audio_merge_path, merge_result_video)
            else:
                print("⚠️ 没有合并音频文件，跳过视频生成步骤")

            print("\n🎉 所有流程执行完成！")
            print(f"📁 输出目录：{os.path.abspath(base_dir)}")

        finally:
            # 关闭事件循环
            loop.close()
            
    except Exception as e:
        print(f"\n❌ 程序执行失败：{str(e)}")
        exit(1)