# encoding:utf-8
import requests


def telseacher(tel):
    url = 'http://cx.shouji.360.cn/phonearea.php'
    params = {
        'number': tel
    }
    try:
        r = requests.get(url, params=params).json()
        print(r)
        prov = r.get('data').get('province')  # 省
        city = r.get('data').get('city')  # 市
        types = r.get('data').get('sp')  # 运营商

        print(prov, city, types)
        res = prov + ',' + city + ',' + types
        # print(res)
        return res
    except:
        return 'tel_api失效'



if __name__ == "__main__":
    tel = input("Enter a number: ")

    print("telType: ", type(tel))
    print(telseacher(tel))