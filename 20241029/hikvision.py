# coding = utf-8
# 海康威视摄像头巡检主程序
# by 风吹我已散（吾爱破解论坛ID：fcwys）
# 博客：www.fcwys.cc
# 如需进行修改请保留作者信息（风吹我已散-www.fcwys.cc）
#####################################################

# 2024.10.25 使用rstp协议取流截图，提升画质 @懇樂樂


import requests
from requests.auth import HTTPDigestAuth
import time
from xml.dom.minidom import parseString
import os, sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, inch
import configparser
import time
import glob
import cv2
import datetime

# 读配置文件配置
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf8')
listPath = config['hkconfig']['listPath']  # 设备列表文件
picPath = config['hkconfig']['picPath']  # 截图保存路径(末尾需加/)
pdfPath = config['hkconfig']['pdfPath']  # PDF保存路径(末尾需加/)
# reportPath=config['hkconfig']['reportPath']  # 报表保存路径(末尾需加/)
copy = config['hkconfig']['copy']  # 公司名称
author = config['hkconfig']['author']  # 联系人
phone = config['hkconfig']['phone']  # 联系电话
addr = config['hkconfig']['addr']  # 地址
customer = config['hkconfig']['customer']  # 客户名

mac = devtype = devname = model = devid = sysCon = devnum = osver = cpu = mem = uptime = chan = codeType = codeRate = camReso = remark = noc = ''
devCount = 0  # 序号
nowDate = time.strftime("%Y%m%d", time.localtime())  # 当前日期
paths = []
# 请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}


# 生成PDF文件
def toPDF(ip, username):
    global paths
    global nowDate, copy, author, phone, addr, customer, devCount, mac, devtype, devname, model, devid, sysCon, devnum, osver, cpu, mem, uptime, remark, pdfPath
    # 判断文件夹是否存在不存在则创建
    if not os.path.exists(pdfPath):
        os.makedirs(pdfPath)
        os.makedirs(pdfPath + nowDate)
    else:
        if not os.path.exists(pdfPath + nowDate):
            os.makedirs(pdfPath + nowDate)

    nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 调用模板，创建指定名称的PDF文档
    # pagesize为文档页面尺寸
    # topMargin/bottomMargin 为文档上/下页边距
    # leftMargin/rightMargin 为文档左/右页边距
    pdfmetrics.registerFont(TTFont('SimSun', 'font/SimSun.ttf'))  # 注册宋体字体
    pdfmetrics.registerFont(TTFont('SimHei', 'font/SimHei.ttf'))  # 注册黑体字体
    doc = SimpleDocTemplate(f'{pdfPath}{nowDate}/{nowDate}_{ip}_检测报告.pdf', pagesize=(A4[0], A4[1]),
                            topMargin=0.3 * inch, bottomMargin=0.3 * inch, leftMargin=0.6 * inch,
                            rightMargin=0.6 * inch)
    # 获得模板表格
    styles = getSampleStyleSheet()
    # 指定模板
    # 标题样式
    title = styles['Heading1']
    title.fontName = 'SimHei'
    title.leading = 25  # 行间距
    # 正文样式
    content = styles['Normal']
    content.fontName = 'SimSun'
    content.fontSize = 11
    content.leading = 15  # 行间距
    # 初始化内容
    story = []
    # 将段落添加到内容中
    story.append(Paragraph(f'设备 {ip} 检测报告', title))
    story.append(Paragraph(f'生成时间：{nowTime}<br/>', content))
    story.append(
        Paragraph(f'---------------------------------------------------------------------------------------', content))
    story.append(
        Paragraph(f'测试公司：{copy}<br/>联系人：{author}<br/>联系电话：{phone}<br/>地址：{addr}<br/>客户名：{customer}<br/>', content))
    story.append(
        Paragraph(f'---------------------------------------------------------------------------------------', content))
    story.append(Paragraph(f'''
    设备IP：{ip}<br/>
    MAC地址：{mac}<br/>
    用户名：{username}<br/>
    设备名称：{devname}<br/>
    厂商：{sysCon}<br/>
    设备类型：{devtype}<br/>
    设备型号：{model}<br/>
    设备号：{devnum}<br/>
    固件：{osver}<br/>    
    设备序列号：{devid}<br/>
    运行时间：{uptime}小时<br/>
    CPU占用率：{cpu}%<br/>
    内存占用率：{mem}%<br/>    
    ''', content))
    # 判断设备类型是否添加截图
    # if devtype=='摄像头':
    # 摄像头详细信息
    # story.append(Paragraph(f'''
    # 通道名称：{chan}<br/>
    # 主码流类型：{codeType}<br/>
    # 码率：{codeRate} Kbps<br/>
    # 分辨率：{camReso}<br/>
    # 备注：{remark}<br/>
    # ''',content))
    story.append(
        Paragraph(f'---------------------------------------------------------------------------------------', content))
    # 将图片添加到内容
    story.append(Paragraph(f'画面截图：<br/>', content))
    # 获取文件目录下图片
    paths = glob.glob(f'{picPath}{nowDate}/{ip}_*.jpg')
    # print(paths)
    for item in paths:
        # print(item)
        campic = Image(item, width=495, height=320)
        story.append(campic)

    # try:
    #     #for numer in range(1,17):
    #     campic = Image(f'{picPath}{nowDate}/{ip}_{numer}01.jpg',width=495,height=320)
    #     story.append(campic)
    # except Exception as e:
    #     print(e)
    # else:

    story.append(Paragraph(f'备注：<br/>', content))
    # 将内容输出到PDF中
    doc.build(story)
    print(f'PDF报告：{pdfPath}{nowDate}/{nowDate}_{ip}_检测报告.pdf\n')
    print(os.path.abspath(f'{pdfPath}{nowDate}/{nowDate}_{ip}_检测报告.pdf'))


# 写入CSV
def toCsv(data):
    global nowDate
    # 判断文件夹是否存在不存在则创建
    if not os.path.exists(reportPath):
        os.makedirs(reportPath)
    with open(f'{reportPath}{nowDate}_巡检报表.csv', 'a', encoding='utf-8-sig') as f:
        f.write(data)
        f.close()


# 获取画面
# 参数 IP地址 端口 用户名 密码
def getImg(ip, port, username, password):
    global nowDate, picPath, model
    if "32" in model:
        noc = "33"
    elif "64" in model:
        noc = "65"
    else:
        noc = "17"
    for i in range(1, int(noc)):
        rtsp_url = f'rtsp://{username}:{password}@{ip}:554/Streaming/Channels/{i}01?transportmode=unicast'
        try:
            # 创建VideoCapture对象
            cap = cv2.VideoCapture(rtsp_url)
            # 检查是否成功打开视频流
            if cap.isOpened():
                # 判断文件夹是否存在,不存在则创建
                if not os.path.exists(picPath):
                    os.makedirs(picPath)
                    if not os.path.exists(picPath + nowDate):
                        os.makedirs(picPath + nowDate)
                else:
                    if not os.path.exists(picPath + nowDate):
                        os.makedirs(picPath + nowDate)
                # 截取时长为1秒
                duration = 1  # seconds
                start_time = datetime.datetime.now()
                while (datetime.datetime.now() - start_time).total_seconds() < duration:
                    # 读取一帧
                    ret, frame = cap.read()
                    # 如果正确读取帧，ret为True
                    if not ret:
                        print("Can't receive frame (stream end?). Exiting ...")
                        break
                        # 构造保存图片的文件名
                imgname = f'{ip}_{i}01.jpg'
                filename = f'{picPath}{nowDate}/{imgname}'
                cv2.imwrite(filename, frame)
                print(f'截图：{picPath}{nowDate}/{imgname}')
            else:
                print(f'设备 {ip} 截图失败：Cannot open video stream or file')
        except Exception as e:
            # print(f'抓取 {ip} 图片超时!\n')
            print(e)
        # imgurl=f'http://{ip}:{port}/ISAPI/Streaming/channels/{i}01/picture'
        # try:
        #     pic=requests.get(imgurl,auth=HTTPDigestAuth(username,password),headers=headers,timeout=5)
        #     #print(pic)
        #     # 判断状态信息请求是否正常
        #     if pic.status_code==200:
        #         #判断文件夹是否存在,不存在则创建
        #         if not os.path.exists(picPath):
        #             os.makedirs(picPath)
        #             if not os.path.exists(picPath+nowDate):
        #                 os.makedirs(picPath+nowDate)
        #         else:
        #             if not os.path.exists(picPath+nowDate):
        #                 os.makedirs(picPath+nowDate)
        #         #获取文件名
        #         imgname=f'{ip}_{i}01.jpg'
        #         with open(f'{picPath}{nowDate}/{imgname}',"wb") as code:
        #             code.write(pic.content)
        #             code.close()
        #         print(f'截图：{picPath}{nowDate}/{imgname}')
        #     else:
        #         print(f'设备 {ip} 截图失败：账号信息有误或请求超时!\n')
        # except Exception as e:
        #     print(e)
        #     #print(f'抓取 {ip} 图片超时!\n')


# 获取通道详细信息
# 参数 IP地址 端口 用户名 密码
def getCaminfo(ip, port, username, password):
    global chan, codeType, codeRate, camReso
    for i in range(9):
        try:
            camUrl = f'http://{ip}:{port}/ISAPI/Streaming/channels/{i}01'
            cam = requests.get(camUrl, auth=HTTPDigestAuth(username, password), headers=headers, timeout=3)
            cam.encoding = "utf-8"
            # 判断状态信息请求是否正常
            if cam.status_code == 200:
                camRes = parseString(cam.text.replace("\n", ""))
                camDom = camRes.documentElement
                # 通道名称
                chan = camDom.getElementsByTagName("channelName")[0].childNodes[0].data
                # 主码流类型
                codeType = camDom.getElementsByTagName("videoCodecType")[0].childNodes[0].data
                # 码率(Kbps)
                codeRate = camDom.getElementsByTagName("constantBitRate")[0].childNodes[0].data
                # 分辨率
                camWidth = camDom.getElementsByTagName("videoResolutionWidth")[0].childNodes[0].data
                camHeight = camDom.getElementsByTagName("videoResolutionHeight")[0].childNodes[0].data
                camReso = f'{camWidth}x{camHeight}'

            else:
                remark = '账号信息有误或请求超时'
        except Exception as e:
            # print(e)
            remark = '账号信息有误或请求超时'


# 获取设备信息
# 参数 IP地址 端口 用户名 密码
def getInfo(ip, port, username, password):
    global devCount, mac, devtype, devname, model, devid, sysCon, devnum, osver, cpu, mem, uptime, chan, codeType, codeRate, camReso, remark
    # 每次请求前初始化数据
    mac = devtype = devname = model = devid = sysCon = devnum = osver = cpu = mem = uptime = remark = ''

    # 开始请求设备信息
    try:
        devUrl = f'http://{ip}:{port}/ISAPI/System/deviceinfo'
        dev = requests.get(devUrl, auth=HTTPDigestAuth(username, password), headers=headers, timeout=3)
        dev.encoding = "utf-8"
        devRes = parseString(dev.text.replace("\n", ""))
        devDom = devRes.documentElement
        # 判断设备信息请求是否正常
        if dev.status_code == 200:
            # 设备类型
            devtype = devDom.getElementsByTagName("deviceType")[0].childNodes[0].data
            if devtype == 'IPCamera':
                devtype = '摄像头'
                # 厂商
                sysCon = devDom.getElementsByTagName("systemContact")[0].childNodes[0].data
                sysCon = sysCon.replace('.China', '')
            else:
                devtype = '硬盘录像机'
                sysCon = 'Hikvision'
            # 设备名称
            devname = devDom.getElementsByTagName("deviceName")[0].childNodes[0].data
            # 设备型号
            model = devDom.getElementsByTagName("model")[0].childNodes[0].data
            # 设备MAC
            mac = devDom.getElementsByTagName("macAddress")[0].childNodes[0].data
            # 设备ID
            devid = devDom.getElementsByTagName("serialNumber")[0].childNodes[0].data
            # 固件版本
            osver = devDom.getElementsByTagName("firmwareVersion")[0].childNodes[0].data
            # 设备号
            devnum = devDom.getElementsByTagName("telecontrolID")[0].childNodes[0].data
        else:
            remark = '账号信息有误或请求超时'
    except Exception as e:
        # print(e)
        remark = '账号信息有误或请求超时'

    # 开始请求状态信息
    try:
        statUrl = f'http://{ip}:{port}/ISAPI/System/status'
        stat = requests.get(statUrl, auth=HTTPDigestAuth(username, password), headers=headers, timeout=3)
        stat.encoding = "utf-8"
        # 判断状态信息请求是否正常
        if stat.status_code == 200:
            statRes = parseString(stat.text.replace("\n", ""))
            statDom = statRes.documentElement
            try:
                # cpu使用率
                cpu = statDom.getElementsByTagName("cpuUtilization")[0].childNodes[0].data
            except Exception as e:
                cpu = 0

            # 运行时间
            uptime = statDom.getElementsByTagName("deviceUpTime")[0].childNodes[0].data
            uptime = round(int(uptime) / 60 / 60)  # 转换为小时(保留两位小数)
            # 内存使用率
            if devtype == '摄像头':
                mem = statDom.getElementsByTagName("memoryUsage")[0].childNodes[0].data
                # 若是摄像头则获取详细信息
                getCaminfo(ip, port, username, password)
            else:
                # 内存使用率
                mem1 = statDom.getElementsByTagName("memoryUsage")[0].childNodes[0].data
                mem2 = statDom.getElementsByTagName("memoryAvailable")[0].childNodes[0].data
                mem = round(float(mem1) / (float(mem1) + float(mem2)) * 100, 2)
        else:
            remark = '账号信息有误或请求超时'
    except Exception as e:
        # print(e)
        remark = '账号信息有误或请求超时'
    # 序号自增
    devCount += 1
    print(f'''
序号：{devCount}
设备IP：{ip}
MAC地址：{mac}
设备类型：{devtype}
设备名称：{devname}
设备型号：{model}
用户名：{username}
设备序列号：{devid}
厂商：{sysCon}
设备号：{devnum}
固件版本：{osver}
CPU占用率：{cpu}%
内存占用率：{mem}%
运行时间：{uptime}小时
通道名称：{chan}
主码流类型：{codeType}
码率：{codeRate} Kbps
分辨率：{camReso}
备注：{remark}''')
    # toCsv(f'{devCount},{ip},{mac},{devtype},{devname},{model},{username},{devid},{sysCon},{devnum},{osver},{cpu},{mem},{uptime},{chan},{codeType},{codeRate},{camReso},{remark}\n')
    if remark == '账号信息有误或请求超时':
        x = input('回车键退出...\n')
        sys.exit()
    getImg(ip, port, username, password)
    toPDF(ip, username)
    # 当设备为摄像头时抓取图像
    # if devtype=='摄像头':
    #     # 抓取截图
    #     getImg(ip,port,username,password)
    # # 生成PDF
    # toPDF(ip,username)


# 从文件获取设备信息
def getHost(hostfile):
    hostlist = open(hostfile, 'r')
    hostlist.seek(0)
    # 跳过第一行
    next(hostlist)
    for host in hostlist.readlines():
        host = host.strip().replace('\n', '')
        host = host.split(',')
        getInfo(host[0], host[1], host[2], host[3])


if __name__ == "__main__":
    print('''
         _    _ _ _     _____                 
        | |  | (_) |   / ____|                
        | |__| |_| | _| (___   ___ __ _ _ __  
        |  __  | | |/ /\___ \ / __/ _` | '_ \ 
        | |  | | |   < ____) | (_| (_| | | | |
        |_|  |_|_|_|\_\_____/ \___\__,_|_| |_|
    ''')
    print('======== 海康威视录像机巡检工具 by 风吹我已散 (懇樂樂于2024.10.25修改) ========\n')
    print('>>> 开始巡检...\n')
    # # Csv文件标题头
    # titles='序号,设备IP,MAC地址,设备类型,设备名称,设备型号,用户名,设备ID,厂商,序列号,固件版本,CPU占用率(%),内存占用率(%),运行时间(小时),通道名称,主码流类型,码率(Kbps),分辨率,备注\n'
    # toCsv(titles)
    getHost(listPath)
    # print(f'>>> 检测报告表： {reportPath}{nowDate}_巡检报表.csv\n')
    print('>>> 巡检完成!\n')
    x = input('回车键退出...\n')

