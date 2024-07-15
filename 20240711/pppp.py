import os
import subprocess
import requests
import scapy.all as scapy
import sys
import traceback
# http://47.119.173.20:18003/request_cluster_control_code
TARGET_IP = "47.119.173.20"
REGISTER_PORT = 18001
VERIFY_PORT = 18001
CONTROL_PORT = 18003
MODIFIED_RESPONSE_CONTENT = b"gAAAAABmRa5phtw-CaWQuOI6dYxQaL4eXE76iPTs42eMMFYQdAkKAto6ST5elyih8j7uNtosHCOPc3z2yO-JFhK6TljGWxMu6D6A0pjnvGGHOQ7j3fesgDs="
WANZHENG_CONTENT = b"gAAAAABmQsG_M6toB78h-3QtI-hrNdgMSrysnKGr4y4hvPOSS31BpRetMQospPONk8YJpG2wrKAczoOB0pZPIvVgqE9hdRmhJkyvbGTWwxoPYgcrvduu3EgiK-6lBZ22nV4N9JQEWLn7np7XJ1RP8Epb0Ibx9S8azS5gkmRznn0J_OGI2tI2OKbmEFgHT0BCduAd1i_vDtbkf2xxVHBQYmDvY9bEoI30GlAzTVkzbMTgOp3qpBPP5RrWeEklY_QNZabfc1pAI7gvdjE7KyJu9NR-bvF3IGQ5DIvb3PvRPtjpodjFc0xMxmOZJ1gdjSmzed7EOh7IUYxKt5uv0xFt9apFR3ERWfc4Y31boeMgjWzcjRQxbKBLLo4oi7nhZPEdtVFbbCkAumo94nRnUmsiGW0bmSzEthFUT29tgPLqVc88KsLPEhfKxLwQSdGhuVlteiXLUFJx4sJ_6muJRlEyzRVztf9vhXO7GS_Ptqb4f8vUyg63wBlgsvxU-PZ7ebNJb_IUaH_a65cLqF94Z1hHM5Y0dSn6uEIUMgmdjNhZHlr-inqsJq8eKAc7hapenBmSrermBMcBEVR89MgI6SlFkgFHF_Glv7IIIvbEFRl0fYxD-q1q1ZiUfJe_ruxa2bmOqLKS3NhPuLPi4yNuHUl4MUgIScwkInTqVtNC_eI1U3PV2S6xupifhrz1tkfz3FRfHj46eaGf-iPqoEBD6nk3YRl6nl6sFisslCWzNVsmRMTocLFqlIFH2ChPIj1K4tbq5e0WZpIHgZ3EHD6spCsWFueFVmDG1qKzL3Yv-GoP-53K4d9xIiVRhmdk_K2lDSnhR6zvWAKBUratbFEfZyZpj_MDlarxX5HudZs1Kg7tZd5cEVrK_IMKfnvBFe7H_Q_3KzbkgJhQnEmnYgeRgZggh-Yp1cCcseEIIw=="
XINXI_CONTENT = b'gAAAAABmQepEbWe8a-WrXuftttxLhXB6_XJCMoz80UzJfNU5WvGKbHhyUJJ_dr54tAmOjm8YWcJuQNg9XSQDLvZBcBQFcu6t_dtE1LuZLOMoUw5I61TbVwJANHZ14lL8pA822TPX60k-Yc6ZGUExKP49AERMFAP7iuvYhLspAX8oN6Wc_y4hRv4ii4aLcS3yI7SeTonWsG4kFvRsQm--VCoM-AFVgTpIC3ygyen7bGM-oHKMf-3U2gLzgJIgxV-NbJupzJXhNBJQcxHorJg4bLCFMdaMNsTovL4R0PgImIItwHXxJbfKaow='

NPCAP_URL = "https://nmap.org/npcap/dist/npcap-1.55.exe"  # Npcap 的下载链接
NPCAP_INSTALLER = "npcap-1.55.exe"

def is_npcap_installed():
    try:
        scapy.conf.L3socket
        return True
    except AttributeError:
        return False

def download_npcap(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            file.write(data)
    print(f"{filename} downloaded successfully.")

def install_npcap(installer_path):
    try:
        subprocess.run([installer_path, '/S', '/winpcap_mode'], check=True)
        print("Npcap installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Npcap: {e}")
        sys.exit(1)

def create_modified_response(content):
    response_payload = (
                           f"HTTP/1.1 200 OK\r\n"
                           f"Content-Length: {len(content)}\r\n"
                           f"Content-Type: text/plain\r\n"
                           f"Connection: close\r\n\r\n"
                       ).encode() + content
    return response_payload

def create_header_only_response():
    content = b'这里是云端代码加密后的字符串，太长了我懒得写，排版也不好看，自己填一下'
    response_payload = (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Connection: close\r\n\r\n"
        ).encode() + content
    return response_payload

def packet_callback(packet):
    if packet.haslayer(scapy.IP) and packet.haslayer(scapy.TCP) and packet.haslayer(scapy.Raw):
        payload = packet[scapy.Raw].load
        if packet[scapy.IP].dst == TARGET_IP and packet[scapy.TCP].dport == REGISTER_PORT:
            if b'POST /software_register' in payload:
                print("[Scapy] 注册请求")
                response_payload = create_modified_response(MODIFIED_RESPONSE_CONTENT)
            elif b'POST /software_verify' in payload:
                print("[Scapy] 心跳请求")
                response_payload = create_modified_response(MODIFIED_RESPONSE_CONTENT)
            else:
                return

        elif packet[scapy.IP].dst == TARGET_IP and packet[scapy.TCP].dport == CONTROL_PORT:
            if b'GET /request_cluster_control_code' in payload:
                print("[Scapy] 远程代码请求")
                response_payload = create_header_only_response()
            elif b'GET /multiple_files_value_verify' in payload:
                return
                print("[Scapy] 完整性校验请求")
                response_payload = create_modified_response(WANZHENG_CONTENT)
            elif b'POST /request_software_information' in payload:  # http://47.119.173.20:18003/request_software_information
                return
                print("[Scapy] 软件信息请求")
                response_payload = create_modified_response(XINXI_CONTENT)
            else:
                # print("[Scapy] payload",payload)
                return

        else:
            return

        # 创建新的数据包，包含伪造的响应内容
        modified_packet = (
                scapy.IP(dst=packet[scapy.IP].src, src=packet[scapy.IP].dst) /
                scapy.TCP(dport=packet[scapy.TCP].sport, sport=packet[scapy.TCP].dport, seq=packet[scapy.TCP].ack,
                          ack=packet[scapy.TCP].seq + len(packet[scapy.Raw]), flags='PA') /
                scapy.Raw(load=response_payload)
        )

        # 发送伪造的响应
        scapy.send(modified_packet)
        print("[Scapy] Sent modified response")
