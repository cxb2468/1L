# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO #引入GPIO模块，重命名为GPIO
import time#引入时间模块
channel=6#设置端口号
j=0#初始化计数器为0
data=[]#初始化数据存储数组

GPIO.setmode(GPIO.BCM) #设置gpio引脚编号模式，有两种编号模式可供选择，自己随意设置就好
time.sleep(1)#程序暂停一秒钟
GPIO.setup(channel, GPIO.OUT) #设置6号口为输出模式
GPIO.output(channel, GPIO.LOW)#6号口输出低电平，即发送触发信号
time.sleep(0.02)#低电平维持0.02秒
GPIO.output(channel, GPIO.HIGH)#输出高电平，标志低电平结束
GPIO.setup(channel, GPIO.IN)#设置端口模式为输入
while GPIO.input(channel)==GPIO.LOW:#跳过初始状态的低电平
    pass
while GPIO.input(channel)==GPIO.HIGH:#跳过初始状态的高电平
    pass

#进入循环
while j < 40:#仅仅存储40个数据
	k = 0
	while GPIO.input(channel) == GPIO.LOW:#跳过低电平
		continue
	
	while GPIO.input(channel) == GPIO.HIGH:#如果是高电平，则进入循环，高电平结束时停止
		k += 1#计数器自增
		if k > 100:#如果高电平计数器大于100，则跳出循环，数据错误
			break
	
	if k < 8:#如果计数器数值小于8次，则认为值为0
		data.append(0)
	else:#否则认为值为1
		data.append(1)
 
	j += 1#数据位数计数器加一

#按位切割数据
humidity_bit = data[0:8]
humidity_point_bit = data[8:16]
temperature_bit = data[16:24]
temperature_point_bit = data[24:32]
check_bit = data[32:40]
 
humidity = 0
humidity_point = 0
temperature = 0
temperature_point = 0
check = 0

#计算各个数据结果和校验值
for i in range(8):
	humidity += humidity_bit[i] * 2 ** (7 - i)
	humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
	temperature += temperature_bit[i] * 2 ** (7 - i)
	temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
	check += check_bit[i] * 2 ** (7 - i)
#计算检查值
tmp = humidity + humidity_point + temperature + temperature_point

 
if check == tmp:
    print('数据正确')
    print("温度: "+str(temperature)+", 湿度: "+str(humidity))
else:
	print('数据错误')
	print("温度: "+str(temperature)+",湿度: "+str(humidity)+"校验值: "+str(check)+" 检查值: "+str(tmp))
 
GPIO.cleanup()