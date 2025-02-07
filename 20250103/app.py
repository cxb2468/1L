import requests
import websockets
import json
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor


# 0. 定义全局变量
txnid = 1
with open("postdata.json", "r") as f:
    postdata = json.load(f)
    f.close()

github_domains = [
    "github.com",
    "raw.githubusercontent.com",
    "avatars.githubusercontent.com",
    "github.githubassets.com",
    "api.github.com",
    "gist.github.com",
    "codeload.github.com",
    "github.io",
    "githubstatus.com",
]


# 1. 获取 ut、code、user


def checkuser(domain):
    url = "https://17ce.com/site/checkuser"
    wss = "wss://wsapi.17ce.com:8001/socket/?"
    logindata = {
        "url": domain,
        "type": "1",
        "isp": "0",
    }
    headers = {
        "Referer": "https://17ce.com/",
    }
    try:
        with requests.Session() as session:
            response = session.post(url, data=logindata, headers=headers)
            resdata = response.json()
    except Exception as e:
        print(f"请求 checkuser 出错: {e}")
        return None
    wsurl = (
        f"user={resdata.get('data', {}).get('user', '').replace('@', '%40')}"
        f"&code={resdata.get('data', {}).get('code')}"
        f"&ut={resdata.get('data', {}).get('ut')}"
    )
    wss += wsurl
    return wss


# 2. 发送登录消息
async def loginsend(domain):
    wss = checkuser(domain)
    # 清空 hosts，以便下一个域名测试使用
    hosts = []
    if not wss:
        return []
    hosts = []
    async with websockets.connect(wss) as ws:
        try:
            result = await ws.recv()
            firdata = json.loads(result)
            if firdata.get("rt") == 1 and firdata.get("msg") == "login ok":
                print("****************登录成功****************")
                # 发送 postdata
                postdata.update({"Url": domain})
                postdata.update({"SrcIP": domain})
                # print(postdata)
                # print(postdata["SrcIP"])
                await ws.send(json.dumps(postdata))
                print("****************发送成功****************")
                while True:
                    result = await ws.recv()
                    secdata = json.loads(result)
                    # print(secdata)
                    if secdata.get("type") == "TaskAccept":
                        print("****************任务开始****************")
                    elif secdata.get("type") == "NewData":
                        src_ip = secdata.get("data", {}).get("SrcIP", "")
                        if src_ip and src_ip not in hosts:
                            hosts.append(src_ip)
                        print(
                            f"****************当前 domain:{domain}*****获取到host:{src_ip}****************"
                        )
                    elif secdata.get("type") == "TaskEnd":
                        print("****************任务完成****************")
                        break
                    elif secdata.get("type") == "TaskErr":
                        print("****************任务失败****************")
                        break
        except Exception as e:
            print(f"WebSocket 操作出错: {e}")
    return hosts


# 3. 处理 hosts ，删除 127.0。0.1 等内网以及无效数据
def process_hosts(hosts):
    if not hosts:
        return []
    # 去除重复元素
    hosts = list(set(hosts))
    # 筛选出不满足条件的元素
    processed_hosts = [
        host
        for host in hosts
        if not (
            host.startswith("127.0.")
            or host.startswith("192.168")
            or host.startswith("10.")
            or host.startswith("172.")
            or host.startswith("169.254")
            or host.startswith("0.0")
        )
    ]
    print(f"*********共获取到 {len(processed_hosts)} 个有效 host**************")
    return processed_hosts


# 4. 多线程获取最快速的 host


def get_fastest_host(hosts):
    if not hosts:
        return None
    speed_dict = {}
    lock = threading.Lock()

    def test_host_speed(host):
        try:
            start_time = time.time()
            # 发送 HEAD 请求，因为我们只关心响应时间，不需要响应体
            response = requests.head(f"http://{host}", timeout=5)
            end_time = time.time()
            # 计算时间差，作为该 host 的速度
            speed = end_time - start_time
            with lock:
                speed_dict[host] = speed
        except requests.RequestException:
            with lock:
                speed_dict[host] = float("inf")

    threads = []
    for host in hosts:
        t = threading.Thread(target=test_host_speed, args=(host,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # 找到速度最快的 host
    if not speed_dict:
        return None
    fastest_host = min(speed_dict, key=speed_dict.get)
    return fastest_host


# 5. 获取 github 域名的最快 host，并返回字典
def get_github_dict():
    domaindict = {}
    global txnid
    global postdata
    global github_domains
    for domain in github_domains:
        print(f"************开始测试 {domain}************")
        hosts = asyncio.run(loginsend(domain))
        hosts = process_hosts(hosts)
        fastest_host = get_fastest_host(hosts)
        if fastest_host:
            print(f"************{domain} 最快的 host 为：{fastest_host}************")
            domaindict.update({domain: fastest_host})
        else:
            print(f"************{domain} 无有效 host************")
        txnid += 1
        postdata["txnid"] = txnid
    print(domaindict)
    return domaindict


# 6. 主函数，获取字典并写入到文件
def main():
    github_dict = get_github_dict()
    with open("github_dict.json", "w") as f:
        json.dump(github_dict, f)
        f.close()
    # 写 hosts 格式
    with open("hosts.txt", "w") as f:
        for domain, host in github_dict.items():
            f.write(f"{host} {domain}\n")
        f.close()


if __name__ == "__main__":
    main()
