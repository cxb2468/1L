# mac_vendor.py
import os

# 加载前缀数据库（第一次调用时加载）
_mac_db = {}

def load_prefixes():
    global _mac_db
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, "mac_prefixes.txt"), "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        _mac_db[parts[0].upper()] = parts[1]
    except Exception as e:
        print("厂商数据库加载失败:", e)


def lookup_vendor(mac: str) -> str:
    if not _mac_db:
        load_prefixes()

    if not mac or ":" not in mac:
        return "未知"

    prefix = ":".join(mac.upper().split(":")[:3])
    return _mac_db.get(prefix, "未知")
