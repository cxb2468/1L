import datetime
import time
import sys
import smtplib
from email.mime.text import MIMEText
import tushare as ts
import pandas as pd
import schedule

# ================== 配置信息 ==================
# 请替换以下邮箱和密码为您的QQ邮箱账号和授权码
from_addr = 'your_email@qq.com'  # 发件人邮箱地址
password = 'your_authorization_code'  # 发件人邮箱授权码
email_add = ['your_email@qq.com']  # 接收邮件的邮箱地址列表

# 股票监控参数
code = '600905'  # 监控的股票代码（三峡能源）
cbj = 5.00  # 购买成本价（单位：元）
shuliang = 1000  # 持股数量
color_bg_fg = '#f0f0f0'  # 邮件表格背景色

# Tushare Pro API 配置
API_TOKEN = "b0088a0010b48f8a0a2c6216580943d847cc9c1d6cf591c84502e940"
pro = ts.pro_api(API_TOKEN)


# 获取股票名称（只获取一次，避免重复请求）
def get_stock_name(code):
    """获取股票名称（通过Pro API）"""
    try:
        df = pro.stock_basic(symbol=code, fields='name')
        if not df.empty:
            return df['name'].values[0]
        return code  # 如果获取失败，返回代码
    except Exception as e:
        print(f"获取股票名称失败: {e}")
        return code


# 获取股票实时价格（使用Tushare Pro API）
def get_now_jiage(code):
    """
    获取股票实时价格（使用Tushare Pro API）
    :param code: 股票代码
    :return: 包含股票信息的DataFrame
    """
    try:
        # 获取实时行情
        df = pro.realtime(fields='symbol,price,pre_close,trade_date,trade_time', code=code)

        if df.empty:
            print("实时行情数据为空")
            return pd.DataFrame()

        # 转换日期和时间格式
        df['date'] = df['trade_date'].apply(lambda x: f"{x // 10000}-{(x // 100) % 100}-{x % 100}")
        df['time'] = df['trade_time'].apply(lambda x: f"{x // 10000}:{(x // 100) % 100}:{x % 100}")

        # 添加股票名称
        df['name'] = stock_name

        return df
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return pd.DataFrame()


# 获取股票名称（程序启动时获取一次）
stock_name = get_stock_name(code)


def pd_ztjytime():
    """判断是否在暂停交易的时间段内（11:30-13:00）"""
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_datetime = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

    # 定义暂停交易时间段：11:30:01 到 13:00:00
    d1 = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 11:30:01', '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 13:00:00', '%Y-%m-%d %H:%M:%S')

    delta1 = (now_datetime - d1).total_seconds()
    delta2 = (d2 - now_datetime).total_seconds()

    # 如果当前时间在暂停交易时间段内，返回True
    if delta1 > 0 and delta2 > 0:
        return True
    else:
        return False


def send_Email(Email_address, email_text):
    """发送邮件通知"""
    title = '股票价格异动监控消息-' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = MIMEText(email_text, 'html', 'utf-8')
    msg['From'] = from_addr
    msg['To'] = Email_address
    msg['Subject'] = title

    try:
        # 使用QQ邮箱的SMTP服务器
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(from_addr, password)
        server.send_message(msg)
        server.quit()
        print(f"邮件发送成功至 {Email_address}")
    except Exception as e:
        print(f"邮件发送失败: {e}")


def do_programe(code):
    """核心监控逻辑"""
    if pd_ztjytime() == False:  # 判断是否在暂停交易的时间范围内
        info = get_now_jiage(code)
        if not info.empty:
            now_jiage = float(info['price'][0])
            name = info['name'][0]
            pre_close = float(info['pre_close'][0])
            riqi = info['date'][0]
            sj = info['time'][0]

            # 计算当前涨跌幅
            now_zdie = round((now_jiage - pre_close) / pre_close * 100, 2)
            # 计算总涨跌幅
            all_zdie = round((now_jiage - cbj) / cbj * 100, 2)
            # 计算当前市值
            now_shizhi = round(shuliang * now_jiage, 2)
            # 计算总盈亏
            ykui = round(now_shizhi - cbj * shuliang, 2)

            # 判断涨跌幅是否达到触发条件
            if (abs(now_zdie) >= 3 and abs(now_zdie) < 3.1) or \
                    (abs(now_zdie) >= 6 and abs(now_zdie) < 6.1) or \
                    (abs(now_zdie) >= 9 and abs(now_zdie) < 9.1):
                # 构建邮件内容
                email_comment = []
                email_comment.append('<html>')
                email_comment.append('<b><p><h3><font size="2" color="black">您好：</font></h4></p></b>')
                email_comment.append(
                    f'<p><font size="2" color="#000000">根据设置参数，现将监控到{name}({code})的证券价格异动消息汇报如下：</font></p>')
                email_comment.append(
                    '<table border="1px" cellspacing="0px" width="600" bgcolor=' + color_bg_fg + ' style="border-collapse:collapse">')

                email_comment.append('<tr>')
                email_comment.append('<td align="center"><b>序号</b></td>')
                email_comment.append('<td align="center"><b>购买单价</b></td>')
                email_comment.append('<td align="center"><b>持股数</b></td>')
                email_comment.append('<td align="center"><b>现价</b></td>')
                email_comment.append('<td align="center"><b>现涨跌幅</b></td>')
                email_comment.append('<td align="center"><b>总涨跌幅</b></td>')
                email_comment.append('<td align="center"><b>现市值</b></td>')
                email_comment.append('<td align="center"><b>盈亏额</b></td>')
                email_comment.append('<td align="center"><b>异动时间</b></td>')
                email_comment.append('</tr>')

                email_comment.append('<tr>')
                email_comment.append('<td align="center">1</td>')
                email_comment.append(f'<td align="center">{cbj}</td>')
                email_comment.append(f'<td align="center">{shuliang}</td>')
                email_comment.append(f'<td align="center">{now_jiage}</td>')
                email_comment.append(f'<td align="center">{now_zdie}%</td>')
                email_comment.append(f'<td align="center">{all_zdie}%</td>')
                email_comment.append(f'<td align="center">{now_shizhi}元</td>')
                email_comment.append(f'<td align="center">{ykui}元</td>')
                email_comment.append(f'<td align="center">{riqi} {sj}</td>')
                email_comment.append('</tr>')

                email_comment.append('</table>')
                email_comment.append('<p><font size="2" color="black">祝：股市天天红，日日发大财！</font></p>')
                email_comment.append('</html>')

                send_msg = '\n'.join(email_comment)
                send_Email(email_add[0], send_msg)
                print(f"触发条件：{name}({code}) 涨跌幅 {now_zdie}%，已发送通知")


def run():
    """主监控循环"""
    while True:
        do_programe(code)

        # 检查是否已到收盘时间（15:00）
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        d1 = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
        d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 23:00:00', '%Y-%m-%d %H:%M:%S')
        delta = d2 - d1

        if delta.total_seconds() <= 0:
            print("已到收盘时间，程序退出")
            sys.exit()

        time.sleep(1)


if __name__ == '__main__':
    # 设置每天9:30开始监控
    schedule.every().day.at("09:30").do(run)

    print("盯盘机器人已启动，将在每天9:30开始监控股票价格...")
    print("程序将在15:00收盘后自动退出")

    # 定时任务循环
    while True:
        schedule.run_pending()
        time.sleep(1)