# -*- coding:utf-8 -*-
import wx
import pyperclip
import os
import zipfile
import tarfile
from collections import defaultdict
import rarfile
import py7zr


def scan_file_types(start_dir):
    file_types = defaultdict(int)
    total_files = 0

    def process_archive(archive_path):
        nonlocal total_files
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                for file_info in zip_file.infolist():
                    ext = os.path.splitext(file_info.filename)[1].lower()
                    file_types[ext] += 1
                    total_files += 1
        elif tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, 'r') as tar_file:
                for file_info in tar_file.getmembers():
                    ext = os.path.splitext(file_info.name)[1].lower()
                    file_types[ext] += 1
                    total_files += 1
        elif rarfile.is_rarfile(archive_path):
            with rarfile.RarFile(archive_path, 'r') as rar_file:
                for file_info in rar_file.infolist():
                    ext = os.path.splitext(file_info.filename)[1].lower()
                    file_types[ext] += 1
                    total_files += 1
        elif archive_path.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, mode='r') as szf:
                for file_info in szf.list():
                    ext = os.path.splitext(file_info.filename)[1].lower()
                    file_types[ext] += 1
                    total_files += 1

    for dirpath, dirnames, filenames in os.walk(start_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in {'.zip', '.tar', '.tar.gz', '.tar.bz2', '.gz', '.bz2', '.rar', '.7z'}:
                process_archive(filepath)
            else:
                file_types[ext] += 1
                total_files += 1
    # 去重
    all_file_types = ", ".join(sorted(key for key in file_types.keys() if key)).replace(".", "")
    return all_file_types, total_files


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='原创：吾爱qianaonan', size=(427, 168), name='frame', style=541072384)
        self.启动窗口 = wx.Panel(self)
        self.Centre()
        self.标签1 = wx.StaticText(self.启动窗口, size=(80, 24), pos=(14, 13), label='选择目录', name='staticText', style=2321)
        self.编辑框1 = wx.TextCtrl(self.启动窗口, size=(222, 22), pos=(87, 10), value='', name='text', style=16)
        self.按钮1 = wx.Button(self.启动窗口, size=(61, 32), pos=(319, 5), label='选择目录', name='button')
        self.按钮1.Bind(wx.EVT_BUTTON, self.按钮1_按钮被单击)
        self.按钮2 = wx.Button(self.启动窗口, size=(61, 32), pos=(319, 75), label='一键复制', name='button')
        self.按钮2.Bind(wx.EVT_BUTTON, self.按钮2_按钮被单击)
        self.按钮3 = wx.Button(self.启动窗口, size=(61, 32), pos=(319, 41), label='一键复制', name='button')
        self.按钮3.Bind(wx.EVT_BUTTON, self.按钮3_按钮被单击)
        self.标签2 = wx.StaticText(self.启动窗口, size=(80, 24), pos=(5, 48), label='文件类型', name='staticText', style=2321)
        self.标签3 = wx.StaticText(self.启动窗口, size=(80, 24), pos=(4, 79), label='文件数量', name='staticText', style=2321)
        self.编辑框3 = wx.TextCtrl(self.启动窗口, size=(222, 22), pos=(87, 45), value='', name='text', style=0)
        self.编辑框4 = wx.TextCtrl(self.启动窗口, size=(222, 22), pos=(87, 75), value='', name='text', style=0)

    def 按钮1_按钮被单击(self, event):
        with wx.DirDialog(self, "选择一个目录", style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                selected_path = dialog.GetPath()
                self.编辑框1.SetValue(selected_path)
        self.编辑框3.SetValue(scan_file_types(self.编辑框1.GetValue())[0])
        self.编辑框4.SetValue(str(scan_file_types(self.编辑框1.GetValue())[1]))

    def 按钮2_按钮被单击(self, event):
        pyperclip.copy(self.编辑框4.GetValue())

    def 按钮3_按钮被单击(self, event):
        pyperclip.copy(self.编辑框3.GetValue())


class myApp(wx.App):
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show(True)
        return True


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()