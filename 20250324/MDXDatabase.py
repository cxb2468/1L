import sys
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, \
    QPushButton, QScrollArea, QGridLayout, QLabel, QFrame, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor
import sqlite3

import pyttsx3  # 离线语音，简单需求可用
import threading
import json


# A脚本的MDX查询模块（修改为QWidget）
class MDXDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")

    def close(self):
        if self.conn:
            self.conn.close()

    def search_exact(self, keyword):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT paraphrase FROM mdx WHERE entry = ?", (keyword,))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"查询失败: {str(e)}")

    def search_fuzzy(self, keyword):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT paraphrase FROM mdx WHERE entry LIKE ?", (f"%{keyword}%",))
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"查询失败: {str(e)}")


class MDXViewer(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.database = MDXDatabase(db_path)
        self.default_font = QFont("霞鹜文楷 屏幕阅读版", 10)
        self._stylesheet = {}
        self._init_ui()
        self._parse_stylesheet(mdx_stylesheet_text)

    def _init_ui(self):
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("查询...")
        self.input_text.returnPressed.connect(self.on_query)

        self.query_button = QPushButton("查询")
        self.query_button.clicked.connect(self.on_query)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(self.default_font)
        self.text_edit.setHtml("")
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.input_text)
        h_layout.addWidget(self.query_button)
        layout.addLayout(h_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def _parse_stylesheet(self, style_str):
        lines = style_str.splitlines()
        for i in range(0, len(lines), 3):
            number_line = lines[i].strip()
            if not number_line or not number_line.isdigit():
                continue
            number = number_line
            start_tag = lines[i + 1].strip()
            end_tag = lines[i + 2].strip()
            self._stylesheet[number] = (start_tag, end_tag)

    def _substitute_stylesheet(self, txt):
        txt_list = re.split(r"`\d+`", txt)
        tags = re.findall(r"`(\d+)`", txt)
        styled_txt = txt_list[0]
        for i, p in enumerate(txt_list[1:]):
            tag = tags[i]
            style = self._stylesheet.get(tag, ("", ""))
            start, end = style
            if p.endswith('\n'):
                p = p.rstrip('\n')
                styled_txt += f"{start}{p}{end}\n"
            else:
                styled_txt += f"{start}{p}{end}"
        return styled_txt

    def on_query(self, text_specify: str = ''):
        keyword = text_specify or self.input_text.text()
        if not keyword:
            return
        try:
            results = self.database.search_exact(keyword)
            if not results:
                results = self.database.search_fuzzy(keyword)
            if results:
                raw_text = results[0]
                if raw_text.startswith("@@@LINK"):  # 繁体或会跳转的（@@@LINK=书 ）
                    c = raw_text[8:].strip()
                    # print(c,len(c))
                    self.on_query(text_specify=c)
                    return

                styled_text = self._substitute_stylesheet(raw_text)
                self.text_edit.setHtml(styled_text)
            else:
                self.text_edit.setHtml(f"未找到与关键词“{keyword}”匹配的条目。")
        except Exception as e:
            print("错误", str(e))


# B脚本的主界面（整合A的组件）
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.default_font = QFont("霞鹜文楷 屏幕阅读版", 13)
        self.initUI()
        self.common_words = self.load_common_words()
        self.engine = pyttsx3.init()
        self.current_highlight_char = None
        self.stroke_counts = self.read_file_to_dict()

        # 初始化A的查询模块
        self.mdx_viewer = MDXViewer("漢語大字典文字版.db")
        self.right_container = QFrame()
        self.right_container.setLayout(QVBoxLayout())
        self.right_container.layout().addWidget(self.mdx_viewer)
        self.right_container.hide()

        # 布局设置
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_container)
        self.splitter.addWidget(self.right_container)
        self.splitter.setSizes([800, 0])  # 初始隐藏右侧

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

    def initUI(self):
        self.setWindowTitle("生僻字分析器 & 词典查询")
        self.setGeometry(100, 100, 1200, 600)
        self.setFont(self.default_font)

        # 左侧布局
        self.left_container = QWidget()
        left_layout = QVBoxLayout()

        self.input_text = QTextEdit(acceptRichText=False)
        self.input_text.setPlaceholderText("输入文本，例如：古之学者必有师。师者，所以传道受业解惑也。")
        self.input_text.setFont(self.default_font)
        left_layout.addWidget(self.input_text)

        # 按钮行
        button_row = QHBoxLayout()
        self.process_btn = QPushButton("分析文本")
        self.process_btn.clicked.connect(self.process_text)
        self.dictionary_btn = QPushButton("词典")
        self.dictionary_btn.clicked.connect(self.toggle_dictionary)
        button_row.addWidget(self.process_btn)
        button_row.addWidget(self.dictionary_btn)
        left_layout.addLayout(button_row)

        # 按钮显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        left_layout.addWidget(self.scroll_area)

        self.left_container.setLayout(left_layout)

    def load_common_words(self):
        try:
            with open('common_words.txt', 'r', encoding='utf-8') as f:
                words = []
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        content = line.split('】', 1)[1].strip()
                        chars = content.split()
                        words.extend(chars)
                    except IndexError:
                        continue
                return words
        except FileNotFoundError:
            return ['的', '一', '是', '了', '我', '有', '人', '在', '他', '这']

    def process_text(self):
        text = self.input_text.toPlainText()
        unique_chars = set()
        for c in text:
            if self.is_chinese_char(c) and c not in self.common_words:
                unique_chars.add(c)

        # 清空布局
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        row = 0
        col = 0
        for char in unique_chars:
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(0)
            container_layout.setContentsMargins(0, 0, 0, 0)

            btn = QPushButton(char)
            btn.setFixedSize(60, 60)
            btn.setFont(QFont("霞鹜文楷 屏幕阅读版", 12))
            btn.clicked.connect(lambda _, c=char: self.button_clicked(c))

            char_unicode = hex(ord(char))[2:].upper()
            key = f"U+{char_unicode}"
            strokes = self.stroke_counts.get(key, "未知")
            strokes_str = f"笔画数：{strokes}"
            stroke_label = QLabel(strokes_str)
            stroke_label.setStyleSheet("color: gray; font-size: 10px;")
            stroke_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

            container_layout.addWidget(btn)
            container_layout.addWidget(stroke_label)
            container.setLayout(container_layout)
            self.scroll_layout.addWidget(container, row, col)
            col += 1
            if col % 10 == 0:
                row += 1
                col = 0

    def speak(self, char):
        threading.Thread(target=self._speak, args=(char,), daemon=True).start()

    def _speak(self, char):
        self.engine.say(char)
        self.engine.runAndWait()

    def button_clicked(self, c):
        self.speak(c)
        self.highlight_char(c)

        # 触发A的查询
        self.mdx_viewer.input_text.setText(c)
        self.mdx_viewer.on_query()

    def highlight_char(self, char):
        cursor = self.input_text.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        format = cursor.charFormat()
        format.setBackground(QColor(255, 255, 255))
        cursor.setCharFormat(format)

        text = self.input_text.toPlainText()
        current_pos = 0
        while True:
            pos = text.find(char, current_pos)
            if pos == -1:
                break
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
            format = QTextCharFormat()
            format.setBackground(QColor(245, 209, 194))
            cursor.setCharFormat(format)
            current_pos = pos + 1
        cursor.clearSelection()
        self.input_text.setTextCursor(cursor)

    @staticmethod
    def is_chinese_char(c):
        return '\u4e00' <= c <= '\u9fff'

    def read_file_to_dict(self, file_path="unicode_Strokes_data.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def toggle_dictionary(self):

        current_sizes = self.splitter.sizes()
        if self.right_container.isHidden():
            # 显示右侧并设置尺寸为左侧60% 右侧40%
            total_width = sum(current_sizes)
            self.splitter.setSizes([int(total_width * 0.618), int(total_width * 0.382)])
            self.right_container.show()
        else:
            # 隐藏右侧时将尺寸设为0
            self.splitter.setSizes([current_sizes[0] + current_sizes[1], 0])
            self.right_container.hide()


# 风格表（来自A脚本）
mdx_stylesheet_text = """1


2


3
<font color="#950000">

4
</font>

5
<font color="#006AD5"><font size=-2 color=red face="DejaVu Sans"> &#9654; </font>

6
</font>

7
<b>

8
</b>

9


10


11


12


13
<com>

14
</com>

15
</font>

16
<font color=blueviolet>

17
<font color=green>

18
<font color=indigo>

19
<font color=red>

20
<font size=+1 color=maroon><b>

21
</b></font><br>

22
<span style="color: #FFFFFF; background-color: #367F36;font-family: Tahoma"> 

23
</span>  

"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("霞鹜文楷 屏幕阅读版"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())