# -*- coding: utf-8 -*-
import pymysql
import time
import re

theId='1'
# way='/sys/bus/w1/devices/28-011432931aaf/w1_slave'
way='D:/1/w1_slave'
print('系统启动，开始连接数据库')
# conn = pymysql.connect(host="数据库IP", user="用户名", passwd="密码", db="other")
conn = pymysql.connect(host="127.0.0.1", user="root", passwd="123456", db="sb")
cursor = conn.cursor()
print("成功连接数据库,状态正常")

def order(iid,values):
    global cursor,conn
    iid=str(iid)
    values=str(values)
    itime=str(time.strftime('%Y-%m-%d %H:%M:%S'))
    iorder='insert into pi (id,itime,val) values ('+iid+',"'+itime+'",'+values+');'
    cursor.execute(iorder)
    conn.commit()
try:
    file=open(way,'r')
except Exception as err:
    print(err)
    order(theId,'-404')
    conn.close()
    try:
        file.close()
    except Exception:
        pass
    exit()

try:
    val=file.read()
    crc=re.compile('crc=.*? (.*?)\n').findall(val)[0]
    if crc!='YES':
        order(theId,'-410')
    else:
        t=re.compile('t=(.*?)\n').findall(val)[0]
        t=str(float(t)/1000.0)
        order(theId,t)
except Exception as err:
    print(err)
    order(theId,'-510')
finally:
    file.close()
    conn.close()