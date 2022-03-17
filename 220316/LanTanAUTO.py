import requests
import random
from lxml import etree
import time
import re



def test_cookie():
    global cookies
    url = "https://bbs.125.la/plugin.php?id=dsu_paulsign:sign"
    headers = {
        'cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    }
    session = requests.session()
    rep = session.get(url=url, headers=headers)
    if rep.status_code == 200:
        print("登录成功")
        # checkin()
        for i in range(1):
            comment()
            time.sleep(7)
            score()
            time.sleep(8)
            print('休息中')
    else:
        print("异常了，快看看")


def comment():
    text = """
        Host: bbs.125.la
        Connection: keep-alive
        Content-Length: 81
        Cache-Control: max-age=0
        sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99"
        sec-ch-ua-mobile: ?0
        sec-ch-ua-platform: "Windows"
        Upgrade-Insecure-Requests: 1
        Origin: https://bbs.125.la
        Content-Type: application/x-www-form-urlencoded
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Sec-Fetch-Site: same-origin
        Sec-Fetch-Mode: navigate
        Sec-Fetch-User: ?1
        Sec-Fetch-Dest: iframe
        Referer: https://bbs.125.la/thread-14721307-1-1.html
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
        Cookie:lDlk_ecc9_lastvisit=1647405725; lDlk_ecc9_client_created=1647409343; lDlk_ecc9_client_token=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_connect_login=1; lDlk_ecc9_connect_is_bind=1; lDlk_ecc9_connect_uin=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_stats_qc_login=3; lDlk_ecc9_myrepeat_rr=R0; lDlk_ecc9_nofavfid=1; lDlk_ecc9_ulastactivity=abb4hl9Y2UfPFUWxdOgst2v28rqy1u0RqJfkWlNIvuRJqW74Hk47; Hm_lvt_fa32dadde3745af309b587b38d20ea1d=1647408605,1647478272; PHPSESSID=0tabgf7rli69ftcsrmvbm10gei; Hm_lpvt_c6927066ad2f2806b262f20b26fabff4=1647478293; Hm_lvt_c6927066ad2f2806b262f20b26fabff4=1647408661,1647478293; lDlk_ecc9_st_t=577977%7C1647478320%7C3ee35baa3a92ad2b200ae6946cd069d0; lDlk_ecc9_atarget=1; lDlk_ecc9_forum_lastvisit=D_125_1647478320; lDlk_ecc9_smile=4D1; lDlk_ecc9_sid=MwMaW6; lDlk_ecc9_lip=112.25.180.198%2C1647480525; lDlk_ecc9_st_p=577977%7C1647480526%7C50781de5407bc69a6c6c641d9118f4d0; lDlk_ecc9_visitedfid=16D125; lDlk_ecc9_viewid=tid_14716817; lDlk_ecc9_lastcheckfeed=577977%7C1647480527; lDlk_ecc9_sendmail=1; lDlk_ecc9_lastact=1647480543%09plugin.php%09vest; Hm_lpvt_fa32dadde3745af309b587b38d20ea1d=1647480527
        """
    dic = get_canshu()
    tid = dic['tid']
    formhash = dic['formhash']
    url = 'https://bbs.125.la/forum.php?mod=post&action=reply&fid=98&tid=' + tid + '&fromvf=1&extra=page=1&replysubmit=yes&infloat=yes&handlekey=vfastpost&inajax=1'
    headers = trans_headers2(text)
    data = 'formhash=' + formhash + '&message=+%E9%A1%B6%EF%BC%8C%E5%AD%A6%E4%B9%A0%E4%B8%80%E4%B8%8B'
    session = requests.session()
    rep = session.post(url=url, headers=headers, data=data)
    print(rep.text)


def trans_headers2(text):  # 格式化请求头
    headers = text
    headers = headers.strip().split('\n')
    headers = {x.split(':')[0].strip(): ("".join(x.split(':')[1:])).strip().replace('//', "://") for x in headers}
    return headers


def get_canshu():  # 获取formhash , tid , pid,以字典返回
    global page_number
    url = 'https://bbs.125.la/thread-' + get_page()[page_number] + '-1-1.html'
    print(get_page()[page_number])
    text = '''
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
    cache-control: max-age=0
    Cookie:lDlk_ecc9_lastvisit=1647405725; lDlk_ecc9_client_created=1647409343; lDlk_ecc9_client_token=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_connect_login=1; lDlk_ecc9_connect_is_bind=1; lDlk_ecc9_connect_uin=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_stats_qc_login=3; lDlk_ecc9_myrepeat_rr=R0; lDlk_ecc9_nofavfid=1; lDlk_ecc9_ulastactivity=abb4hl9Y2UfPFUWxdOgst2v28rqy1u0RqJfkWlNIvuRJqW74Hk47; Hm_lvt_fa32dadde3745af309b587b38d20ea1d=1647408605,1647478272; PHPSESSID=0tabgf7rli69ftcsrmvbm10gei; Hm_lpvt_c6927066ad2f2806b262f20b26fabff4=1647478293; Hm_lvt_c6927066ad2f2806b262f20b26fabff4=1647408661,1647478293; lDlk_ecc9_st_t=577977%7C1647478320%7C3ee35baa3a92ad2b200ae6946cd069d0; lDlk_ecc9_atarget=1; lDlk_ecc9_forum_lastvisit=D_125_1647478320; lDlk_ecc9_smile=4D1; lDlk_ecc9_sid=MwMaW6; lDlk_ecc9_lip=112.25.180.198%2C1647480525; lDlk_ecc9_st_p=577977%7C1647480526%7C50781de5407bc69a6c6c641d9118f4d0; lDlk_ecc9_visitedfid=16D125; lDlk_ecc9_viewid=tid_14716817; lDlk_ecc9_lastcheckfeed=577977%7C1647480527; lDlk_ecc9_sendmail=1; lDlk_ecc9_lastact=1647480543%09plugin.php%09vest; Hm_lpvt_fa32dadde3745af309b587b38d20ea1d=1647480527
    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Windows"
    sec-fetch-dest: document
    sec-fetch-mode: navigate
    sec-fetch-site: cross-site
    sec-fetch-user: ?1
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39
    '''
    headers = trans_headers2(text)
    rep = requests.get(url=url, headers=headers).text
    # pattern=re.compile(r'formhash=(.*?)\"')
    formhash_init = re.search(r'formhash=(?P<formhash>.*?)"', rep)
    pid_init = re.search(r'pid(?P<pid>.*?)"', rep)

    cansu = {}
    cansu['formhash'] = formhash_init.group("formhash")
    cansu['tid'] = get_page()[page_number]
    cansu['pid'] = pid_init.group("pid")
    print(cansu)
    return cansu


def score():  # 进行每日评分，注意，每日4分
    global cookies
    try:
        headers = {
            'cookie': cookies,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
        }
        session = requests.session()
        dic = get_canshu()
        tid = dic['tid']
        pid = dic['pid']
        formhash = dic['formhash']
        url_page = 'https://bbs.125.la/thread-' + tid + '-1-1.html'
        rep = session.get(url=url_page, headers=headers)
        print(url_page)
        print("获取pid={}与tid={}与formash={}成功，开始自动评分".format(pid, tid, formhash))
        # 开始评分
        url_score = 'https://bbs.125.la/forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1'
        data = 'formhash=' + formhash + '&tid=' + tid + '&pid=' + pid + '&referer=https%3A%2F%2Fbbs.125.la%2Fforum.php%3Fmod%3Dviewthread%26tid%3D' + tid + '%26page%3D0%23pid' + pid + '&handlekey=rate&score4=%2B1&reason=%E6%84%9F%E8%B0%A2%E5%88%86%E4%BA%AB%EF%BC%8C%E5%BE%88%E7%BB%99%E5%8A%9B%EF%BC%81%7E'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Referer'] = 'https://bbs.125.la/thread-' + tid + '-1-1.html'
        rep_score = session.post(url=url_score, data=data, headers=headers)
        print(rep_score.text)
    except:
        print('不存在帖子')


# 获取易语言源码模块的第二页帖子
def get_page():
    text = '''
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
    cache-control: max-age=0
    Cookie:lDlk_ecc9_lastvisit=1647405725; lDlk_ecc9_client_created=1647409343; lDlk_ecc9_client_token=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_connect_login=1; lDlk_ecc9_connect_is_bind=1; lDlk_ecc9_connect_uin=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_stats_qc_login=3; lDlk_ecc9_myrepeat_rr=R0; lDlk_ecc9_nofavfid=1; lDlk_ecc9_ulastactivity=abb4hl9Y2UfPFUWxdOgst2v28rqy1u0RqJfkWlNIvuRJqW74Hk47; Hm_lvt_fa32dadde3745af309b587b38d20ea1d=1647408605,1647478272; PHPSESSID=0tabgf7rli69ftcsrmvbm10gei; Hm_lpvt_c6927066ad2f2806b262f20b26fabff4=1647478293; Hm_lvt_c6927066ad2f2806b262f20b26fabff4=1647408661,1647478293; lDlk_ecc9_st_t=577977%7C1647478320%7C3ee35baa3a92ad2b200ae6946cd069d0; lDlk_ecc9_atarget=1; lDlk_ecc9_forum_lastvisit=D_125_1647478320; lDlk_ecc9_smile=4D1; lDlk_ecc9_sid=MwMaW6; lDlk_ecc9_lip=112.25.180.198%2C1647480525; lDlk_ecc9_st_p=577977%7C1647480526%7C50781de5407bc69a6c6c641d9118f4d0; lDlk_ecc9_visitedfid=16D125; lDlk_ecc9_viewid=tid_14716817; lDlk_ecc9_lastcheckfeed=577977%7C1647480527; lDlk_ecc9_sendmail=1; lDlk_ecc9_lastact=1647480543%09plugin.php%09vest; Hm_lpvt_fa32dadde3745af309b587b38d20ea1d=1647480527
    referer: https://bbs.125.la/
    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Microsoft Edge";v="99"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Windows"
    sec-fetch-dest: document
    sec-fetch-mode: navigate
    sec-fetch-site: same-origin
    sec-fetch-user: ?1
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39
    '''
    headers = trans_headers2(text)
    url = 'https://bbs.125.la/forum-98-2.html'
    session = requests.session()
    rep = session.get(url=url, headers=headers)
    print(rep)
    tree = etree.HTML(rep.text)
    tbody_list = tree.xpath('/html/body/div[7]/div[5]/div/div/div[5]/div[2]/form/table/tbody')
    id_list = []
    for tbody in tbody_list:
        id_list.append(tbody.xpath('@id'))
    del id_list[0]
    id = []
    for i in range(len(id_list)):
        id.append(id_list[i - 1][0])
    for i in range(len(id)):
        id[i - 1] = id[i - 1].split('_')[1]
    return id


def checkin():  # 签到
    global cookies
    url = "https://bbs.125.la/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1"
    data = {
        "formhash": "8b9834f2",
        "submit": "1",
        "targerurl": "",
        "todaysay": "",
        "qdxq": "kx"
    }
    headers = {
        'cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    }
    session = requests.session()
    rep = session.post(url=url, headers=headers, data=data)
    jso = rep.json()
    print(jso)


if __name__ == "__main__":
    cookies = 'lDlk_ecc9_lastvisit=1647405725; lDlk_ecc9_client_created=1647409343; lDlk_ecc9_client_token=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_connect_login=1; lDlk_ecc9_connect_is_bind=1; lDlk_ecc9_connect_uin=E68E19C6A53BCAFB68D9EF859620A67B; lDlk_ecc9_stats_qc_login=3; lDlk_ecc9_myrepeat_rr=R0; lDlk_ecc9_nofavfid=1; lDlk_ecc9_ulastactivity=abb4hl9Y2UfPFUWxdOgst2v28rqy1u0RqJfkWlNIvuRJqW74Hk47; Hm_lvt_fa32dadde3745af309b587b38d20ea1d=1647408605,1647478272; PHPSESSID=0tabgf7rli69ftcsrmvbm10gei; Hm_lpvt_c6927066ad2f2806b262f20b26fabff4=1647478293; Hm_lvt_c6927066ad2f2806b262f20b26fabff4=1647408661,1647478293; lDlk_ecc9_st_t=577977%7C1647478320%7C3ee35baa3a92ad2b200ae6946cd069d0; lDlk_ecc9_atarget=1; lDlk_ecc9_forum_lastvisit=D_125_1647478320; lDlk_ecc9_smile=4D1; lDlk_ecc9_sid=MwMaW6; lDlk_ecc9_lip=112.25.180.198%2C1647480525; lDlk_ecc9_st_p=577977%7C1647480526%7C50781de5407bc69a6c6c641d9118f4d0; lDlk_ecc9_visitedfid=16D125; lDlk_ecc9_viewid=tid_14716817; lDlk_ecc9_lastcheckfeed=577977%7C1647480527; lDlk_ecc9_sendmail=1; lDlk_ecc9_lastact=1647480543%09plugin.php%09vest; Hm_lpvt_fa32dadde3745af309b587b38d20ea1d=1647480527'
    page_number = random.randint(0, 40)
    print(page_number)
    test_cookie()

# 腾讯云函数用这个
# def main_handler(*args):  # 腾讯云函数
#     main()
#
# def main():
#     cookies = '换cookies'
#     page_number = random.randint(0, 40)
#     test_cookie()
#
# if __name__ == '__main__':
#     main()