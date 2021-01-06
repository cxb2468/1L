import pyperclip,re

#从复制的网页中 提取telephone 和 email

#phone 提取规则

# phoneRegex = re.compile(r'''(
#              (\d{3})?                             #前3位
#              (\s|-|\.)                            #-
#              (\d{3})?                             #中3位
#              (\s|-|\.)                            #-
#              (\d{4})                              #后四位
#              (\s*(ext|x|ext.)\s*(\d{2,5}))?       #其他位置
#
# )''',re.VERBOSE)


phoneRegex =re.compile(r'''(\d{3})?(\n)(\d{4})?(\n)(\d{4})''')






#email 提取规则
emailRegex = re.compile(r'''(
             [a-zA-Z0-9._%+-]+     #用户名
             @                     #@
             [a-zA-Z0-9.-]+        #域名
             (\.[a-zA-Z]{2,4})     #.com 类型

)''',re.VERBOSE)

#从剪切板上找到 match 规则的数据
text ="162\n5649\n9991\n新号现卡\n贵阳电信网络\n低消：6/月\n¥500\n162\n5649\n9992\n新号现卡\n贵阳电信网络\n低消：6/月\n¥500\n162\n5649\n1414    123456123@qq.com   dadasd@qq.com"

# text = str(pyperclip.paste())
matches =[]



# for groups in phoneRegex.findall(text):
#     print(groups)
#
#     phoneNum = "-".join([groups[1],groups[3],groups[5]])
#     if groups[8] != "":
#         phoneNum += " x" + groups[8]
#     matches.append(phoneNum)

mo =phoneRegex.findall(text)
print(mo)


for groups in phoneRegex.findall(text):
    print(groups)
    phoneNum = "".join([groups[0],groups[2],groups[4]])
    # matches.apppend(phoneNum)

for groups in emailRegex.findall(text):
    matches.append(groups[0])
    print(groups)
print(matches)



#将找到的数据 粘贴至 粘贴板
if len(matches) > 0 :
    pyperclip.copy("\n".join(matches))
    print("已复制到剪切板")
    print("\n".join(matches))
else:
    print("电话 和email 没找到！！！")