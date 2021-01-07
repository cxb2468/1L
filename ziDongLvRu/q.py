import pyperclip
import pyautogui
import pandas as pd
import easygui as  eg
import time

pyautogui.FAILSAFE =True           # 如果出错，将鼠标移至屏幕左上角可停止程序

#--------------------------------------选择文件,并清洗数据（因为示例文件的数据相对简单，谈不上清洗）
path=eg.fileopenbox(msg='')            #将path =资料打开盒
data=pd.read_excel(path,header=0)      #pandas读取path  指定0行为 header 表头
data = data.iloc[:, 1:5]               #选择1—4位置列即2-5列
[m, n] = data.shape                    #数据shape 确定矩阵的 m,n
print(data)

#--------------------------------------设置各项目在屏幕上的坐标数值（x,y）
with open('信息补充.txt', 'r', encoding='utf-8') as t:
    txt = t.readlines()
    def zuobiao(i):
        x=txt[i].split("=")[-1].strip().split(",")[0]
        y=txt[i].split("=")[-1].strip().split(",")[1]
        a=(int(x),int(y))
        return a
应用坐标 = zuobiao(0)
数据输入坐标1 = zuobiao(1)
数据输入坐标2 = zuobiao(2)
数据输入坐标3 = zuobiao(3)
数据输入坐标4 = zuobiao(4)
按钮坐标 = zuobiao(5)
print(应用坐标)
print(数据输入坐标1)
# 应用坐标=(807,1073)      # 应用图标位置
# 数据输入坐标1=(560,332)   # 项目A
# 数据输入坐标2=(930,331)   # 项目B
# 数据输入坐标3=(556,456)   # 项目C
# 数据输入坐标4=(932,539)   # 项目D
# 按钮坐标=(1168,332)      # 按钮

#--------------------------------------函数设置

def 输入(数据输入坐标,第几个数据,一行数据):
    pyperclip.copy(一行数据[第几个数据])   #将数据复制到剪贴板
    pyautogui.click(数据输入坐标)
    pyautogui.hotkey('ctrl','v')
    # print(一行数据[第几个数据])

def main ():

    # pyautogui.alert(text='This is an alert box.', title='Test')
    # pyautogui.confirm('Enter option.', buttons=['A', 'B', 'C'])
    # a = pyautogui.password('Enter password (text will be hidden)')
    # print(a)
    # b = pyautogui.prompt('input  message')
    # print(b)
    time.sleep(2)
    pyautogui.PAUSE = 0.3
    pyautogui.click(应用坐标)
    for i in range(0,m):
        一行数据=data.loc[i]              #   选择某一行数据
        # print(一行数据)
        输入(数据输入坐标1,0,一行数据)      #   选择第1个数据
        输入(数据输入坐标2,1,一行数据)      #   选择第2个数据
        输入(数据输入坐标3,2,一行数据)      #   选择第3个数据
        输入(数据输入坐标4,3,一行数据)
        pyautogui.click(按钮坐标)
        
main ()

