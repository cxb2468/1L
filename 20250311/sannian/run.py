import sys
import traceback
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    try:
        from voice_recorder import VoiceRecorder
        logging.info('正在初始化应用程序...')
        app = VoiceRecorder()
        logging.info('应用程序初始化完成，开始运行...')
        app.run()
    except ImportError as e:
        logging.error(f'导入模块失败: {e}\n{traceback.format_exc()}')
    except Exception as e:
        logging.error(f'程序运行时出错: {e}\n{traceback.format_exc()}')

if __name__ == '__main__':
    main()