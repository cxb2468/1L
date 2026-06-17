"""
英语闪卡背诵程序
功能：从划词翻译收藏夹JSON文件中加载单词，提供带发音的闪卡学习体验
作者：工程师 & 英语老师
日期：2026-05-12
"""

import json
import sys
import random
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextBrowser,
                             QGroupBox, QMessageBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont, QColor, QIcon


class FlashCardApp(QMainWindow):
    """英语闪卡主应用窗口"""
    
    def __init__(self):
        super().__init__()
        self.words = []
        self.current_index = 0
        self.showing_answer = False
        self.correct_count = 0
        self.random_mode = False
        
        # 初始化UI
        self.init_ui()
        
        # 加载单词数据
        self.load_words()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('英语闪卡背诵程序 🎓')
        self.setGeometry(300, 300, 800, 650)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f4f8;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            .nav-button {
                background-color: #2196F3;
            }
            .nav-button:hover {
                background-color: #0b7dda;
            }
            .audio-button {
                background-color: #FF9800;
                min-width: 80px;
            }
            .audio-button:hover {
                background-color: #e68900;
            }
            .flip-button {
                background-color: #9C27B0;
                font-size: 16px;
                padding: 15px 30px;
            }
            .flip-button:hover {
                background-color: #7b1fa2;
            }
        """)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('📚 英语闪卡背诵')
        title_label.setFont(QFont('Microsoft YaHei', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: #2c3e50; margin: 10px;')
        main_layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 进度信息
        self.progress_label = QLabel('进度: 0 / 0')
        self.progress_label.setFont(QFont('Microsoft YaHei', 11))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet('color: #555;')
        main_layout.addWidget(self.progress_label)
        
        # 闪卡区域
        card_group = QGroupBox('单词卡片')
        card_group.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        card_layout = QVBoxLayout(card_group)
        
        # 单词显示
        self.word_label = QLabel('')
        self.word_label.setFont(QFont('Arial', 36, QFont.Bold))
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet('color: #2c3e50; padding: 20px;')
        self.word_label.setMinimumHeight(80)
        card_layout.addWidget(self.word_label)
        
        # 音标显示
        self.phonetic_label = QLabel('')
        self.phonetic_label.setFont(QFont('Arial', 16))
        self.phonetic_label.setAlignment(Qt.AlignCenter)
        self.phonetic_label.setStyleSheet('color: #666; padding: 10px;')
        card_layout.addWidget(self.phonetic_label)
        
        # 发音按钮区域
        audio_layout = QHBoxLayout()
        audio_layout.addStretch()
        
        self.us_audio_btn = QPushButton('🇺🇸 美音')
        self.us_audio_btn.setObjectName('audio-button')
        self.us_audio_btn.clicked.connect(lambda: self.play_audio('us'))
        audio_layout.addWidget(self.us_audio_btn)
        
        self.uk_audio_btn = QPushButton('🇬🇧 英音')
        self.uk_audio_btn.setObjectName('audio-button')
        self.uk_audio_btn.clicked.connect(lambda: self.play_audio('uk'))
        audio_layout.addWidget(self.uk_audio_btn)
        
        audio_layout.addStretch()
        card_layout.addLayout(audio_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet('background-color: #ddd;')
        card_layout.addWidget(line)
        
        # 释义显示区域
        self.answer_browser = QTextBrowser()
        self.answer_browser.setFont(QFont('Microsoft YaHei', 13))
        self.answer_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 15px;
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
        
        # 导航按钮区域
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton('⬅ 上一个')
        self.prev_btn.setObjectName('nav-button')
        self.prev_btn.clicked.connect(self.previous_word)
        nav_layout.addWidget(self.prev_btn)
        
        self.random_btn = QPushButton('🎲 随机模式: 关')
        self.random_btn.setCheckable(True)
        self.random_btn.clicked.connect(self.toggle_random)
        self.random_btn.setStyleSheet('background-color: #FF5722;')
        nav_layout.addWidget(self.random_btn)
        
        self.next_btn = QPushButton('下一个 ➡')
        self.next_btn.setObjectName('nav-button')
        self.next_btn.clicked.connect(self.next_word)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # 底部统计信息
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel('✅ 正确: 0 | ❌ 错误: 0')
        self.stats_label.setFont(QFont('Microsoft YaHei', 11))
        self.stats_label.setStyleSheet('color: #555;')
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        self.reset_btn = QPushButton('🔄 重置进度')
        self.reset_btn.clicked.connect(self.reset_progress)
        self.reset_btn.setStyleSheet('background-color: #757575;')
        stats_layout.addWidget(self.reset_btn)
        
        main_layout.addLayout(stats_layout)
        
    def load_words(self):
        """从JSON文件加载单词数据"""
        json_file = Path(__file__).parent / '划词翻译收藏夹.json'
        
        if not json_file.exists():
            QMessageBox.critical(self, '错误', f'找不到文件: {json_file}')
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            
            if len(self.words) == 0:
                QMessageBox.warning(self, '警告', 'JSON文件中没有单词数据')
                return
            
            self.current_index = 0
            self.update_display()
            self.update_progress()
            
            QMessageBox.information(self, '加载成功', 
                                  f'成功加载 {len(self.words)} 个单词！\n开始学习吧！')
            
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
            
            phonetic_text = f"美 [{us_phonetic}]   英 [{uk_phonetic}]"
            self.phonetic_label.setText(phonetic_text)
        else:
            self.phonetic_label.setText('')
        
        # 准备释义内容
        answer_html = '<div style="line-height: 1.8;">'
        
        # 添加词典释义
        dict_entries = bing_dict.get('dict', [])
        if dict_entries:
            for entry in dict_entries:
                pos = entry.get('pos', '')
                terms = entry.get('terms', [])
                if pos and terms:
                    answer_html += f'<p><b style="color: #2196F3;">{pos}</b> '
                    answer_html += '; '.join(terms) + '</p>'
        
        # 添加翻译结果
        bing_trans = results.get('Bing', {})
        if bing_trans:
            trans_result = bing_trans.get('result', [])
            if trans_result:
                answer_html += f'<p style="margin-top: 15px;"><b style="color: #4CAF50;">翻译:</b> '
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
    
    def flip_card(self):
        """翻转卡片显示/隐藏释义"""
        self.showing_answer = not self.showing_answer
        self.answer_browser.setVisible(self.showing_answer)
        
        if self.showing_answer:
            self.flip_btn.setText('🔄 隐藏释义 (空格键)')
        else:
            self.flip_btn.setText('🔄 显示释义 (空格键)')
    
    def play_audio(self, accent='us'):
        """播放发音（模拟功能）"""
        if not self.words:
            return
        
        word_data = self.words[self.current_index]
        results = word_data.get('results', {})
        bing_dict = results.get('BingDictWeb', {})
        phonetics = bing_dict.get('phonetic', [])
        
        # 查找对应的音频URL
        audio_url = None
        for p in phonetics:
            if accent == 'us' and p['name'] == '美':
                audio_url = p.get('ttsURI', '')
                break
            elif accent == 'uk' and p['name'] == '英':
                audio_url = p.get('ttsURI', '')
                break
        
        if audio_url:
            # 注意：这里的TTS URL是相对路径，需要 Bing Dict 的完整URL
            # 实际使用时需要使用完整的URL或使用其他TTS服务
            full_url = f'https://www.bing.com{audio_url}'
            QMessageBox.information(self, '发音提示', 
                                  f'播放{word_data["text"]}的{"美式" if accent == "us" else "英式"}发音\n\n'
                                  f'音频URL: {full_url}\n\n'
                                  f'(在实际应用中，这里会调用音频播放器)')
        else:
            QMessageBox.warning(self, '提示', '该单词暂无音频数据')
    
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
            self.random_btn.setText('🎲 随机模式: 开')
            # 打乱单词顺序
            indices = list(range(len(self.words)))
            random.shuffle(indices)
            self.shuffled_indices = indices
            self.current_index = 0
            QMessageBox.information(self, '随机模式', '已开启随机模式，单词顺序已打乱！')
        else:
            self.random_btn.setText('🎲 随机模式: 关')
            self.current_index = 0
        
        self.update_display()
        self.update_progress()
    
    def update_progress(self):
        """更新进度显示"""
        total = len(self.words)
        current = self.current_index + 1
        
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f'进度: {current} / {total}')
    
    def reset_progress(self):
        """重置学习进度"""
        reply = QMessageBox.question(self, '确认', 
                                    '确定要重置学习进度吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_index = 0
            self.correct_count = 0
            self.showing_answer = False
            self.update_display()
            self.update_progress()
            QMessageBox.information(self, '完成', '进度已重置！')
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Space:
            self.flip_card()
        elif event.key() == Qt.Key_Right:
            if self.current_index < len(self.words) - 1:
                self.next_word()
        elif event.key() == Qt.Key_Left:
            if self.current_index > 0:
                self.previous_word()
        else:
            super().keyPressEvent(event)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格
    
    # 设置应用程序字体
    font = QFont('Microsoft YaHei', 10)
    app.setFont(font)
    
    window = FlashCardApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
