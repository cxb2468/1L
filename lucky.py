import requests,sys,webbrowser,bs4

print("Googling....")
req =requests.get("https://www.google.com.hk/search?sxsrf=ALeKk021Oxk4h37LhOu9KmG-JQnEm4KmHQ%3A1610334871603&ei=l8L7X9ipJIjorQGay7LQBQ&q= " + " ".join(sys.argv[1:]))
req.raise_for_status()

#取回搜索结果链接
soup =bs4.BeautifulSoup(req.text)

#打开浏览器栏 为每个结果
links = soup.select(".r a")
numOpen = min(5,len(links))
for i in range(numOpen):
    webbrowser.open("https://www.google.com.hk" + links[i].get("href"))


