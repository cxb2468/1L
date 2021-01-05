import pyperclip
import pyautogui
import pandas as pd
import easygui as  eg
import time,datetime


pyautogui.FAILSAFE = True  # 如果出错，将鼠标移至屏幕左上角可停止程序




# --------------------------------------选择文件,并清洗数据（因为示例文件的数据相对简单，谈不上清洗）
# path = eg.fileopenbox(msg='')
# data = pd.read_excel(path, header=0)
# data = data.iloc[:, 1:5]  # 选择2-5列
# [m, n] = data.shape
# print(data)
# --------------------------------------设置各项目在屏幕上的坐标数值（x,y）
with open('坐标信息.txt', 'r', encoding='utf-8') as t:
    txt = t.readlines()
    def zb(i):
        x = txt[i].split("=")[-1].strip().split(",")[0]
        y = txt[i].split("=")[-1].strip().split(",")[1]
        a = (int(x), int(y))
        return a
app=zb(0)
gongGao=zb(1)
quFu=zb(2)
touxiang=zb(3)
miJing=zb(4)
xiongGui=zb(5)
anDong=zb(6)
luoJi=zb(7)
niMu=zb(8)
xgQiu=zb(9)
saoDang=zb(10)
queRenX=zb(11)
fanHuiX=zb(12)
saoDangXG=zb(13)
nvShen=zb(14)
qiuX=zb(15)
saoDangX=zb(16)
jiBan=zb(17)
shenDian=zb(18)
qiuSD=zb(19)
mo=zb(20)
fu=zb(21)
qiZhi=zb(22)
qianDaoX=zb(23)
mianBao=zb(24)
lianBing =zb(25)
zhuJiao = zb(26)
weiTuo1 = zb(27)
xiaoShi = zb(28)
xuanZe = zb(29)
yingXiong1=zb(30)
queDing=zb(31)
queRen = zb(32)
weiTuo2 = zb(33)
yingXiong2 = zb(34)
weiTuo3 = zb(35)
yingXiong3 = zb(36)



print(app)
print(gongGao)

#颜色值
color_gongGao = (176,158,137)
color_mo =(8, 4, 5)
color_fu=(255, 255, 123)
color_miJing=(184, 182, 168)
color_qiZhi=(109, 117, 72)
color_mianBao=(247, 240, 219)
color_lianBing = (41,28,8)
color_weiTuo1_red = (174,70,95)
color_weiTuo1_blue = (86,195,230)


# 应用坐标=(807,1073)      # 应用图标位置
# 数据输入坐标1=(560,332)   # 项目A
# 数据输入坐标2=(930,331)   # 项目B
# 数据输入坐标3=(556,456)   # 项目C
# 数据输入坐标4=(932,539)   # 项目D
# 按钮坐标=(1168,332)      # 按钮

# --------------------------------------函数设置
#
# def 输入(数据输入坐标, 第几个数据, 一行数据):
#     pyperclip.copy(一行数据[第几个数据])  # 将数据复制到剪贴板
#     pyautogui.click(数据输入坐标)
#     pyautogui.hotkey('ctrl', 'v')
#     # print(一行数据[第几个数据])


#while当颜色 非  match时 ，一直sleep 0.5s，match则执行下一步
def  is_color(x,y,color_x):
     pyautogui.moveTo(x, y)
     while not pyautogui.pixelMatchesColor(x, y,color_x):
        time.sleep(0.5)
        # print(pyautogui.pixelMatchesColor(x, y,color_x))
        # print(pyautogui.position())
        # print(pyautogui.screenshot().getpixel((pyautogui.position())))

def autoZhuJiao(x,y):
    pyautogui.click(xiaoShi)
    pyautogui.click(xuanZe)
    pyautogui.click(x,y)
    pyautogui.click(queDing)
    pyautogui.click(queRen)
    time.sleep(2)



def main():
    time.sleep(2)
    pyautogui.PAUSE = 1.3
    pyautogui.doubleClick(app)

    # 1715,120点像素 不等于 该点像素时 sleep 0.5,如果等于，则跳出while 循环。
    is_color(gongGao[0],gongGao[1],color_gongGao)
    pyautogui.click(gongGao)

    #有个 账号登录中画面，需要判断像素点
    is_color(mo[0],mo[1],color_mo)
    pyautogui.click(quFu)

    #while判断头像像素
    is_color(fu[0],fu[1],color_fu)
    pyautogui.click(touxiang)

    #选完区服中角色后，判断像素点是否等于 1000,580像素
    is_color(mo[0], mo[1], color_mo)
    pyautogui.click(touxiang)
    #进入签到奖励界面  判断面包的像素 ，while 非面包像素，则一直点击 叉叉 标记！

    pyautogui.moveTo(mianBao[0], mianBao[1])
    while not pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao):
        pyautogui.click(qianDaoX)
        pyautogui.moveTo(mianBao[0], mianBao[1])
        time.sleep(0.3)
        print(pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao))
        print(pyautogui.position())
        print(pyautogui.screenshot().getpixel((pyautogui.position())))


    #判断 勇气的旗帜像素 ，确定有没有买月卡
    pyautogui.moveTo(qiZhi)
    if pyautogui.pixelMatchesColor(qiZhi[0], qiZhi[1],color_qiZhi):
        # 先要补充一个面包
        pyautogui.click(1438,45)
        pyautogui.click(784,675)

        # 秘境   判断是否在秘境像素的上
        pyautogui.click(miJing)
        is_color(miJing[0],miJing[1],color_miJing)
        pyautogui.click(miJing)

        #兄贵
        pyautogui.click(xiongGui)
        #周1、4、7 andong  周2、5 luoji  周3、6 nimu
        day = datetime.datetime.now().isoweekday()
        if day == 2 or day ==5:
            pyautogui.click(luoJi)
        elif day ==3 or day ==6:
            pyautogui.click(niMu)
        else:
            pyautogui.click(anDong)

        time.sleep(1)
        pyautogui.click(xgQiu)
        pyautogui.click(saoDangX)
        pyautogui.click(queRenX)    #第一次扫荡
        time.sleep(1)
        pyautogui.click(saoDangXG)  #第二次扫荡
        time.sleep(1)
        pyautogui.click(saoDangXG)  #第三次扫荡
        time.sleep(1)
        #pyautogui.click(800,690) #取消按钮
        pyautogui.click(fanHuiX)
        pyautogui.click(fanHuiX)

        #女神
        pyautogui.click(nvShen)
        pyautogui.click(qiuX)
        pyautogui.click(saoDangX)
        pyautogui.click(queRenX)    #第一次扫荡
        time.sleep(1)
        pyautogui.click(saoDangXG)  #第二次扫荡
        time.sleep(1)
        pyautogui.click(fanHuiX)
        pyautogui.click(fanHuiX)
    else:
        # 秘境
        # 判断是否在秘境像素的上
        is_color(miJing[0], miJing[1], color_miJing)
        pyautogui.click(miJing)

        # 兄贵
        pyautogui.click(xiongGui)
        # 周1、4、7 andong  周2、5 luoji  周3、6 nimu
        day = datetime.datetime.now().isoweekday()
        if day == 2 or day == 5:
            pyautogui.click(luoJi)
        elif day == 3 or day == 6:
            pyautogui.click(niMu)
        else:
            pyautogui.click(anDong)

        time.sleep(1)
        pyautogui.click(xgQiu)
        pyautogui.click(saoDangX)
        pyautogui.click(queRenX)  # 第一次扫荡
        time.sleep(1)
        pyautogui.click(saoDangXG)  # 第二次扫荡
        time.sleep(1)
        # pyautogui.click(800,690) #取消按钮
        pyautogui.click(fanHuiX)
        pyautogui.click(fanHuiX)

        # 女神
        pyautogui.click(nvShen)
        pyautogui.click(qiuX)
        pyautogui.click(saoDangX)
        pyautogui.click(queRenX)  # 第一次扫荡
        time.sleep(1)
        pyautogui.click(fanHuiX)
        pyautogui.click(fanHuiX)

    #拖动秘境 进入羁绊
    pyautogui.click(220,1055)#(返回后起点)
    #pyautogui.dragTo(x=427, y=535, duration=3, button='left')
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    #羁绊
    pyautogui.click(jiBan)
    pyautogui.click(qiuX)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    # 拖动秘境 进入神殿
    pyautogui.click(220, 1055)  # (返回后起点)
    # pyautogui.dragTo(x=427, y=535, duration=3, button='left')
    pyautogui.dragTo(x=220, y=100, duration=4, button='left')
    #神殿
    pyautogui.click(shenDian)
    pyautogui.click(qiuSD)
    pyautogui.click(saoDangX)
    pyautogui.click(queRenX)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)


   #任务
    time.sleep(1)
   #判断下是否回到主界面
    pyautogui.moveTo(mianBao[0], mianBao[1])
    while not pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao):
        #pyautogui.click(fanHuiX)
        pyautogui.moveTo(mianBao[0], mianBao[1])
        time.sleep(0.3)
        print(pyautogui.pixelMatchesColor(mianBao[0], mianBao[1], color_mianBao))
        print(pyautogui.position())
        print(pyautogui.screenshot().getpixel((pyautogui.position())))

    pyautogui.click(1066,991)
    time.sleep(2)
    pyautogui.click(1700,925)
    time.sleep(2)
    pyautogui.click(fanHuiX)
    pyautogui.click(fanHuiX)

    #练兵
    is_color(lianBing[0], lianBing[1], color_lianBing)
    pyautogui.click(lianBing)
    pyautogui.click(zhuJiao)
    time.sleep(1)

    # 如果委托颜色为红色，返回主界面；否则 开始委托1、委托2、委托3
    #   蓝色 未执行  0
    #   红色 执行中  0.5
    #   黄色 已执行完成 1
    pyautogui.moveTo(weiTuo1)
    if pyautogui.pixelMatchesColor(weiTuo1[0], weiTuo1[1], color_weiTuo1_red):
        pyautogui.click(fanHuiX)
    elif pyautogui.pixelMatchesColor(weiTuo1[0], weiTuo1[1], color_weiTuo1_blue):
        pyautogui.click(weiTuo1)
        autoZhuJiao(yingXiong1[0], yingXiong1[1])
        pyautogui.click(weiTuo2)
        autoZhuJiao(yingXiong2[0], yingXiong2[1])
        pyautogui.click(weiTuo3)
        autoZhuJiao(yingXiong3[0], yingXiong3[1])
        pyautogui.click(fanHuiX)
    else:
        pyautogui.click(weiTuo1,clicks=2)
        autoZhuJiao(yingXiong1[0], yingXiong1[1])
        pyautogui.click(weiTuo2,clicks=2)
        autoZhuJiao(yingXiong2[0], yingXiong2[1])
        pyautogui.click(weiTuo3,clicks=2)
        autoZhuJiao(yingXiong3[0], yingXiong3[1])
        pyautogui.click(fanHuiX)

    #好友
    pyautogui.click(60, 615)
    time.sleep(1.5)
    pyautogui.click(380, 970)
    pyautogui.click(700, 970)
    pyautogui.click(fanHuiX)
    pyautogui.alert(text="程序已执行完成",title="Test")




    # for i in range(0, m):
    #     一行数据 = data.loc[i]  # 选择某一行数据
    #     # print(一行数据)
    #     输入(数据输入坐标1, 0, 一行数据)  # 选择第1个数据
    #     输入(数据输入坐标2, 1, 一行数据)  # 选择第2个数据
    #     输入(数据输入坐标3, 2, 一行数据)  # 选择第3个数据
    #     输入(数据输入坐标4, 3, 一行数据)
    #     pyautogui.click(按钮坐标)


main()

