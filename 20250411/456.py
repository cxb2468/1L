import json
import os
import requests

# 直接将JSON数据赋值给一个变量
data = {
    "status": 200,
    "data": {
        "id": "26359",
        "code": "XMTSKC001002",
        "name": "学校安全教育的定位、职责与标准",
        "recommendLearnTime": 12,
        "sectionCount": 0,
        "teacher": "李雯",
        "introduction": "<p> 课程站在学校安全教育实践的视角，通过理论阐述和案例分析，确定了学校安全教育的基本定位、讲解了学校安全教育的主要职责，明确了学校安全教育的实施标准，总结了学校安全教育的创新探索。本专题课程旨在为中小学校长和教师理解、设计和实施学校安全教育提供整体思路和重要启发。 </p>",
        "resourceItemList": [
            {
                "itemId": "32047a9f-9aa0-439d-8349-49d0f8118388",
                "parentItemId": "00000000-0000-0000-0000-000000000000",
                "directory": False,
                "itemName": "内容提要",
                "resourceId": "441",
                "resourceUrl": "https://doc.xiaoben365.com/Attachment/SCORM/86FCE567-4C8B-44DF-8247-F02D7028B881/intro.html",
                "resourceType": "URL",
                "breakPoint": 0,
                "finished": True,
                "lastTimeView": False
            },
            {
                "itemId": "d31fadcc-1caf-44ba-a373-f451e76f9c27",
                "parentItemId": "00000000-0000-0000-0000-000000000000",
                "directory": True,
                "itemName": "第一讲 学校安全教育的基本定位",
                "breakPoint": 0,
                "finished": False,
                "lastTimeView": False
            },
            {
                "itemId": "ab826dc4-f266-46ec-8577-ad9bfdeed9a2",
                "parentItemId": "0023840e-2d19-41b6-b942-af231639fa63",
                "directory": False,
                "itemName": "第二节 学校安全教育的创新探索（二）",
                "resourceId": "485",
                "resourceUrl": "https://gpmp4.open.com.cn/M604/guopei_mp4/2014/gz_ts/XMTS0901/4_2_g.mp4",
                "resourceType": "VIDEO",
                "breakPoint": 217,
                "finished": True,
                "lastTimeView": False
            },
            {
                "itemId": "389fdd42-5577-4dd6-bdb3-7f9fa0e197d4",
                "parentItemId": "d31fadcc-1caf-44ba-a373-f451e76f9c27",
                "directory": False,
                "itemName": "第一节 从法律、法规的要求看（一）",
                "resourceId": "443",
                "resourceUrl": "https://gpmp4.open.com.cn/M604/guopei_mp4/2014/gz_ts/XMTS0901/1_1_g.mp4",
                "resourceType": "VIDEO",
                "breakPoint": 0,
                "finished": True,
                "lastTimeView": False
            }
        ],
        "reportLearnTime": False,
        "selectedInRequired": False,
        "selectedInOptional": True
    },
    "time": "1744160879956"
}

# 获取资源项列表
resource_items = data['data']['resourceItemList']

# 遍历每个资源项，检查其类型是否为"VIDEO"
for item in resource_items:
    # 检查resourceType键是否存在
    if 'resourceType' in item and item['resourceType'] == 'VIDEO':
        video_url = item['resourceUrl']
        video_name = os.path.basename(video_url)

        # 下载视频文件
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(video_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {video_name}")
        else:
            print(f"Failed to download: {video_url}")

print("All videos have been processed.")



