# scanner.py
import subprocess
import platform
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from getmac import get_mac_address
import utils
import mac_vendor


def ping(ip):
    system = platform.system().lower()
    cmd = ["ping", "-n", "1", "-w", "300", ip] if system == "windows" else ["ping", "-c", "1", "-W", "1", ip]

    startupinfo = None
    if system == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
        return result.returncode == 0
    except:
        return False


def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "未知主机"


def get_device_icon(hostname, mac):
    hostname = hostname.lower()
    vendor = mac_vendor.lookup_vendor(mac).lower() if mac else ""

    if "printer" in hostname or "printer" in vendor:
        return "🖨️"
    elif any(k in hostname for k in ["iphone", "ipad", "android", "huawei", "oppo", "vivo", "honor", "realme"]):
        return "📱"
    elif any(k in vendor for k in ["hp", "epson", "canon", "brother", "printer"]):
        return "🖨️"
    elif any(k in vendor for k in ["apple", "samsung", "zte", "xiaomi", "vivo", "realme", "huawei"]):
        return "📱"
    elif "virtual" in vendor or "vmware" in vendor or "hyper-v" in vendor:
        return "💻"
    else:
        return "👨‍💻"


def scan_ip_range(ip_range, progress_callback=None):
    ip_list = utils.parse_ip_range(ip_range)
    total = len(ip_list)
    results = []
    count = 0

    with ThreadPoolExecutor(max_workers=200) as executor:
        future_map = {executor.submit(ping, ip): ip for ip in ip_list}

        for future in as_completed(future_map):
            ip = future_map[future]
            try:
                is_up = future.result()
                hostname = resolve_hostname(ip) if is_up else ""
                mac = get_mac_address(ip=ip) if is_up else ""
                vendor = mac_vendor.lookup_vendor(mac) if mac else "未知"
                status = "✅ 已启用" if is_up else "❌ 未启用"
                icon = get_device_icon(hostname, mac)

                if is_up:
                    results.append([ip, hostname, mac or "未知", vendor, status, icon])
            except:
                pass

            count += 1
            if progress_callback:
                try:
                    progress_callback.emit(int(count * 100 / total))
                except:
                    pass

    return results
