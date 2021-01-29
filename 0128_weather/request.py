import requests
req =requests.get("http://www.weather.com.cn/data/sk/101010100.html")
req.encoding = "utf-8"

print(req.json())
print("城市:"+req.json()["weatherinfo"]["city"])
print("温度：%s " % req.json()["weatherinfo"]["temp"]+" 度")