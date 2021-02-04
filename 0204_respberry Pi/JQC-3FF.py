# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO #引入GPIO模块，重命名为GPIO
GPIO.setmode(GPIO.BCM) #设置gpio引脚编号模式，有两种编号模式可供选择，自己随意设置就好
GPIO.setup(13, GPIO.OUT) #设置13号口为输出模式
GPIO.output(13, GPIO.HIGH) #13号口输出高电平

