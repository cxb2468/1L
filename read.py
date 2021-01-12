import pandas  as pd
import easygui as eg
import os,time,pyautogui


path=eg.fileopenbox(msg='')            #将path =资料打开盒
data=pd.read_excel(path,header=5)      #pandas读取path  指定0行为 header 表头
data = data.iloc[:, 0:18]               #选择1—4位置列即2-5列
[m, n] = data.shape                    #数据shape 确定矩阵的 m,n
print(data)


def main():

    time.sleep(2)
    for i in range(0, m):
        rowData = data.loc[i]  # 选择某一行数据
        print(rowData)


main()