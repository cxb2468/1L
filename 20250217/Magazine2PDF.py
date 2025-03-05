import os
import re
import requests
from PIL import Image
from fpdf import FPDF
from io import BytesIO
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class Qikan:

    default_img_start = [
        [[0,0],[468,0],[936,0],[1404,0]],
        [[0,468],[468,468],[936,468],[1404,468]],
        [[0,936],[468,936],[936,936],[1404,936]],
        [[0,1404],[468,1404],[936,1404],[1404,1404]],
        [[0,1872],[468,1872],[936,1872],[1404,1872]],
    ]

    default_img_total_size = {'width':1597, 'height':2255}

    web_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def http_get(self, url, headers=None):
        try:
            response = self.session.get(url, headers=headers or self.web_headers, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"HTTP GET error: {e}")
            return None

    def download_image(self, url, destination):
        content = self.http_get(url)
        if content:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(content)
            return destination
        return None

    def get_magazine_issue(self, url):
        content = self.http_get(url)
        if not content:
            return None

        variables_to_match = ['guid', 'year', 'issue', 'codename', 'pagecount']
        result = {}

        # 提取JavaScript变量
        pattern = re.compile(r'var\s+([^=]+)\s*=\s*"([^"]+)"\s*;')
        matches = pattern.findall(content.decode('utf-8'))
        for var_name, var_value in matches:
            var_name = var_name.strip()
            if var_name in variables_to_match:
                result[var_name] = var_value.strip()

        # 提取标题
        title_match = re.search(r'<p class="maga-tc-title">(.*?)</p>', content.decode('utf-8'))
        if title_match:
            result['title'] = title_match.group(1)

        return result

    def download_image_list(self, info):
        path_temp = f"./{info['year']}_{info['issue']}_{info['codename']}"
        os.makedirs(path_temp, exist_ok=True)

        for page in range(1, int(info['pagecount']) + 1):
            print(f"\r正在下载第 {page} 页  ", end="")
            url = f"http://www.qikan.com.cn/FReader/h5/handle/originalapi.ashx?year={info['year']}&issue={info['issue']}&codename={info['codename']}&page={page}&types=getbigimages"
            content = self.http_get(url)
            if content:
                img_list = content.decode('utf-8')
                # 这里需要根据实际返回格式解析图片列表
                # 假设返回的是JSON数组
                import json
                img_urls = json.loads(img_list)
                for img_url in img_urls:
                    filename = os.path.basename(img_url.split('?')[0])
                    self.download_image(img_url, os.path.join(path_temp, filename))

                self.splicing_img(path_temp, page)
                print(f"\r已下载完成 {page} 页  ", end="")

    def splicing_img(self, path, page):
        page_t = str(page).zfill(4)
        merged_image = Image.new('RGB', (self.default_img_total_size['width'], self.default_img_total_size['height']))

        for row in range(5):
            row_t = str(row).zfill(4)
            for col in range(4):
                col_t = str(col).zfill(4)
                img_path = os.path.join(path, f"{page_t}_{row_t}_{col_t}.jpg")
                try:
                    img = Image.open(img_path)
                    x, y = self.default_img_start[row][col]
                    width, height = img.size
                    merged_image.paste(img, (x, y, x + width, y + height))
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")

        output_path = os.path.join(path, f"{page_t}.jpg")
        merged_image.save(output_path)

    def create_pdf(self, path, page_all, name=None):
        pdf = FPDF()
        pdf.set_auto_page_break(0)

        # 获取第一张图片的实际尺寸
        first_page = str(1).zfill(4)
        first_img_path = os.path.join(path, f"{first_page}.jpg")

        try:
            with Image.open(first_img_path) as img:
                original_width, original_height = img.size
        except Exception as e:
            print(f"❌ 读取首图尺寸失败: {str(e)}")
            return

        # 计算适合A4的缩放比例（宽度适配210mm）
        a4_width_mm = 210  # A4纸宽度
        mm_per_pixel = a4_width_mm / original_width  # 每像素对应的毫米数
        page_width = a4_width_mm
        page_height = original_height * mm_per_pixel  # 保持宽高比

        # 设置页面尺寸（关键修正点）✅
        page_size = (page_width, page_height)
        pdf = FPDF(unit="mm", format=page_size)

        for page in range(1, page_all + 1):
            page_t = str(page).zfill(4)
            img_path = os.path.join(path, f"{page_t}.jpg")

            # 兼容旧版 fpdf（< 1.7）
            pdf.add_page()  # 无需再传参数

            try:
                pdf.image(img_path, 0, 0, page_width, page_height)
            except Exception as e:
                print(f"添加图片失败 {img_path}: {str(e)}")
                continue

        output_path = f"./{name}.pdf" if name else f"{path}.pdf"
        pdf.output(output_path)
        print(f"\n文件被保存在：{output_path}")

    # 新增辅助方法获取图片物理尺寸（毫米）
    def _get_physical_size(self, img_path):
        try:
            with Image.open(img_path) as img:
                # 获取DPI信息（默认为72）
                dpi = img.info.get('dpi', (72, 72))
                width_inch = img.width / dpi[0]
                height_inch = img.height / dpi[1]
                return (width_inch * 25.4, height_inch * 25.4)  # 英寸转毫米
        except Exception as e:
            print(f"⚠️ 获取物理尺寸失败：{str(e)}")
            return None
    def download_magazine(self, url):
        url = url.replace('/magdetails/', '/original/').replace('/m/', '/')
        info = self.get_magazine_issue(url)
        if not info:
            print("\n解析失败")
            return

        print(f"\n杂志名称：{info.get('title', '')}")
        print(f"页码总数：{info.get('pagecount', 0)}\n")

        self.download_image_list(info)
        self.create_pdf(
            path=f"./{info['year']}_{info['issue']}_{info['codename']}",
            page_all=int(info['pagecount']),
            name=info.get('title', None)
        )

if __name__ == "__main__":
    qikan = Qikan()
    url = input("请输入杂志url: ")
    qikan.download_magazine(url)
