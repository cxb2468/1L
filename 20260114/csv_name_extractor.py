import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QMessageBox, QGroupBox, QFormLayout, QSplitter)
from PyQt5.QtCore import Qt


class CSVNameExtractorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_file_path = ""
        self.names_list = []
    
    def init_ui(self):
        self.setWindowTitle('CSV/Excel名称提取工具')
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部控制区域
        top_group = QGroupBox("操作区")
        top_layout = QHBoxLayout(top_group)
        
        # 文件选择按钮
        self.select_file_btn = QPushButton('选择CSV/Excel文件')
        self.select_file_btn.clicked.connect(self.select_file)
        
        # 处理按钮
        self.process_btn = QPushButton('提取名称列')
        self.process_btn.clicked.connect(self.process_file)
        self.process_btn.setEnabled(False)
        
        # 复制按钮
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.clicked.connect(self.copy_result)
        self.copy_btn.setEnabled(False)
        
        # 清空按钮
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_all)
        
        top_layout.addWidget(self.select_file_btn)
        top_layout.addWidget(self.process_btn)
        top_layout.addWidget(self.copy_btn)
        top_layout.addWidget(self.clear_btn)
        
        # 创建分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：文件信息
        left_group = QGroupBox("文件信息")
        left_layout = QVBoxLayout(left_group)
        
        self.file_info_display = QTextEdit()
        self.file_info_display.setReadOnly(True)
        left_layout.addWidget(self.file_info_display)
        
        # 右侧：结果显示
        right_group = QGroupBox("提取结果")
        right_layout = QVBoxLayout(right_group)
        
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        right_layout.addWidget(self.result_display)
        
        # 添加到分割器
        main_splitter.addWidget(left_group)
        main_splitter.addWidget(right_group)
        main_splitter.setSizes([300, 700])
        
        # 添加到主布局
        main_layout.addWidget(top_group)
        main_layout.addWidget(main_splitter)
        
        # 状态栏
        self.statusBar().showMessage('就绪')
    
    def select_file(self):
        """选择CSV或Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择CSV或Excel文件', 
            '', 
            'CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        
        if file_path:
            self.current_file_path = file_path
            self.process_btn.setEnabled(True)
            
            # 显示文件信息
            file_info = f"文件路径: {file_path}\n"
            file_info += f"文件大小: {os.path.getsize(file_path)} 字节\n"
            file_info += f"修改时间: {self.format_time(os.path.getmtime(file_path))}\n"
            
            try:
                # 读取文件并显示前几行
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                file_info += f"行数: {len(df)}\n"
                file_info += f"列数: {len(df.columns)}\n"
                file_info += f"列名: {', '.join(df.columns.tolist())}\n\n"
                file_info += "前5行数据预览:\n"
                file_info += str(df.head())
            except Exception as e:
                file_info += f"读取文件时出错: {str(e)}"
            
            self.file_info_display.setPlainText(file_info)
            self.statusBar().showMessage(f'已选择文件: {os.path.basename(file_path)}')
    
    def format_time(self, timestamp):
        """格式化时间戳"""
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def process_file(self):
        """处理文件，提取名称列"""
        if not self.current_file_path:
            QMessageBox.warning(self, '警告', '请先选择一个文件！')
            return
        
        try:
            # 读取文件
            if self.current_file_path.endswith('.csv'):
                df = pd.read_csv(self.current_file_path)
            else:
                df = pd.read_excel(self.current_file_path)
            
            # 尝试查找名称列（可能的列名）
            possible_name_columns = ['name', 'Name', 'NAME', '软件名称', '名称', '应用名称', '应用程序']
            
            name_col = None
            for col in possible_name_columns:
                if col in df.columns:
                    name_col = col
                    break
            
            if name_col is None:
                # 如果没有找到标准名称列，则提示用户选择
                available_columns = list(df.columns)
                selected_col, ok = self.select_column_dialog(available_columns)
                if ok and selected_col:
                    name_col = selected_col
                else:
                    QMessageBox.warning(self, '警告', '未找到名称列，请手动选择列！')
                    return
            
            # 提取名称列数据
            names_series = df[name_col].dropna()  # 移除NaN值
            self.names_list = names_series.astype(str).tolist()  # 转换为字符串列表
            
            # 用逗号拼接
            result_str = ','.join(self.names_list)
            
            # 显示结果
            self.result_display.setPlainText(result_str)
            
            # 启用复制按钮
            self.copy_btn.setEnabled(True)
            
            # 更新状态
            self.statusBar().showMessage(f'成功提取 {len(self.names_list)} 个名称')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'处理文件时出错: {str(e)}')
    
    def copy_result(self):
        """复制提取结果到剪贴板"""
        result_text = self.result_display.toPlainText()
        if result_text:
            # 在结果前添加指定文本
            full_text = "你是一个软件专家，请检查以下哪些软件 需要购买许可证才可以公司使用？\n" + result_text
            clipboard = QApplication.clipboard()
            clipboard.setText(full_text)
            self.statusBar().showMessage('结果已复制到剪贴板', 2000)  # 2秒后自动清除消息
        else:
            self.statusBar().showMessage('没有可复制的结果', 2000)
    
    def select_column_dialog(self, columns):
        """让用户选择列的对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('选择名称列')
        dialog_layout = QVBoxLayout(dialog)
        
        label = QLabel('请选择名称列:')
        combo_box = QComboBox()
        combo_box.addItems(columns)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        dialog_layout.addWidget(label)
        dialog_layout.addWidget(combo_box)
        dialog_layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            return combo_box.currentText(), True
        else:
            return None, False
    
    def clear_all(self):
        """清空所有内容"""
        self.current_file_path = ""
        self.names_list = []
        self.file_info_display.clear()
        self.result_display.clear()
        self.process_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)  # 清空时也禁用复制按钮
        self.statusBar().showMessage('已清空')
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, 
            '确认退出', 
            '确定要退出程序吗？', 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    window = CSVNameExtractorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()