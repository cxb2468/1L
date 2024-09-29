import os
import win32api, win32con


def msgbox(msg, title='提醒'):
    win32api.MessageBox(0, msg, title, win32con.MB_OK)


def local_ip_mac():  # 本机IP和MAC
    output = os.popen('ipconfig /all')
    for i in output:
        if '物理地址.' in i:
            mac = i.split(':')[1].strip()
        if 'IPV4' in i.upper() and '(' in i:
            ip = i.split(':')[1].split('(')[0].strip()
    if ip and mac:
        return [ip, mac]


def lan_ip_mac():  # 局域网IP和MAC
    ls = []
    output = os.popen('arp -a')
    for i in output:
        if '动态' in i:
            ip, mac, _ = i.strip().split()
            ls.append([ip, mac])
    return ls


if __name__ == '__main__':
    res = lan_ip_mac()
    res.append(local_ip_mac())
    print(res)

    # 结果写入文本
    txt = 'ip_mac.txt'
    out_txt = '\n'.join(['\t'.join(i) for i in res])
    with open(txt, 'w') as f:
        f.write(out_txt)

    msgbox(f'提取结果已保存到：{txt}')  # 注释掉此行则不弹窗提醒