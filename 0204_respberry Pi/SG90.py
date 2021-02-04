# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
#将舵机度数转换为信号占空比，0-180度线性对应2.5%-12.5%的占空比
def tonum(num):
    fm=10.0/180.0
    num=num*fm+2.5
    num=int(num*10)/10.0
    return num

GPIO.setmode(GPIO.BCM) #设置gpio引脚编号模式，有两种编号模式可供选择，自己随意设置就好
GPIO.setup(13, GPIO.OUT) #设置13号口为输出模式
p13 = GPIO.PWM(13, 50) #设置13号口为PWM信号，标定频率为50HZ
p13.start(tonum(0)) #初始化舵机度数为0
while True: #进入死循环
    num=int(input("num:")) #请求用户输入转到多少度
    if num<0 or num>180:
        p13.stop() #停止端口占用（很重要）
        exit() #如果输入不正确则退出
    else:
        p13.ChangeDutyCycle(tonum(num)) #否则改变P13口的占空比为对应占空比