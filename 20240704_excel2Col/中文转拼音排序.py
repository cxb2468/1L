# -*- coding: utf-8 -*-
from itertools import chain
from pypinyin import pinyin, Style
import pandas as pd

'''
公众号：Python数据分析实战
'''


def to_pinyin(s):
    '''转拼音
    :param s: 字符串或列表
    :type s: str or list
    :return: 拼音字符串
    >>> to_pinyin('你好吗') 'ni3hao3ma'
    >>> to_pinyin(['你好', '吗'])'ni3hao3ma'
    '''

    return ''.join(chain.from_iterable(pinyin(s, style=Style.TONE3)))


if __name__ == '__main__':
    # print(sorted(['美国', '中国', '日本']))
    # print(sorted(['美国', '中国', '日本'], key=to_pinyin))

    df_tmp = pd.DataFrame([
        {"aa": "data1", "cnt": "总开通", "b": "20"}, {"aa": "data2", "cnt": "魅力惠B3308", "b": "22"},
        {"aa": "data2", "cnt": "魅力惠B3305", "b": "22"},
        {"aa": "data2", "cnt": "淘宝汇总", "b": "22"}, {"aa": "data4", "cnt": "你好a", "b": "22"},
        {"aa": "data4", "cnt": "你好b", "b": "22"}
    ])

    # print(df_tmp)
    # pandas默认排序--仍为乱序
    df_tmp.sort_values(by="cnt", inplace=True)
    print(df_tmp)

    # 获取dataframe指定列数值，并以列表形式返回
    sort_values_list = df_tmp[:]["cnt"].values.tolist()
    # 中文排序
    new_list = sorted(sort_values_list, key=to_pinyin)
    # print(new_list)

    # 自定义排序 (先取列内容 去重，按给定顺序排序)
    df_tmp['cnt'] = pd.Categorical(df_tmp['cnt'], categories=new_list, ordered=True)
    df_tmp.sort_values(by='cnt', inplace=True)

    # 重置行序号 index
    df_tmp.reset_index(drop=True, inplace=True)
    print(df_tmp)

    '''
          aa       cnt   b
    0  data2  魅力惠B3305  22
    1  data2  魅力惠B3308  22
    2  data4       你好a  22
    3  data4       你好b  22
    4  data2      淘宝汇总  22
    5  data1       总开通  20
    '''