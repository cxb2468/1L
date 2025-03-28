import os
import time
import json
import wave
import pyaudio
import requests
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import urllib.request
import nls
import queue
import threading
import warnings
from openai import OpenAI

warnings.filterwarnings("ignore", category=SyntaxWarning)

from config import Config

# 从配置文件加载阿里云API配置
config = Config()
ACCESS_KEY_ID = config.access_key_id
ACCESS_KEY_SECRET = config.access_key_secret
APP_KEY = config.app_key
REGION_ID = config.region_id

# 使用run.py中的logging配置

class SpeechRecognizer:
    def __init__(self):
        if not check_internet():
            raise ConnectionError("网络连接不可用，请检查网络设置")
        if not validate_appkey():
            raise ValueError("AppKey格式不正确，请检查配置")
        try:
            self._token = self._get_token()
            if not self._token:
                raise ValueError("获取Token失败")
            self.transcriber = nls.NlsSpeechTranscriber(
                url="wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1",
                token=self._token,
                appkey=APP_KEY,
                on_sentence_end=self._on_sentence_end,
                on_completed=self._on_completed,
                on_error=self._on_error
            )
            # 初始化DeepSeek客户端
            self.deepseek_client = OpenAI(
                api_key=config.deepseek_api_key,
                base_url=config.deepseek_base_url
            )
            # 初始化结果列表
            self.results = []
            self.recognition_completed = False
        except Exception as e:
            print(f"初始化语音识别器失败: {str(e)}")
            raise

    def _correct_text(self, text):
        """使用DeepSeek进行文本纠错"""
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的文本优化助手，请严格按照以下规范处理文本：\n1. 标点符号使用规范：\n   - 句子结尾使用句号（。）\n   - 并列短句之间使用顿号（、）\n   - 语气停顿使用逗号（，）\n   - 转折或因果关系使用分号（；）\n   - 表达强烈情感使用感叹号（！）\n   - 疑问句使用问号（？）\n   - 引用或特殊词语使用引号（）"},
                    {"role": "user", "content": f"请优化以下文本（包括错别字修正和标点符号添加）：{text}"}
                ],
                stream=False
            )
            corrected_text = response.choices[0].message.content
            logging.info(f"原文本: {text}")
            logging.info(f"修正后: {corrected_text}")
            return corrected_text
        except Exception as e:
            logging.error(f"文本纠错失败: {str(e)}")
            return text

    def _on_sentence_end(self, message):
        try:
            if isinstance(message, str):
                msg = json.loads(message)
            else:
                msg = message
            payload = msg.get('payload', {})
            result = payload.get('result', '')
            if result:
                # 对识别结果进行纠错处理
                corrected_result = self._correct_text(result)
                if corrected_result:
                    self.result = corrected_result  # 直接替换而不是追加
                    logging.info(f'更新识别结果: {self.result}')
        except Exception as e:
            logging.error(f"处理结果时出错: {str(e)}")

    def recognize(self, audio_file):
        """识别整个音频文件"""
        if not os.path.exists(audio_file):
            logging.error(f"音频文件不存在: {audio_file}")
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
        
        try:
            logging.info(f"开始处理音频文件: {audio_file}")
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            if len(audio_data) == 0:
                logging.error("音频文件为空")
                raise ValueError("音频文件为空")
            
            self.result = ""
            try:
                try:
                    logging.info("启动语音识别转录器")
                    self.transcriber.start(aformat='wav', sample_rate=16000)
                    time.sleep(0.5)

                    max_retries = 3
                    for chunk in self._audio_chunks(audio_data):
                        if not chunk:
                            continue
                        retry_count = 0
                        while retry_count < max_retries:
                            try:
                                self.transcriber.send_audio(chunk)
                                time.sleep(0.01)
                                break
                            except Exception as e:
                                retry_count += 1
                                logging.warning(f"发送音频数据出错(尝试第{retry_count}次): {str(e)}")
                                if retry_count == max_retries:
                                    raise RuntimeError(f"音频发送失败: {str(e)}") from e
                                time.sleep(0.1 * retry_count)
                finally:
                    try:
                        # 增加超时重试机制
                        max_stop_retries = 3
                        stop_retry_count = 0
                        while stop_retry_count < max_stop_retries:
                            try:
                                self.transcriber.stop()
                                break
                            except Exception as stop_error:
                                stop_retry_count += 1
                                logging.warning(f"停止转录器出错(尝试第{stop_retry_count}次): {str(stop_error)}")
                                if stop_retry_count == max_stop_retries:
                                    logging.error(f"停止转录器失败: {str(stop_error)}")
                                time.sleep(0.5)
                    finally:
                        time.sleep(1)
                
                if not self.result:
                    logging.warning("警告: 未获取到识别结果")
                return self.result
            except Exception as e:
                logging.error(f"语音识别过程出错: {str(e)}")
                raise
        except Exception as e:
            logging.error(f"处理音频文件时出错: {str(e)}")
            raise

    def _audio_chunks(self, data, chunk_size=640):
        return (data[i:i+chunk_size] for i in range(0, len(data), chunk_size))


    def _on_completed(self, message):
        logging.info("识别完成")

    def _on_error(self, message):
        # 处理错误消息格式
        error_msg = json.loads(message) if isinstance(message, str) else message
        logging.error(f"发生错误: {error_msg.get('message', '未知错误')}")

    def _get_token(self):
        # 保持原有token获取逻辑
        client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION_ID)
        request = CommonRequest()
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')
        response = client.do_action_with_exception(request)
        logging.debug(f"获取到的Token响应: {response}")  # 调试输出
        return json.loads(response)['Token']['Id']

def get_aliyun_token():
    """使用阿里云SDK获取Token"""
    client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION_ID)
    
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')

    try:
        response = client.do_action_with_exception(request)
        jss = json.loads(response)
        if 'Token' in jss and 'Id' in jss['Token']:
            return jss['Token']['Id']
        else:
            print("获取Token失败：响应格式不正确")
            return ""
    except Exception as e:
        print(f"获取Token失败：{str(e)}")
        return ""

def record_audio(filename, stop_event):
    """支持中断的录音函数"""
    CHUNK = 640
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    frames = []
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("请开始说话...")
        while not stop_event.is_set():
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"录音过程出错: {e}")
                break

        print("录音结束")
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        print(f"录音系统初始化失败: {e}")
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

    print("录音结束")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def speech_to_text(stop_event=None):
    # 获取Token
    token = get_aliyun_token()
    if not token:
        return ""

    # 如果没有传入stop_event，创建一个新的Event对象
    if stop_event is None:
        stop_event = threading.Event()

    # 录制音频
    audio_file = "temp.wav"
    record_audio(audio_file, stop_event)

    # 调用阿里云语音识别API
    url = f"https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"
    headers = {
        "X-NLS-Token": token,
        "Content-Type": "application/octet-stream"
    }
    params = {
        "appkey": APP_KEY,
        "format": "wav",
        "sample_rate": 16000,
        "enable_punctuation_prediction": True,
        "enable_inverse_text_normalization": True,
        "enable_voice_detection": True
    }

    try:
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        response = requests.post(url, headers=headers, params=params, data=audio_data)
        response.raise_for_status()
        result = response.json()
        
        if result['status'] == 20000000:
            return result['result']
        else:
            print(f"识别失败：{result['message']}")
            print(f"完整响应：{result}")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"语音识别请求失败：{str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"错误响应内容：{e.response.text}")
        return ""

def check_internet():
    """检测网络连接，使用阿里云服务端点"""
    test_urls = [
        "https://nls-meta.cn-shanghai.aliyuncs.com",  # 阿里云语音识别服务
        "https://www.aliyun.com",  # 阿里云官网
        "https://www.baidu.com"  # 百度作为备用
    ]
    
    for url in test_urls:
        try:
            urllib.request.urlopen(url, timeout=3)
            return True
        except:
            continue
    return False

def validate_appkey():
    """验证AppKey格式"""
    if len(APP_KEY) not in [16, 32] or not APP_KEY.isalnum():
        print("AppKey格式不正确，应为16或32位字母数字组合")
        return False
    return True

def validate_credentials():
    """验证环境变量配置"""
    required_vars = {
        'ACCESS_KEY_ID': ACCESS_KEY_ID,
        'ACCESS_KEY_SECRET': ACCESS_KEY_SECRET,
        'APP_KEY': APP_KEY
    }
    
    for var, value in required_vars.items():
        if not value:
            raise ValueError(f"必须设置环境变量: {var}")
        if len(value) < 16:  # 基本长度检查
            raise ValueError(f"无效的 {var} 配置")
    return True

if __name__ == "__main__":
    if not validate_appkey():
        print("请检查AppKey配置")
    elif not check_internet():
        print("网络连接不可用，请检查网络设置")
    else:
        stop_event = threading.Event()
        try:
            result = speech_to_text(stop_event)
            if result:
                print("最终识别内容：", result)
            else:
                print("没有获取到有效输入")
        except KeyboardInterrupt:
            print("\n用户中断录音")
            stop_event.set()
        except Exception as e:
            print(f"\n发生错误: {e}")
            stop_event.set()
