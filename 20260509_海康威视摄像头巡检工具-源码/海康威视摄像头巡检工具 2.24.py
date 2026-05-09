# coding = utf-8
# 海康威视摄像头巡检 2.0
# by 风吹我已散（吾爱破解论坛ID：fcwys）
# received by fishershoot


import requests
from requests.auth import HTTPDigestAuth
import time
from xml.dom.minidom import parseString
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4,inch
import configparser
import subprocess

# 配置文件格式转换
print('正在转换config文件格式...\n')
s = open('config.ini', mode='r', encoding='utf-8-sig').read()
open('config.ini', mode='w', encoding='utf-8').write(s)
print('转换成功！！\n')

# 读配置文件配置
config = configparser.ConfigParser()
config.read('config.ini',encoding='utf8')
listPath=config['hkconfig']['listPath'] # 设备列表文件
picPath=config['hkconfig']['picPath']  # 截图保存路径(末尾需加/)
pdfPath=config['hkconfig']['pdfPath']  # PDF保存路径(末尾需加/)
reportPath=config['hkconfig']['reportPath']  # 报表保存路径(末尾需加/)
copy=config['hkconfig']['copy']    #公司名称
author=config['hkconfig']['author'] # 联系人
phone=config['hkconfig']['phone'] #联系电话
addr=config['hkconfig']['addr'] # 地址
customer=config['hkconfig']['customer'] #客户名

mac=devtype=devname=model=devid=sysCon=devnum=osver=cpu=mem=uptime=chan=codeType=codeRate=camReso=remark=''
devCount=0  #序号
nowDate=time.strftime("%Y%m%d",time.localtime())    # 当前日期

# 请求头信息
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}


# Windows系统下使用ping命令检测IP是否在线
def is_ip_online(ip):

    command = ["ping", "-n", "1", ip]  # -n 1表示发送一个ICMP请求
    
    # subprocess.STDOUT 表示将标准错误重定向到标准输出
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        try:
            # 等待命令执行完成，timeout可以设置为适当的超时时间
            stdout, _ = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            # 如果命令执行超时，终止进程
            proc.kill()
            return False  # IP不在线

        # 检查返回码，0表示命令成功执行，即IP在线
        return proc.returncode == 0

    

# 生成PDF文件
def toPDF(ip,username):
    global nowDate,nowtime,copy,author,phone,addr,customer,devCount,mac,devtype,devname,model,devid,sysCon,devnum,osver,cpu,mem,uptime,remark,pdfPath,picPath,chan,codeType,codeRate,camReso
    #判断文件夹是否存在不存在则创建
    if not os.path.exists(pdfPath):
        os.makedirs(pdfPath)
        os.makedirs(pdfPath+nowDate)
    else:
        if not os.path.exists(pdfPath+nowDate):
            os.makedirs(pdfPath+nowDate)
            
    nowTime=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    nowtime=nowTime
    # 调用模板，创建指定名称的PDF文档
    # pagesize为文档页面尺寸
    # topMargin/bottomMargin 为文档上/下页边距
    # leftMargin/rightMargin 为文档左/右页边距
    pdfmetrics.registerFont(TTFont('SimSun', 'font/SimSun.ttf')) #注册宋体字体
    pdfmetrics.registerFont(TTFont('SimHei', 'font/SimHei.ttf')) #注册黑体字体
    doc = SimpleDocTemplate(f'{pdfPath}{nowDate}/{nowDate}_{ip}_{devname}_摄像头巡检报告.pdf',pagesize=(A4[0],A4[1]),topMargin = 0.3 * inch,bottomMargin =  0.3 * inch,leftMargin=0.6 * inch,rightMargin=0.6 * inch)
    # 获得模板表格
    styles = getSampleStyleSheet()
    # 指定模板
    # 标题样式
    title = styles['Heading1']
    title.fontName='SimHei'
    title.leading=25  #行间距
    # 正文样式
    content = styles['Normal']
    content.fontName='SimSun'
    content.fontSize=11
    content.leading=15  #行间距
    # 初始化内容
    story =[]
    # 将段落添加到内容中
    story.append(Paragraph(f'设备 {ip} 巡检报告',title))
    story.append(Paragraph(f'生成时间：{nowTime}<br/>',content))
    story.append(Paragraph(f'---------------------------------------------------------------------------------------',content))
    story.append(Paragraph(f'测试公司：{copy}<br/>联系人：{author}<br/>联系电话：{phone}<br/>地址：{addr}<br/>客户名：{customer}<br/>',content))
    story.append(Paragraph(f'---------------------------------------------------------------------------------------',content))
    story.append(Paragraph(f'''
    设备IP：{ip}<br/>
    MAC地址：{mac}<br/>
    用户名：{username}<br/>
    设备名：{devname}<br/>
    厂商：{sysCon}<br/>
    设备类型：{devtype}<br/>
    设备型号：{model}<br/>
    设备编号：{devnum}<br/>
    固件：{osver}<br/>    
    设备序列号：{devid}<br/>
    运行时间：{uptime}小时<br/>
    CPU占用率：{cpu}%<br/>
    内存占用率：{mem}%<br/>    
    ''',content))
    # 判断设备类型是否添加截图
    if devtype=='摄像头':
        # 摄像头详细信息
        story.append(Paragraph(f'''
        通道名称：{chan}<br/>
        主码流类型：{codeType}<br/>
        码率：{codeRate} Kbps<br/>
        分辨率：{camReso}<br/>
        备注：{remark}<br/>
        ''',content))
        # 将图片添加到内容（检查图片文件是否存在）
        img_path = f'{picPath}{nowDate}/{ip}.jpg'
        if os.path.exists(img_path):
            story.append(Paragraph(f'监控画面截图：<br/>',content))
            campic = Image(img_path,width=495,height=320)
            story.append(campic)
        else:
            story.append(Paragraph(f'监控画面截图：无法获取<br/>',content))
    else:
        story.append(Paragraph(f'备注信息：<br/>',content))
    # 将内容输出到PDF中
    doc.build(story)
    print(f'PDF报告：{pdfPath}{nowDate}/{nowDate}_{ip}_{devname}_摄像头巡检报告.pdf\n')

# 写入CSV
def toCsv(data):
    global nowDate
    #判断文件夹是否存在不存在则创建
    if not os.path.exists(reportPath):
        os.makedirs(reportPath)            
    with open(f'{reportPath}{nowDate}_巡检报表.csv','a',encoding='utf-8-sig') as f:
        f.write(data)
        f.close()

# 获取摄像头画面
# 参数 IP地址 端口 用户名 密码
def getImg(ip,port,username,password):
    global nowDate,picPath,osver
    
    # 根据固件版本智能选择截图端点优先级
    # V6.0.x 固件主码流截图被禁止，优先尝试子码流
    is_new_firmware = osver.startswith('V6') if 'osver' in globals() else False
    
    if is_new_firmware:
        # 新型号固件：优先子码流
        img_urls = [
            f'http://{ip}:{port}/ISAPI/Streaming/channels/102/picture',  # 子码流截图（V6.0.x优先）
            f'http://{ip}:{port}/ISAPI/Streaming/channels/101/picture',  # 主码流截图
            f'http://{ip}:{port}/Streaming/channels/102/picture',        # 简化路径子码流
            f'http://{ip}:{port}/cgi-bin/snapshot.cgi',                  # 通用截图端点
            f'http://{ip}:{port}/axis-cgi/jpg/image.cgi',                # AXIS兼容端点
        ]
    else:
        # 旧型号固件：优先主码流
        img_urls = [
            f'http://{ip}:{port}/ISAPI/Streaming/channels/101/picture',  # 主码流截图（标准ISAPI）
            f'http://{ip}:{port}/Streaming/channels/101/picture',        # 简化路径
            f'http://{ip}:{port}/ISAPI/Streaming/channels/102/picture',  # 子码流截图
            f'http://{ip}:{port}/cgi-bin/snapshot.cgi',                  # 通用截图端点
            f'http://{ip}:{port}/axis-cgi/jpg/image.cgi',                # AXIS兼容端点
        ]
    
    for imgurl in img_urls:
        try:
            debug_log(ip, f'尝试截图端点: {imgurl}')
            # 尝试 Digest 认证
            pic=requests.get(imgurl,auth=HTTPDigestAuth(username,password),headers=headers,timeout=5)
            debug_log(ip, f'截图请求状态码: {pic.status_code}')
            
            if pic.status_code==200:
                # 判断内容是否为图片（检查 Content-Type）
                content_type = pic.headers.get('Content-Type', '')
                if 'image' in content_type.lower() or len(pic.content) > 100:
                    # 判断文件夹是否存在不存在则创建
                    if not os.path.exists(picPath):
                        os.makedirs(picPath)
                        os.makedirs(picPath+nowDate)
                    else:
                        if not os.path.exists(picPath+nowDate):
                            os.makedirs(picPath+nowDate)
                    # 获取文件名
                    imgname=f'{ip}.jpg'
                    with open(f'{picPath}{nowDate}/{imgname}',"wb") as code:
                         code.write(pic.content)
                         code.close()
                    print(f'截图：{picPath}{nowDate}/{imgname}')
                    debug_log(ip, f'截图保存成功: {picPath}{nowDate}/{imgname}')
                    return  # 成功后立即返回
                
            elif pic.status_code == 401:
                # 尝试 Basic 认证
                debug_log(ip, f'尝试 Basic 认证')
                from requests.auth import HTTPBasicAuth
                pic=requests.get(imgurl,auth=HTTPBasicAuth(username,password),headers=headers,timeout=5)
                if pic.status_code==200:
                    content_type = pic.headers.get('Content-Type', '')
                    if 'image' in content_type.lower() or len(pic.content) > 100:
                        if not os.path.exists(picPath):
                            os.makedirs(picPath)
                            os.makedirs(picPath+nowDate)
                        else:
                            if not os.path.exists(picPath+nowDate):
                                os.makedirs(picPath+nowDate)
                        imgname=f'{ip}.jpg'
                        with open(f'{picPath}{nowDate}/{imgname}',"wb") as code:
                             code.write(pic.content)
                             code.close()
                        print(f'截图：{picPath}{nowDate}/{imgname}')
                        debug_log(ip, f'截图保存成功(Basic认证): {picPath}{nowDate}/{imgname}')
                        return
                
        except Exception as e:
            debug_log(ip, f'截图端点 {imgurl} 请求异常: {str(e)}')
            continue  # 尝试下一个端点
    
    # 所有端点都失败
    print(f'设备 {ip} 截图失败：所有可用端点均无法获取截图\n')
    debug_log(ip, f'截图失败：所有可用端点均无法获取截图')

# 获取摄像头详细信息
# 参数 IP地址 端口 用户名 密码
def getCaminfo(ip,port,username,password):
    global chan,codeType,codeRate,camReso
    try:
        debug_log(ip, '请求摄像头通道信息: /ISAPI/Streaming/channels/101')
        camUrl=f'http://{ip}:{port}/ISAPI/Streaming/channels/101'
        cam=requests.get(camUrl,auth=HTTPDigestAuth(username,password),headers=headers,timeout=3)
        cam.encoding="utf-8"
        
        debug_log(ip, f'摄像头通道信息请求状态码: {cam.status_code}')
        
        # 保存通道信息XML用于调试
        cam_xml_path = f'debug_{ip}_channels.xml'
        with open(cam_xml_path, 'w', encoding='utf-8') as f:
            f.write(cam.text)
        debug_log(ip, f'原始通道信息XML已保存到: {cam_xml_path}')
        
        # 判断状态信息请求是否正常
        if  cam.status_code==200:
            camRes=parseString(cam.text.replace("\n", ""))            
            camDom=camRes.documentElement
            # 通道名称
            try:
                chan=camDom.getElementsByTagName("channelName")[0].childNodes[0].data
                debug_log(ip, f'channelName: {chan}')
            except Exception as e:
                debug_log(ip, f'获取 channelName 失败: {str(e)}')
            
            # 主码流类型
            try:
                codeType=camDom.getElementsByTagName("videoCodecType")[0].childNodes[0].data
                debug_log(ip, f'videoCodecType: {codeType}')
            except Exception as e:
                debug_log(ip, f'获取 videoCodecType 失败: {str(e)}')
            
            # 码率(Kbps) - 兼容新型号使用vbrUpperCap代替constantBitRate
            try:
                codeRateNodes=camDom.getElementsByTagName("constantBitRate")
                if len(codeRateNodes)>0:
                    codeRate=codeRateNodes[0].childNodes[0].data
                    debug_log(ip, f'constantBitRate: {codeRate}')
                else:
                    # 尝试获取变码率上限
                    vbrUpperNodes=camDom.getElementsByTagName("vbrUpperCap")
                    if len(vbrUpperNodes)>0:
                        codeRate=vbrUpperNodes[0].childNodes[0].data
                        debug_log(ip, f'vbrUpperCap (变码率上限): {codeRate}')
                    else:
                        codeRate='N/A'
                        debug_log(ip, '码率信息: constantBitRate和vbrUpperCap均不存在')
            except Exception as e:
                debug_log(ip, f'获取 constantBitRate 失败: {str(e)}')
                codeRate='N/A'
            
            # 分辨率
            try:
                camWidth=camDom.getElementsByTagName("videoResolutionWidth")[0].childNodes[0].data
                camHeight=camDom.getElementsByTagName("videoResolutionHeight")[0].childNodes[0].data
                camReso=f'{camWidth}x{camHeight}'
                debug_log(ip, f'videoResolution: {camReso}')
            except Exception as e:
                debug_log(ip, f'获取 videoResolution 失败: {str(e)}')

        else:
            remark='无法获取参数'
            debug_log(ip, '摄像头通道信息请求失败')
    except Exception as e:
        debug_log(ip, f'摄像头通道信息请求异常: {str(e)}')
        remark='未知错误183'
        

# 调试日志函数
def debug_log(ip, message):
    log_path = 'debug.log'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_line = f'[{timestamp}] IP: {ip} - {message}\n'
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_line)
    print(log_line, end='')

# 获取设备信息
# 参数 IP地址 端口 用户名 密码
def getInfo(ip,port,username,password):
    global devCount,mac,devtype,devname,model,devid,sysCon,devnum,osver,cpu,mem,uptime,chan,codeType,codeRate,camReso,remark
    # 每次请求前初始化数据
    mac=devtype=devname=model=devid=sysCon=devnum=osver=cpu=mem=uptime=remark=''
    
    debug_log(ip, '========== 开始处理设备 ==========')
    debug_log(ip, f'端口: {port}, 用户名: {username}')
    
    # 开始请求设备信息
    try:
        debug_log(ip, '请求设备信息: /ISAPI/System/deviceinfo')
        devUrl=f'http://{ip}:{port}/ISAPI/System/deviceinfo'
        dev=requests.get(devUrl,auth=HTTPDigestAuth(username,password),headers=headers,timeout=3)
        dev.encoding="utf-8"
        
        debug_log(ip, f'设备信息请求状态码: {dev.status_code}')
        
        # 保存原始XML用于调试
        xml_path = f'debug_{ip}_deviceinfo.xml'
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(dev.text)
        debug_log(ip, f'原始设备信息XML已保存到: {xml_path}')
        
        devRes=parseString(dev.text.replace("\n", ""))
        devDom=devRes.documentElement
        # 判断设备信息请求是否正常
        if dev.status_code==200:
            # 设备类型
            try:
                devtype=devDom.getElementsByTagName("deviceType")[0].childNodes[0].data
                debug_log(ip, f'获取到的 deviceType: "{devtype}"')
            except Exception as e:
                debug_log(ip, f'获取 deviceType 失败: {str(e)}')
                devtype = '未知'
            
            # 支持的摄像头设备类型列表
            supported_camera_types = ['IPCamera', 'IPDome', 'IPC', 'IPCamera2', 'Camera', 'DigitalCamera']
            if devtype in supported_camera_types:
                devtype='摄像头'
                # 厂商
                try:
                    sysCon=devDom.getElementsByTagName("systemContact")[0].childNodes[0].data
                    sysCon=sysCon.replace('.China','')
                except Exception as e:
                    debug_log(ip, f'获取 systemContact 失败: {str(e)}')
                    sysCon='Hikvision'
            else:
                debug_log(ip, f'deviceType "{devtype}" 不在支持列表中，默认标记为硬盘录像机')
                devtype='硬盘录像机'
                sysCon='Hikvision'
            
            # 设备名称
            try:
                devname=devDom.getElementsByTagName("deviceName")[0].childNodes[0].data
                debug_log(ip, f'deviceName: {devname}')
            except Exception as e:
                debug_log(ip, f'获取 deviceName 失败: {str(e)}')
            
            # 设备型号
            try:
                model=devDom.getElementsByTagName("model")[0].childNodes[0].data
                debug_log(ip, f'model: {model}')
            except Exception as e:
                debug_log(ip, f'获取 model 失败: {str(e)}')
            
            # 设备MAC
            try:
                mac=devDom.getElementsByTagName("macAddress")[0].childNodes[0].data
                debug_log(ip, f'macAddress: {mac}')
            except Exception as e:
                debug_log(ip, f'获取 macAddress 失败: {str(e)}')
            
            # 设备ID
            try:
                devid=devDom.getElementsByTagName("serialNumber")[0].childNodes[0].data
                debug_log(ip, f'serialNumber: {devid}')
            except Exception as e:
                debug_log(ip, f'获取 serialNumber 失败: {str(e)}')
            
            # 固件版本
            try:
                osver=devDom.getElementsByTagName("firmwareVersion")[0].childNodes[0].data
                debug_log(ip, f'firmwareVersion: {osver}')
            except Exception as e:
                debug_log(ip, f'获取 firmwareVersion 失败: {str(e)}')
            
            # 序列号
            try:
                devnum=devDom.getElementsByTagName("telecontrolID")[0].childNodes[0].data
                debug_log(ip, f'telecontrolID: {devnum}')
            except Exception as e:
                debug_log(ip, f'获取 telecontrolID 失败: {str(e)}')
        else:
            remark='不支持的设备类型'
            debug_log(ip, f'设备信息请求失败，状态码: {dev.status_code}')
    except Exception as e:
        debug_log(ip, f'设备信息请求异常: {str(e)}')
        remark='未知错误228'
        
    # 开始请求状态信息
    try:
        debug_log(ip, '检查设备在线状态...')
        online = is_ip_online(ip)
        debug_log(ip, f'设备在线状态: {"在线" if online else "离线"}')
        
        debug_log(ip, '请求状态信息: /ISAPI/System/status')
        statUrl=f'http://{ip}:{port}/ISAPI/System/status'
        stat=requests.get(statUrl,auth=HTTPDigestAuth(username,password),headers=headers,timeout=3)
        stat.encoding="utf-8"
        
        debug_log(ip, f'状态信息请求状态码: {stat.status_code}')
        
        # 保存状态信息XML用于调试
        stat_xml_path = f'debug_{ip}_status.xml'
        with open(stat_xml_path, 'w', encoding='utf-8') as f:
            f.write(stat.text)
        debug_log(ip, f'原始状态信息XML已保存到: {stat_xml_path}')
        
        # 判断状态信息请求是否正常
        if stat.status_code==200:
            statRes=parseString(stat.text.replace("\n", ""))            
            statDom=statRes.documentElement
            # cpu使用率 - 兼容新型号可能没有CPUList的情况
            try:
                cpuNodes=statDom.getElementsByTagName("cpuUtilization")
                if len(cpuNodes)>0:
                    cpu=cpuNodes[0].childNodes[0].data
                    debug_log(ip, f'cpuUtilization: {cpu}%')
                else:
                    cpu='N/A'
                    debug_log(ip, 'cpuUtilization: 新型号固件不支持此字段')
            except Exception as e:
                debug_log(ip, f'获取 cpuUtilization 失败: {str(e)}')
                cpu='N/A'
            
            # 运行时间 - 兼容新型号可能没有deviceUpTime的情况
            try:
                uptimeNodes=statDom.getElementsByTagName("deviceUpTime")
                if len(uptimeNodes)>0:
                    uptime=uptimeNodes[0].childNodes[0].data
                    uptime=round(int(uptime)/60/60)
                    debug_log(ip, f'deviceUpTime: {uptime}小时')
                else:
                    uptime='N/A'
                    debug_log(ip, 'deviceUpTime: 新型号固件不支持此字段')
            except Exception as e:
                debug_log(ip, f'获取 deviceUpTime 失败: {str(e)}')
                uptime='N/A'
            
            # 内存使用率
            if devtype=='摄像头':
                try:
                    memNodes=statDom.getElementsByTagName("memoryUsage")
                    if len(memNodes)>0:
                        mem=memNodes[0].childNodes[0].data
                        debug_log(ip, f'memoryUsage: {mem}%')
                    else:
                        mem='N/A'
                        debug_log(ip, 'memoryUsage: 新型号固件不支持此字段')
                except Exception as e:
                    debug_log(ip, f'获取 memoryUsage 失败: {str(e)}')
                    mem='N/A'
                # 若是摄像头则获取详细信息
                getCaminfo(ip,port,username,password)
            else:
                try:
                    mem1Nodes=statDom.getElementsByTagName("memoryUsage")
                    mem2Nodes=statDom.getElementsByTagName("memoryAvailable")
                    if len(mem1Nodes)>0 and len(mem2Nodes)>0:
                        mem1=mem1Nodes[0].childNodes[0].data                        
                        mem2=mem2Nodes[0].childNodes[0].data                
                        mem=round(float(mem1)/(float(mem1)+float(mem2))*100,2)
                        debug_log(ip, f'memoryUsage: {mem1}, memoryAvailable: {mem2}, 计算后: {mem}%')
                    else:
                        mem='N/A'
                        debug_log(ip, '内存信息: 新型号固件不支持此字段')
                except Exception as e:
                    debug_log(ip, f'获取内存信息失败: {str(e)}')
                    mem='N/A'
        else:
            remark='设备不是海康设备'
            debug_log(ip, f'状态信息请求失败，状态码: {stat.status_code}')
    except Exception as e:
        debug_log(ip, f'状态信息请求异常: {str(e)}')

        if not online:
            remark='设备不在线'
        else:
            remark='设备不支持'
    # 序号自增
    devCount+=1
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
序列号：{devnum}
固件版本：{osver}
CPU占用率：{cpu}%
内存占用率：{mem}%
运行时间：{uptime}小时
通道名称：{chan}
主码流类型：{codeType}
码率：{codeRate} Kbps
分辨率：{camReso}
备注：{remark}''')
    toCsv(f'{devCount},{ip},{mac},{devtype},{devname},{model},{username},{devid},{sysCon},{devnum},{osver},{cpu},{mem},{uptime},{chan},{codeType},{codeRate},{camReso},{remark}\n')
    # 当设备为摄像头时抓取图像
    if devtype=='摄像头':
        # 抓取截图
        getImg(ip,port,username,password)
    # 生成PDF
        toPDF(ip,username)
    else:
            remark='不支持录像机'
        

# 从文件获取设备信息
def getHost(hostfile):
    hostlist=open(hostfile,'r')
    hostlist.seek(0)
    # 跳过第一行
    next(hostlist)
    for host in hostlist.readlines():
        host=host.strip().replace('\n','')
        host=host.split(',')    
        getInfo(host[0],host[1],host[2],host[3])

if __name__=="__main__":
    print('''
         _    _ _ _     _____                 
        | |  | (_) |   / ____|                
        | |__| |_| | _| (___   ___ __ _ _ __  
        |  __  | | |/ /\___ \ / __/ _` | '_ \ 
        | |  | | |   < ____) | (_| (_| | | | |
        |_|  |_|_|_|\_\_____/ \___\__,_|_| |_|
    ''')    
    print('======== 海康威视摄像头巡检工具 by 风吹我已散 (www.fcwys.cc) received by fishershoot========\n')
    print('======== 2026.5.8由“又是馒头”更新对2CD2245CV8-L 5.8版本、2CD2345CV5-L 6.0.1版本的支持=======\n')
    print('>>> 开始巡检...\n')
    # Csv文件标题头
    titles='序号,设备IP,MAC地址,设备类型,设备名称,设备型号,用户名,设备ID,厂商,序列号,固件版本,CPU占用率(%),内存占用率(%),运行时间(小时),通道名称,主码流类型,码率(Kbps),分辨率,备注\n'
    toCsv(titles)
    getHost(listPath)
    print(f'>>> 检测报告表： {reportPath}{nowDate}_巡检报表.csv\n')
    print('>>> 巡检完成!\n')
    x=input('回车键退出...\n')
