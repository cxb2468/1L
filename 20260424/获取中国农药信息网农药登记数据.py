# -*- coding: utf-8 -*-
"""
中国农药信息网 - 农药登记数据爬虫
目标网站: http://www.chinapesticide.org.cn/zwb/dataCenter (农药登记)
数据接口: https://www.icama.cn/BasicdataSystem/pesticideRegistration/
提取字段: 登记证号、农药名称、农药类别、剂型、总含量、有效期至、登记证持有人、持有人地址
"""

import csv
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── 接口地址 ──────────────────────────────────────────────────────
BASE = "https://www.icama.cn/BasicdataSystem/pesticideRegistration"
LIST_URL = f"{BASE}/queryselect.do"
DETAIL_URL = f"{BASE}/viewcompany.do"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

OUTPUT_FILE = "pesticide_data.csv"
CSV_COLUMNS = [
    "登记证号", "农药名称", "农药类别", "剂型",
    "总含量", "有效期至", "登记证持有人", "持有人地址",
]

# ── Session ───────────────────────────────────────────────────────
session = requests.Session()
session.headers.update(HEADERS)


def clean(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", "", text).strip()


# ── 列表请求 ──────────────────────────────────────────────────────
def fetch_list(page: int = 1, size: int = 20) -> List[Dict]:
    """请求列表接口并解析表格"""
    data = {
        "pageNo": str(page),
        "pageSize": str(size),
        "djzh": "", "nymc": "", "cjmc": "", "sf": "", "nylb": "",
        "zhl": "", "jx": "", "zwmc": "", "fzdx": "", "syff": "",
        "dx": "", "yxcf": "", "yxcf_en": "", "yxcfhl": "",
        "yxcf2": "", "yxcf2_en": "", "yxcf2hl": "",
        "yxcf3": "", "yxcf3_en": "", "yxcf3hl": "",
        "yxqs_start": "", "yxqs_end": "",
        "yxjz_start": "", "yxjz_end": "",
        "accOrfuzzy": "2",
    }
    headers = {**HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
    resp = session.post(LIST_URL, data=data, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    if resp.status_code != 200 or len(resp.text) < 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="tab")
    if not table:
        return []

    rows = []
    for idx, tr in enumerate(table.find_all("tr")):
        if idx == 0:
            continue  # 跳过表头
        tds = tr.find_all("td")
        if len(tds) < 7:
            continue

        # 提取纯文本: 7列 = 登记证号|农药名称|农药类别|剂型|总含量|有效期至|登记证持有人
        texts = [clean(td.get_text()) for td in tds]

        # 从 td[6] 的 <a> 中提取持有人名称
        holder_name = texts[6] if len(texts) >= 7 else ""
        cert_code = texts[0]
        holder_td = tds[6] if len(tds) >= 7 else None
        if holder_td:
            a = holder_td.find("a", onclick=True)
            if a:
                a_text = clean(a.get_text())
                if a_text:
                    holder_name = a_text
                m = re.search(r"_viewcompany\('([^']+)'", a["onclick"])
                if m:
                    cert_code = m.group(1)

        rows.append({
            "登记证号": texts[0],
            "农药名称": texts[1],
            "农药类别": texts[2],
            "剂型": texts[3],
            "总含量": texts[4],
            "有效期至": texts[5],
            "登记证持有人": holder_name,
            "持有人地址": "",
            "_cert_code": cert_code or texts[0],  # 用于查详情
        })
    return rows


# ── 持有人详情 ────────────────────────────────────────────────────
def fetch_holder_address(certificate_code: str) -> str:
    """通过 viewcompany.do 获取登记证持有人的单位地址"""
    url = f"{DETAIL_URL}?certificateCode={certificate_code}"
    try:
        resp = session.get(url, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return ""
    except Exception:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # 在 td 中查找"单位地址"字段，地址值在其后的兄弟 td 中
    for td in soup.find_all("td"):
        text = clean(td.get_text())
        if "地址" in text:
            next_td = td.find_next_sibling("td")
            if next_td:
                addr = clean(next_td.get_text())
                if addr and len(addr) > 3:
                    return addr
    return ""


# ── 保存 CSV ──────────────────────────────────────────────────────
def save_csv(rows: List[Dict], filename: str = OUTPUT_FILE):
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in CSV_COLUMNS})


# ── 主流程 ────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("中国农药信息网 - 农药登记数据爬虫")
    log.info("=" * 60)

    # 先测试第1页
    log.info("正在测试列表接口...")
    test_rows = fetch_list(page=1, size=20)
    if not test_rows:
        log.error("列表接口不可用，请检查网络或接口是否变更")
        return

    log.info("接口可用! 第1页返回 %d 条数据", len(test_rows))

    all_rows: List[Dict] = []
    page = 1

    while True:
        log.info("正在抓取第 %d 页...", page)
        rows = fetch_list(page=page) if page > 1 else test_rows
        if not rows:
            log.info("第 %d 页无数据，抓取结束", page)
            break

        # 获取每条的持有人地址
        for row in rows:
            code = row.pop("_cert_code", "")
            if code:
                addr = fetch_holder_address(code)
                row["持有人地址"] = addr
                time.sleep(0.3)
            all_rows.append(row)

        log.info(
            "  第 %d 页完成, 本页 %d 条, 累计 %d 条",
            page, len(rows), len(all_rows),
        )

        # 每页保存一次（防中断）
        save_csv(all_rows)
        page += 1
        time.sleep(0.5)

    # 最终保存
    save_csv(all_rows)
    log.info("抓取完成! 共 %d 条, 已保存至 %s", len(all_rows), OUTPUT_FILE)

    # 预览前5条
    if all_rows:
        log.info("-" * 80)
        for i, r in enumerate(all_rows[:5], 1):
            log.info(
                "[%d] %s | %s | %s | %s | %s | %s | %s | %s",
                i,
                r["登记证号"], r["农药名称"], r["农药类别"],
                r["剂型"], r["总含量"], r["有效期至"],
                r["登记证持有人"], r["持有人地址"],
            )


if __name__ == "__main__":
    main()