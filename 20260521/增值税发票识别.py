import re
import sys

import pandas as pd
import wcocr
# 本地 wcocr.pyd文件
import os

wechat_path = os.getcwd() + r"\wxocr2"
wechatocr3_path = os.getcwd() + r"\wxocr2\WeChatOCR.exe"


# ==================== 核心：自动格式化发票 ====================
def format_invoice(ocr_result):
    # 过滤低置信度噪点文本
    valid_texts = []
    for item in ocr_result:
        txt = item.get("text", "").strip()
        score = item.get("rate", 0.0)
        if txt and score >= 0.5:
            valid_texts.append(txt)

    full_str = " ".join(valid_texts)
    res = {
        "发票号码": "",
        "不含税金额": "",
        "税额": "",
        "价税合计": "",
        "税率": "",
        "销售方信息": "",
        "开票日期": "",
        "发票类型": ""
    }

    # 1. 发票类型识别
    if "增值税专" in full_str and "用发票" in full_str:
        res["发票类型"] = "增值税专用发票"
    elif "电子发票" in full_str:
        res["发票类型"] = "增值税电子普通发票"
    elif "普通发票" in full_str:
        res["发票类型"] = "增值税普通发票"

    # 2. 发票号码
    num_reg = re.search(r"发票号码\s*[:：]\s*(\d+)", full_str)
    if num_reg:
        res["发票号码"] = num_reg.group(1)

    # 3. 开票日期
    date_reg = re.search(r"开票日期\s*[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)", full_str)
    if date_reg:
        res["开票日期"] = date_reg.group(1).replace("年", "-").replace("月", "-").replace("日", "")

    # 4. 税率 通用匹配 0%-17%
    rate_reg = re.search(r"(\d{1,2}\.?\d?)%", full_str)
    if rate_reg:
        res["税率"] = rate_reg.group(1) + "%"

    # 5. 提取所有金额数字（保留两位小数）必须带 ￥ 或者 &#165;
    money_pat = re.compile(r"[￥&#165;]\s*(\d+\.\d{2})")
    all_money = money_pat.findall(full_str)
    # 去重
    money_list = list(set(all_money))
    # print(money_list)
    # 转浮点排序：小=税额 中=不含税 大=价税合计
    try:
        money_sort = sorted([float(m) for m in money_list])
        if len(money_sort) >= 3:
            res["税额"] = f"{money_sort[0]:.2f}"
            res["不含税金额"] = f"{money_sort[1]:.2f}"
            res["价税合计"] = f"{money_sort[2]:.2f}"
        elif len(money_sort) == 2:
            res["不含税金额"] = f"{money_sort[0]:.2f}"
            res["价税合计"] = f"{money_sort[1]:.2f}"
    except:
        pass
    # 金额校准
    try:
        if float(res["税额"]) + float(res["不含税金额"]) == float(res["价税合计"]):
            res["金额校准"] = "正确"
        else:
            res["金额校准"] = "出错"
    except:
        res["金额校准"] = "出错"

    # 6. 销售方信息整合
    # print(valid_texts)
    # #seller_keys = ["销售方", "纳税人识别号", "统一社会信用代码", "销售方地址", "开户行", "银行账号"]
    seller_keys = ["名称"]
    seller_data = []
    for text in valid_texts:
        if any(k in text for k in seller_keys):
            if len(text) > 6:  # 防止识别到关键字，但是不是公司名
                seller_data.append(text)
    # 6. 销售方信息：只取 名称: 开头的销售方名称
    # 规则：两个名称，靠后出现的为销售方
    # 第二个名称为销售方
    # print(seller_data)
    if len(seller_data) >= 2:
        res["销售方信息"] = seller_data[1][3:].strip()
    elif len(seller_data) == 1:
        res["销售方信息"] = seller_data[0][3:].strip()
    # res["销售方信息"] = " | ".join(seller_data)
    return res


def get_all_jpg_files(folder_path):
    """
    遍历指定文件夹，返回所有 .jpg 文件的完整路径列表
    :param folder_path: 文件夹路径（如 "C:/发票/2025"）
    :return: 所有 jpg 绝对路径列表
    """
    jpg_files = []

    # 遍历文件夹
    for filename in os.listdir(folder_path):
        # 只筛选 .jpg 文件（不区分大小写，也支持 .JPG）
        if filename.lower().endswith(".jpg"):
            full_path = os.path.join(folder_path, filename)
            jpg_files.append(full_path)

    return jpg_files


if __name__ == '__main__':
    # OUTPUT_EXCEL = "发票信息汇总表.xlsx"  # 输出表格名
    # if len(sys.argv) < 2:
    while 1:
        print("使用方法：")
        print("   输入发票文件夹路径即可")
        print("   当前只支持后缀为.jpg格式发票图片")
        print("示例：")
        print(r"  D:\发票\2026")
        # 命令行参数：只需要文件夹
        img_folder = input("发票路径：")
        if not os.path.isdir(img_folder):
            print(f"错误：文件夹不存在 → {img_folder}")
            continue

        # 开始处理
        print("开始批量处理发票...")
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        OUTPUT_EXCEL = os.path.join(exe_dir, "发票信息汇总表.xlsx")
        # print(os.getcwd())
        tried_v3 = False
        if os.path.isfile(wechatocr3_path) and os.path.isdir(wechat_path):
            tried_v3 = True
            wcocr.init(wechatocr3_path, wechat_path)
        else:
            print("找不到微信3.x配置，或者不正确")
            continue
            # 1. 设置你的文件夹路径
        # target_folder = r"D:\python\Python+EasyOCR\png"  # 改成你自己的路径
        if tried_v3:
            # 2. 获取所有 jpg
            jpg_list = get_all_jpg_files(img_folder)

            # 3. 打印结果
            print(f"找到 {len(jpg_list)} 张 jpg 发票：")
            if len(jpg_list) > 0:
                all_data = []
                for path in jpg_list:
                    print(path)
                    print("+" * 30)
                    # jpgfile = input("输入图片文件名：")
                    result = wcocr.ocr(path)
                    # print(result)
                    # break
                    # 2. 自动格式化
                    invoice = format_invoice(result['ocr_response'])
                    # 3. 输出漂亮格式
                    invoice["图片路径"] = path  # 加入文件名方便核对
                    all_data.append(invoice)
                    # print("\n" + "=" * 50)
                    # print("          发票识别结果（格式化完成）")
                    # print("=" * 50)
                    # for key, value in invoice.items():
                    #     print(f"{key}：{value}")
                    # print("=" * 50)
                # 3. Pandas 输出Excel
                df = pd.DataFrame(all_data)
                df.to_excel(OUTPUT_EXCEL, index=False)

                print(f"\n&#9989; 提取完成！已保存到：{OUTPUT_EXCEL}")