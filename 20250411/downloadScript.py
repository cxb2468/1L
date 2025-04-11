import json
import os
import re
import requests
from uuid import UUID


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', filename).strip()


# 从文件读取JSON数据
with open('mp4json.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


print(data['data']['name'])
course_name = sanitize_filename(data['data']['name'])
save_dir = os.path.join(os.getcwd(), course_name)
os.makedirs(save_dir, exist_ok=True)

# 构建目录结构映射表
dir_structure = {}
for item in data['data']['resourceItemList']:
    item_id = item['itemId']
    if item['directory']:
        dir_structure[item_id] = {
            'name': sanitize_filename(item['itemName']),
            'parent': item['parentItemId']
        }


def get_full_path(item_id, path=[]):
    if str(item_id) == '00000000-0000-0000-0000-000000000000':
        return []
    node = dir_structure.get(item_id, {})
    if node.get('parent'):
        return get_full_path(node['parent']) + [node['name']]
    return [node['name']]


headers = {'User-Agent': 'Mozilla/5.0'}

for item in data['data']['resourceItemList']:
    if item.get('resourceType') == 'VIDEO':
        parent_id = item['parentItemId']
        path_components = get_full_path(parent_id)

        final_dir = os.path.join(save_dir, *path_components)
        os.makedirs(final_dir, exist_ok=True)

        video_name = sanitize_filename(item['itemName']) + '.mp4'
        file_path = os.path.join(final_dir, video_name)

        if os.path.exists(file_path):
            print(f'Skipped: {file_path}')
            continue

        print(f'Downloading: {file_path}')
        try:
            with requests.get(item['resourceUrl'], headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f'Success: {file_path}')
        except Exception as e:
            print(f'Failed: {file_path}, Error: {str(e)}')
            if os.path.exists(file_path):
                os.remove(file_path)

print('All downloads completed!')