
#
# while True:
#     print("输入你的年龄：")
#     age = input()
#     if age.isdecimal():
#         break
#     print("请确定输入的数字！！！")
#
# while True:
#     print("选择一个新密码（仅字母和数字）：")
#     password = input()
#     if password.isalnum():
#         break
#     print("请确定输入的是 字母和数字！！！")
#
#
#
#






spams = ["banana","apples","tofu","cats"]


def douhao(sp):
    gaiBian = "and "+sp[-1]
    sp[-1] =gaiBian
    print(sp)
    for i in range(len(sp)):
        sp[i] =  sp[i]+", "
        print(sp[i])
    print(" ")
    str = " ".join(sp)
    print(str)

douhao(spams)
