"""
英语闪卡背诵程序 - 增强版
功能：使用在线TTS实现真实发音，支持更多学习模式
作者：工程师 & 英语老师
日期：2026-05-12
"""

import json
import sys
import random
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextBrowser,
                             QGroupBox, QMessageBox, QProgressBar, QFrame,
                             QComboBox, QCheckBox, QFileDialog, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class TTSPlayer(QThread):
    """TTS音频播放线程"""
    finished = pyqtSignal(bool)
    
    def __init__(self, text, lang='en', audio_url=''):
        super().__init__()
        self.text = text
        self.lang = lang
        self.audio_url = audio_url  # Bing词典音频URL
        
    def run(self):
        """优先使用Bing词典音频，备选多种TTS方案"""
        
        # 方案1: 优先使用Bing词典音频URL
        if self.audio_url:
            try:
                player = QMediaPlayer()
                # Bing词典音频需要完整URL
                full_url = f'https://www.bing.com{self.audio_url}'
                player.setMedia(QMediaContent(QUrl(full_url)))
                player.setVolume(100)
                player.play()
                
                # 等待播放完成
                import time
                time.sleep(1.5)
                
                self.finished.emit(True)
                return
                
            except Exception as e:
                print(f"Bing音频播放失败: {e}，尝试其他方案...")
        
        # 方案2: 尝试使用Google TTS（需要网络）
        try:
            from gtts import gTTS
            import tempfile
            import os
            
            tts = gTTS(text=self.text, lang=self.lang)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            tts.save(temp_file.name)
            
            # 播放音频
            player = QMediaPlayer()
            player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_file.name)))
            player.setVolume(100)
            player.play()
            
            # 等待播放完成
            import time
            time.sleep(2)
            
            # 删除临时文件
            os.unlink(temp_file.name)
            
            self.finished.emit(True)
            
        except ImportError:
            print("gtts未安装，尝试离线TTS...")
        except Exception as e:
            print(f"在线TTS失败: {e}，尝试离线TTS...")
            
            # 方案3: 尝试使用pyttsx3（离线TTS，无需网络）
            # 由于pyttsx3与PyQt事件循环冲突，我们使用系统命令播放
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    # 在Windows上使用PowerShell的语音功能
                    script = f'''Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.Rate = 1
$speak.Volume = 100
$speak.Speak("{self.text}")
'''
                    subprocess.run(['powershell', '-Command', script], timeout=5)
                    self.finished.emit(True)
                    return
                
            except Exception as e2:
                print(f"PowerShell TTS也失败: {e2}")
            
            # 方案4: 尝试使用say命令（macOS）或espeak（Linux）
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['say', self.text])
                    self.finished.emit(True)
                    return
                elif platform.system() == 'Linux':
                    subprocess.run(['espeak', self.text])
                    self.finished.emit(True)
                    return
            except Exception as e3:
                print(f"系统TTS方案也失败: {e3}")
            
            # 所有方案都失败
            self.finished.emit(False)


class FlashCardAppV2(QMainWindow):
    """英语闪卡主应用窗口 - 增强版"""
    
    def __init__(self):
        super().__init__()
        self.words = []
        self.current_index = 0
        self.showing_answer = False
        self.learned_words = set()
        self.random_mode = False
        self.auto_play = False
        self.current_json_file = None  # 记录当前加载的JSON文件路径
        
        # 初始化UI
        self.init_ui()
        
        # 加载默认单词数据
        self.load_default_words()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('英语闪卡背诵程序 V2.0 🎓✨')
        self.setGeometry(300, 300, 850, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #e3f2fd, stop:1 #f3e5f5);
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #2e7d32;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            .nav-button {
                background-color: #2196F3;
            }
            .nav-button:hover {
                background-color: #0b7dda;
                border: 2px solid #01579b;
            }
            .audio-button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
                min-width: 100px;
            }
            .audio-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb74d, stop:1 #FF9800);
            }
            .flip-button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9C27B0, stop:1 #7B1FA2);
                font-size: 16px;
                padding: 15px 30px;
                min-height: 50px;
            }
            .flip-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #BA68C8, stop:1 #9C27B0);
            }
            .mark-button {
                background-color: #00BCD4;
            }
            .mark-button:hover {
                background-color: #00ACC1;
            }
            .mark-button:checked {
                background-color: #4CAF50;
            }
        """)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title_label = QLabel('📚 英语闪卡背诵 V2.0')
        title_label.setFont(QFont('Microsoft YaHei', 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: #1a237e; margin: 10px;')
        main_layout.addWidget(title_label)
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        # 导入JSON按钮
        self.import_btn = QPushButton('📂 导入JSON')
        self.import_btn.setFont(QFont('Microsoft YaHei', 11))
        self.import_btn.setStyleSheet('background-color: #FF9800; min-height: 35px;')
        self.import_btn.clicked.connect(self.import_json_file)
        control_layout.addWidget(self.import_btn)
        
        # 自动播放复选框
        self.auto_play_check = QCheckBox('🔊 自动播放发音')
        self.auto_play_check.setFont(QFont('Microsoft YaHei', 11))
        self.auto_play_check.stateChanged.connect(self.toggle_auto_play)
        control_layout.addWidget(self.auto_play_check)
        
        control_layout.addStretch()
        
        # 当前文件显示
        self.file_label = QLabel('📄 未加载文件')
        self.file_label.setFont(QFont('Microsoft YaHei', 10))
        self.file_label.setStyleSheet('color: #666; padding: 5px;')
        control_layout.addWidget(self.file_label)
        
        # 学习统计
        self.stats_label = QLabel('✅ 已学: 0 / 0')
        self.stats_label.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        self.stats_label.setStyleSheet('color: #2e7d32; padding: 5px;')
        control_layout.addWidget(self.stats_label)
        
        main_layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 3px solid #2196F3;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                font-size: 14px;
                font-weight: bold;
                color: #1565c0;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #64B5F6);
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 进度信息
        self.progress_label = QLabel('进度: 0 / 0')
        self.progress_label.setFont(QFont('Microsoft YaHei', 12))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet('color: #424242; font-weight: bold;')
        main_layout.addWidget(self.progress_label)
        
        # 闪卡区域
        card_group = QGroupBox('🎴 单词卡片')
        card_group.setFont(QFont('Microsoft YaHei', 13, QFont.Bold))
        card_group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(255, 255, 255, 0.7);
                border: 3px solid #90caf9;
                border-radius: 15px;
                margin-top: 15px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #1565c0;
            }
        """)
        card_layout = QVBoxLayout(card_group)
        card_layout.setSpacing(15)
        
        # 单词显示
        self.word_label = QLabel('')
        self.word_label.setFont(QFont('Arial', 42, QFont.Bold))
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("""
            color: #1a237e; 
            padding: 25px;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            border: 2px solid #bbdefb;
        """)
        self.word_label.setMinimumHeight(120)  # 增加最小高度
        self.word_label.setWordWrap(True)  # 允许自动换行
        self.word_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # 水平扩展
        card_layout.addWidget(self.word_label)
        
        # 音标显示
        self.phonetic_label = QLabel('')
        self.phonetic_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.phonetic_label.setAlignment(Qt.AlignCenter)
        self.phonetic_label.setStyleSheet("""
            color: #5c6bc0; 
            padding: 12px;
            background-color: rgba(227, 242, 253, 0.8);
            border-radius: 8px;
        """)
        card_layout.addWidget(self.phonetic_label)
        
        # 发音按钮区域
        audio_layout = QHBoxLayout()
        audio_layout.addStretch()
        
        self.us_audio_btn = QPushButton('🇺🇸 美式发音')
        self.us_audio_btn.setObjectName('audio-button')
        self.us_audio_btn.clicked.connect(lambda: self.play_audio('us'))
        self.us_audio_btn.setMinimumHeight(45)
        audio_layout.addWidget(self.us_audio_btn)
        
        self.uk_audio_btn = QPushButton('🇬🇧 英式发音')
        self.uk_audio_btn.setObjectName('audio-button')
        self.uk_audio_btn.clicked.connect(lambda: self.play_audio('uk'))
        self.uk_audio_btn.setMinimumHeight(45)
        audio_layout.addWidget(self.uk_audio_btn)
        
        audio_layout.addStretch()
        card_layout.addLayout(audio_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet('background-color: #90caf9;')
        card_layout.addWidget(line)
        
        # 释义显示区域
        self.answer_browser = QTextBrowser()
        self.answer_browser.setFont(QFont('Microsoft YaHei', 14))
        self.answer_browser.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(255, 255, 255, 0.95);
                border: 3px solid #ce93d8;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.answer_browser.setVisible(False)
        card_layout.addWidget(self.answer_browser)
        
        main_layout.addWidget(card_group)
        
        # 翻转按钮
        self.flip_btn = QPushButton('🔄 显示释义 (空格键)')
        self.flip_btn.setObjectName('flip-button')
        self.flip_btn.clicked.connect(self.flip_card)
        main_layout.addWidget(self.flip_btn)
        
        # 标记已学按钮
        self.mark_btn = QPushButton('✓ 标记为已学')
        self.mark_btn.setObjectName('mark-button')
        self.mark_btn.setCheckable(True)
        self.mark_btn.clicked.connect(self.mark_learned)
        main_layout.addWidget(self.mark_btn)
        
        # 导航按钮区域
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)
        
        self.prev_btn = QPushButton('⬅ 上一个 (←)')
        self.prev_btn.setObjectName('nav-button')
        self.prev_btn.clicked.connect(self.previous_word)
        self.prev_btn.setMinimumHeight(50)
        nav_layout.addWidget(self.prev_btn)
        
        self.random_btn = QPushButton('🎲 随机')
        self.random_btn.setCheckable(True)
        self.random_btn.clicked.connect(self.toggle_random)
        self.random_btn.setStyleSheet('background-color: #FF5722; min-height: 50px;')
        nav_layout.addWidget(self.random_btn)
        
        self.next_btn = QPushButton('下一个 (→)')
        self.next_btn.setObjectName('nav-button')
        self.next_btn.clicked.connect(self.next_word)
        self.next_btn.setMinimumHeight(50)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # 底部信息栏
        info_layout = QHBoxLayout()
        
        help_label = QLabel('💡 快捷键: 空格=翻转 | ←=上一个 | →=下一个')
        help_label.setFont(QFont('Microsoft YaHei', 10))
        help_label.setStyleSheet('color: #666;')
        info_layout.addWidget(help_label)
        
        info_layout.addStretch()
        
        self.export_btn = QPushButton('💾 导出JSON')
        self.export_btn.clicked.connect(self.export_current_words)
        self.export_btn.setStyleSheet('background-color: #00BCD4; min-height: 35px;')
        info_layout.addWidget(self.export_btn)
        
        self.reset_btn = QPushButton('🔄 重置')
        self.reset_btn.clicked.connect(self.reset_progress)
        self.reset_btn.setStyleSheet('background-color: #757575; min-height: 35px;')
        info_layout.addWidget(self.reset_btn)
        
        main_layout.addLayout(info_layout)
        
    def load_default_words(self):
        """加载默认单词数据（同目录下的划词翻译收藏夹.json）"""
        json_file = Path(__file__).parent / '划词翻译收藏夹.json'
        
        if json_file.exists():
            self.load_words_from_file(str(json_file))
        else:
            QMessageBox.warning(self, '提示', 
                              '未找到默认单词文件\n\n'
                              '请使用"📂 导入JSON"按钮加载单词文件')
    
    def import_json_file(self):
        """导入JSON文件"""
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '导入单词JSON文件',
            '',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            self.load_words_from_file(file_path)
    
    def load_words_from_file(self, file_path):
        """从指定JSON文件加载单词数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            
            if not isinstance(self.words, list):
                QMessageBox.critical(self, '错误', 
                                   'JSON文件格式错误：根节点必须是数组')
                return
            
            if len(self.words) == 0:
                QMessageBox.warning(self, '警告', 'JSON文件中没有单词数据')
                return
            
            # 验证JSON格式（检查第一个元素是否有必要的字段）
            if len(self.words) > 0:
                first_word = self.words[0]
                if 'text' not in first_word:
                    QMessageBox.critical(self, '错误',
                                       'JSON格式不正确：每个单词必须包含"text"字段')
                    return
            
            # 保存当前文件路径
            self.current_json_file = file_path
            
            # 重置学习状态
            self.current_index = 0
            self.learned_words.clear()
            self.showing_answer = False
            
            # 更新显示
            self.update_display()
            self.update_progress()
            
            # 更新文件标签
            file_name = Path(file_path).name
            self.file_label.setText(f'📄 {file_name}')
            
            # 显示成功消息
            QMessageBox.information(self, '导入成功', 
                                  f'✨ 成功导入 {len(self.words)} 个单词！\n\n'
                                  f'📁 文件: {file_name}\n\n'
                                  f'🎯 开始学习吧！')
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'JSON解析错误', 
                               f'JSON文件格式错误:\n{str(e)}')
        except UnicodeDecodeError:
            QMessageBox.critical(self, '编码错误',
                               '文件编码错误，请确保使用UTF-8编码保存')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载文件失败:\n{str(e)}')
    
    def update_display(self):
        """更新显示内容"""
        if not self.words:
            return
        
        word_data = self.words[self.current_index]
        word_text = word_data.get('text', '')
        results = word_data.get('results', {})
        bing_dict = results.get('BingDictWeb', {})
        
        # 显示单词
        self.word_label.setText(word_text)
        
        # 显示音标
        phonetics = bing_dict.get('phonetic', [])
        if phonetics:
            us_phonetic = ''
            uk_phonetic = ''
            for p in phonetics:
                if p['name'] == '美':
                    us_phonetic = p['value']
                elif p['name'] == '英':
                    uk_phonetic = p['value']
            
            phonetic_text = f"🇺🇸 美 [{us_phonetic}]     🇬🇧 英 [{uk_phonetic}]"
            self.phonetic_label.setText(phonetic_text)
        else:
            self.phonetic_label.setText('暂无音标')
        
        # 准备释义内容
        answer_html = '<div style="line-height: 2.0; font-size: 15px;">'
        
        # 添加词典释义
        dict_entries = bing_dict.get('dict', [])
        if dict_entries:
            answer_html += '<h3 style="color: #1565c0;">📖 词典释义</h3>'
            for entry in dict_entries:
                pos = entry.get('pos', '')
                terms = entry.get('terms', [])
                if pos and terms:
                    answer_html += f'<p style="margin: 10px 0;"><b style="color: #2196F3; font-size: 16px;">{pos}</b><br>'
                    for i, term in enumerate(terms):
                        answer_html += f'&nbsp;&nbsp;{i+1}. {term}<br>'
                    answer_html += '</p>'
        
        # 添加翻译结果
        bing_trans = results.get('Bing', {})
        if bing_trans:
            trans_result = bing_trans.get('result', [])
            if trans_result:
                answer_html += '<hr style="border: 1px solid #ce93d8;">'
                answer_html += f'<h3 style="color: #7b1fa2;">🌐 中文翻译</h3>'
                answer_html += f'<p style="font-size: 18px; color: #2e7d32; font-weight: bold;">'
                answer_html += ', '.join(trans_result) + '</p>'
        
        answer_html += '</div>'
        self.answer_browser.setHtml(answer_html)
        
        # 重置卡片状态
        self.showing_answer = False
        self.answer_browser.setVisible(False)
        self.flip_btn.setText('🔄 显示释义 (空格键)')
        
        # 更新按钮状态
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.words) - 1)
        
        # 检查是否已学
        if self.current_index in self.learned_words:
            self.mark_btn.setChecked(True)
            self.mark_btn.setText('✓ 已标记')
        else:
            self.mark_btn.setChecked(False)
            self.mark_btn.setText('✓ 标记为已学')
        
        # 自动播放发音
        if self.auto_play:
            QTimer.singleShot(500, lambda: self.play_audio('us'))
    
    def flip_card(self):
        """翻转卡片显示/隐藏释义"""
        self.showing_answer = not self.showing_answer
        self.answer_browser.setVisible(self.showing_answer)
        
        if self.showing_answer:
            self.flip_btn.setText('🔄 隐藏释义 (空格键)')
            # 滚动到顶部
            self.answer_browser.verticalScrollBar().setValue(0)
        else:
            self.flip_btn.setText('🔄 显示释义 (空格键)')
    
    def play_audio(self, accent='us'):
        """播放发音 - 优先使用Bing词典音频"""
        if not self.words:
            return
        
        word_data = self.words[self.current_index]
        word_text = word_data.get('text', '')
        results = word_data.get('results', {})
        bing_dict = results.get('BingDictWeb', {})
        
        # 获取Bing词典音频URL
        audio_url = ''
        phonetics = bing_dict.get('phonetic', [])
        for p in phonetics:
            if accent == 'us' and p['name'] == '美':
                audio_url = p.get('ttsURI', '')
                break
            elif accent == 'uk' and p['name'] == '英':
                audio_url = p.get('ttsURI', '')
                break
        
        # 创建并启动TTS线程（传入音频URL）
        self.tts_thread = TTSPlayer(word_text, lang='en', audio_url=audio_url)
        self.tts_thread.finished.connect(self.on_tts_finished)
        self.tts_thread.start()
        
        # 显示提示
        accent_name = '美式' if accent == 'us' else '英式'
        source = 'Bing词典' if audio_url else 'TTS'
        status_msg = f'正在播放: {word_text} ({accent_name} - {source})'
        self.statusBar().showMessage(status_msg, 2000)
    
    def on_tts_finished(self, success):
        """TTS播放完成回调"""
        if success:
            self.statusBar().showMessage('✓ 播放完成', 1000)
        else:
            # 提供更详细的错误提示和解决方案
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle('发音播放失败')
            msg.setText('无法播放发音，请尝试以下解决方案：')
            
            solution_text = (
                '方案1（推荐 - 离线）：\n'
                '   安装 pyttsx3: pip install pyttsx3\n\n'
                '方案2（在线）：\n'
                '   检查网络连接，或使用VPN\n\n'
                '当前将使用系统默认语音（如果可用）。'
            )
            msg.setInformativeText(solution_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    
    def next_word(self):
        """下一个单词"""
        if self.current_index < len(self.words) - 1:
            self.current_index += 1
            self.update_display()
            self.update_progress()
    
    def previous_word(self):
        """上一个单词"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            self.update_progress()
    
    def toggle_random(self):
        """切换随机模式"""
        self.random_mode = not self.random_mode
        
        if self.random_mode:
            self.random_btn.setText('🎲 随机: 开')
            QMessageBox.information(self, '随机模式', 
                                  '✨ 已开启随机模式！\n单词顺序将被打乱。')
        else:
            self.random_btn.setText('🎲 随机: 关')
            self.current_index = 0
        
        self.update_display()
        self.update_progress()
    
    def toggle_auto_play(self, state):
        """切换自动播放"""
        self.auto_play = (state == Qt.Checked)
        if self.auto_play:
            self.statusBar().showMessage('自动播放已开启', 2000)
        else:
            self.statusBar().showMessage('自动播放已关闭', 2000)
    
    def mark_learned(self, checked):
        """标记单词为已学"""
        if checked:
            self.learned_words.add(self.current_index)
            self.mark_btn.setText('✓ 已标记')
            self.statusBar().showMessage(f'✅ 已标记第 {self.current_index + 1} 个单词', 2000)
        else:
            self.learned_words.discard(self.current_index)
            self.mark_btn.setText('✓ 标记为已学')
            self.statusBar().showMessage(f'❌ 取消标记第 {self.current_index + 1} 个单词', 2000)
        
        self.update_progress()
    
    def update_progress(self):
        """更新进度显示"""
        total = len(self.words)
        current = self.current_index + 1
        learned = len(self.learned_words)
        
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f'进度: {current} / {total}')
        self.stats_label.setText(f'✅ 已学: {learned} / {total}')
    
    def reset_progress(self):
        """重置学习进度"""
        reply = QMessageBox.question(self, '确认', 
                                    '确定要重置所有学习进度吗？\n这将清除所有标记。',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_index = 0
            self.learned_words.clear()
            self.showing_answer = False
            self.update_display()
            self.update_progress()
            QMessageBox.information(self, '完成', '✨ 进度已重置！重新开始学习吧！')
    
    def export_current_words(self):
        """导出当前单词列表为JSON"""
        if not self.words:
            QMessageBox.warning(self, '提示', '当前没有单词可导出')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '导出单词JSON文件',
            f'我的单词本_{len(self.words)}词.json',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.words, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, '导出成功',
                                      f'✅ 成功导出 {len(self.words)} 个单词！\n\n'
                                      f'📁 文件: {Path(file_path).name}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导出失败:\n{str(e)}')
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Space:
            self.flip_card()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Down:
            if self.current_index < len(self.words) - 1:
                self.next_word()
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Up:
            if self.current_index > 0:
                self.previous_word()
        elif event.key() == Qt.Key_Home:
            self.current_index = 0
            self.update_display()
            self.update_progress()
        elif event.key() == Qt.Key_End:
            self.current_index = len(self.words) - 1
            self.update_display()
            self.update_progress()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        reply = QMessageBox.question(self, '退出确认', 
                                    f'你已学习了 {len(self.learned_words)} / {len(self.words)} 个单词\n\n'
                                    f'确定要退出吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用程序字体
    font = QFont('Microsoft YaHei', 11)
    app.setFont(font)
    
    window = FlashCardAppV2()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
