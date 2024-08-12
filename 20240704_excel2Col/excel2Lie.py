"""
把excel表按照某列拆分成多个表
具体为保留前六列的前提下，把第六列以后的每一列都形成一个分表 ，并且不存在空元素
"""

import pandas as pd

data = pd.read_excel("D:\\1.xlsx")  # 打开原始工作表
lens = data.shape[1]  # 获取行数 shape[1]获取列数
rows = data.shape[0]  # 获取行数 shape[0]获取行数


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def format_str(content):
    '''只提取字符串中的汉字函数'''
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str + i
    return content_str


df_list_all = []  # 预定义一个空列表存储所有的sheets
for department in range(6, lens):  # 对第六列以后的每一列进行提取
    df_list = pd.DataFrame()  # 定义空pd.dataframe
    for i in range(1, rows):  # 对每一行进行遍历
        if is_number(str(data.iloc[i][department])) == True:  # 判断单元格的值为数字，仅提取有数据的行
            df_list = pd.concat([df_list, data.iloc[[i], [0, 1, 2, 3, 4, 5, department]]], axis=0,
                                ignore_index=True)  # 提取0,1,2,3,4,5，department列
    df_list_all.append(df_list)  # 利用append把所有整理好的分列表进行汇总
writer = pd.ExcelWriter('D:\\new.xlsx')  # 利用pd.ExcelWriter()存多张sheets

# for i in range(len(df_list_all)):  # 保存sheets到new.xlsx
#     name = str(data.iloc[[1], i + 6])  # 提取每一分列第一行对应字符串
#     name = format_str(name)  # 将列名保存下来
#     df_list_all[i].to_excel(writer, sheet_name=name, index=False)  # 注意加上index=FALSE 去掉index列
# writer.save()  # 保存文件

# 确保从第6列（索引为5）开始不会超过data的列数
start_col_index = 6
max_col_index = min(start_col_index + len(df_list_all), data.shape[1])

for i in range(start_col_index, max_col_index):  # 修正循环范围避免越界
    print(data.iloc[0, i])
    name = str(data.iloc[0, i])  # 修正为第0行，提取列名
    print(name)
    # name = format_str(name)  # 将列名保存下来
    # 确保i - start_col_index的值是合法的df_list_all索引
    if i - start_col_index < len(df_list_all):
        df_list_all[i - start_col_index].to_excel(writer, sheet_name=name, index=False)  # 写入Excel，去掉index列
    else:
        print(f"警告：df_list_all 索引 {i - start_col_index} 超出范围，已跳过。")

writer.save()  # 保存文件
