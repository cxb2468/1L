import os
import time
import pandas as pd

os.chdir('D:\\1L\\Python+excel\\源数据128张表格')


### 打开单个表格


name = '垂钓装备&绑钩器.xlsx'
df = pd.read_excel(name)
df.head()
print(df.head())

### 查看日期范围


df['日期'].unique()



### 计算销售额



df['销售额'] = df['访客数'] * df['转化率'] * df['客单价']
df.head()
print(df.head())


### 单表销售额合并


df_sum = df.groupby('品牌')['销售额'].sum().reset_index()
df_sum.head()
print(df_sum.head())



### 增加行业标签



df_sum['行业'] = name.replace('.xlsx','')
df_sum.head()
print(df_sum.head())



### 搞定单个文件，批量处理只需要循环即可




# #开始时间
# start = time.time()
#
# #存储汇总的结果
# result = pd.DataFrame()
#
# #循环遍历表格名称
# for name in os.listdir():
#     df = pd.read_excel(name)
#     #计算销售额字段
#     df['销售额'] = df['访客数'] * df['转化率'] * df['客单价']
#     #按品牌对细分行业销售额进行汇总
#     df_sum = df.groupby('品牌')['销售额'].sum().reset_index()
#     df_sum['类目'] = name.replace('.xlsx','')
#     result = pd.concat([result,df_sum])
#
# #对最终结果按销售额进行排序
# final = result.groupby('品牌')['销售额'].sum().reset_index().sort_values('销售额',ascending = False)
#
# #结束时间
# end = time.time()
# print('用Python操作所花费时间：{} s'.format(end-start))
#
#
#
# final.head()
#
#
# ### 不显示科学计数法，保留小数点两位数
#
#
# pd.set_option('display.float_format', lambda x: '%.2f' % x)
# final.head()