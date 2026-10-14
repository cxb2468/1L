"""DHL 运单查询
仅依赖 curl_cffi，无需 Akamai sensor / _abck 流程
关键：impersonate="chrome"（自动用最新 Chrome TLS 指纹）
"""
import json
import sys
from curl_cffi import requests


def query(tracking_number: str) -> dict:
    """查询单个 DHL 运单，返回原始 JSON"""
    url = "https://www.dhl.com/utapi"
    params = {
        "trackingNumber": tracking_number,
        "language": "zh",
        "requesterCountryCode": "CN",
        "source": "tt",
    }
    headers = {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": "https://www.dhl.com/cn-zh/home/tracking.html",
    }
    r = requests.get(url, params=params, headers=headers, impersonate="chrome")
    r.raise_for_status()
    return r.json()


def _place(addr: dict) -> str:
    """从地址字典中提取可读地点：优先城市，其次国家、邮编"""
    if not addr:
        return "-"
    parts = [addr.get("addressLocality"), addr.get("countryCode"), addr.get("postalCode")]
    return ", ".join(str(p) for p in parts if p) or "-"


def brief(data: dict) -> str:
    """提取关键字段输出"""
    lines = []
    for s in data.get("shipments", []):
        st = s.get("status", {})
        loc = (st.get("location") or {}).get("address", {})
        events = s.get("events", [])
        # utapi 通常不返回 origin/destination，起止地需从 events 推导：
        # events 按时间倒序，最早一条(列表末尾)为始发地，最新一条为目的地/当前
        origin_addr = (s.get("origin") or {}).get("address")
        dest_addr = (s.get("destination") or {}).get("address")
        if not origin_addr and events:
            origin_addr = (events[-1].get("location") or {}).get("address", {})
        if not dest_addr and events:
            dest_addr = (events[0].get("location") or {}).get("address", {})
        lines.append(
            f"单号     : {s.get('id')}\n"
            f"服务     : {s.get('service')}\n"
            f"始发地   : {_place(origin_addr)}\n"
            f"目的地   : {_place(dest_addr)}\n"
            f"当前状态 : {st.get('description')} @ {st.get('timestamp')}\n"
            f"当前位置 : {_place(loc)}\n"
            f"轨迹条数 : {len(events)}"
        )
    return "\n---\n".join(lines) if lines else "(无 shipments 数据)"


if __name__ == "__main__":
    # 用法: python demo.py 1234567890
    tn = sys.argv[1] if len(sys.argv) > 1 else "1234567890"  ## 默认测试单号
    raw = query(tn)
    print(f"===== 运单 {tn} =====")
    print(brief(raw))
    # 如需完整原始数据，取消下一行注释
    # print(json.dumps(raw, ensure_ascii=False, indent=2))