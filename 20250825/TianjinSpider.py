# -*- coding: utf-8 -*-
"""
爬虫框架优化版本
主要改进：
1. 更清晰的代码结构和职责分离
2. 配置管理优化
3. 异常处理增强
4. 日志记录完善
5. 代码复用性提升
6. 类型注解和文档字符串
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
import time
import re
import base64
from pathlib import Path

from curl_cffi.requests import Session
from curl_cffi.requests.exceptions import HTTPError, ConnectionError, Timeout
import pandas as pd
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from lxml import etree
from loguru import logger


@dataclass
class SpiderConfig:
    """爬虫配置类，统一管理所有配置参数"""
    name: str
    website: str
    base_url: str
    start_time: str = "2025-06-01"
    end_time: str = "2025-08-20"
    keywords: List[str] = field(default_factory=lambda: ["马路", "公路", "道路"])
    title_filters: List[str] = field(default_factory=lambda: ["结果", "中标"])
    content_filters: List[str] = field(default_factory=lambda: ["开标记录"])
    max_retries: int = 3
    request_delay: float = 1.0
    headers: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
    })


@dataclass
class SpiderItem:
    """爬虫数据项，标准化数据结构"""
    title: str
    date: str
    origin: str
    content: str
    link: str
    website: str

    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            "标题": self.title,
            "时间": self.date,
            "来源": self.origin,
            "正文": self.content,
            "链接": self.link,
            "所在网站": self.website
        }


class RequestManager:
    """请求管理器，统一处理HTTP请求"""

    def __init__(self, config: SpiderConfig):
        self.config = config
        self.session = Session()
        self.logger = logger

    def request(self, method: str, url: str, **kwargs) -> Union[Dict, str, bytes]:
        """
        统一的请求方法，包含重试机制和异常处理

        Args:
            method: 请求方法 (GET/POST)
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            响应数据

        Raises:
            ValueError: 不支持的请求方法
            Exception: 请求失败
        """
        method = method.upper()
        if method not in ["GET", "POST"]:
            raise ValueError(f"不支持的请求方法: {method}")

        # 合并默认headers
        headers = {**self.config.headers, **kwargs.get('headers', {})}
        kwargs['headers'] = headers
        kwargs.setdefault('verify', False)

        fetch_func = getattr(self.session, method.lower())

        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"请求 {method} {url} (尝试 {attempt + 1}/{self.config.max_retries})")
                resp = fetch_func(url, **kwargs)
                resp.raise_for_status()

                # 尝试解析JSON
                try:
                    return resp.json()
                except ValueError:
                    # JSON解析失败，根据Content-Type返回相应格式
                    content_type = resp.headers.get('Content-Type', '').lower()
                    if content_type.startswith(('text/', 'application/json', 'application/javascript')):
                        return resp.text
                    else:
                        return resp.content

            except (HTTPError, ConnectionError, Timeout) as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"请求最终失败: {url}, 错误: {e}")
                time.sleep(1)  # 重试前等待
            except Exception as e:
                self.logger.error(f"请求异常: {e}")
                raise

    def get(self, url: str, **kwargs) -> Union[Dict, str, bytes]:
        """GET请求"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Union[Dict, str, bytes]:
        """POST请求"""
        return self.request("POST", url, **kwargs)


class DataProcessor:
    """数据处理器，处理HTML解析和文本提取"""

    @staticmethod
    def element_to_text(content_element: etree._Element) -> str:
        """
        提取HTML元素中的文本并保留换行结构

        Args:
            content_element: lxml解析后的HTML元素

        Returns:
            保留换行的纯文本
        """
        # 为需要换行的标签添加换行符
        for tag in content_element.xpath('.//p | .//br | .//tr | .//li | .//h1 | .//h2 | .//h3'):
            if tag.tag == "br":
                # br标签直接替换为换行符
                br_newline = etree.Element("text")
                br_newline.text = "\n"
                tag.addprevious(br_newline)
                tag.getparent().remove(tag)
            else:
                # 其他标签前后添加换行符
                prev_elem = tag.getprevious()
                if prev_elem is None or prev_elem.tag != "text":
                    pre_newline = etree.Element("text")
                    pre_newline.text = "\n"
                    tag.addprevious(pre_newline)

                next_elem = tag.getnext()
                if next_elem is None or next_elem.tag != "text":
                    post_newline = etree.Element("text")
                    post_newline.text = "\n"
                    tag.addnext(post_newline)

        # 提取文本
        text = etree.tostring(content_element, method="text", encoding="utf8").decode("utf8")

        # 清理多余空行
        text = re.sub(r'\n+', '\n', text)  # 多换行→单换行
        text = re.sub(r'\n\s+', '\n', text)  # 换行后多空格→仅换行
        text = text.strip()  # 去除首尾空行

        return text


class DataStorage:
    """数据存储器，负责数据的保存和管理"""

    def __init__(self):
        self.items: List[SpiderItem] = []
        self.logger = logger

    def add_item(self, item: SpiderItem) -> None:
        """添加数据项"""
        self.items.append(item)
        self.logger.debug(f"添加数据项: {item.title}")

    def save_to_excel(self, filename: Optional[str] = None) -> None:
        """
        保存数据到Excel文件

        Args:
            filename: 文件名，如果为None则使用时间戳命名
        """
        if not self.items:
            self.logger.warning("没有数据需要保存")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spider_data_{timestamp}.xlsx"

        # 转换为DataFrame
        data = [item.to_dict() for item in self.items]
        df = pd.DataFrame(data)

        # 保存到Excel
        df.to_excel(filename, index=False)
        self.logger.info(f"数据已保存到: {filename}, 共 {len(self.items)} 条记录")

    def get_data_count(self) -> int:
        """获取数据条数"""
        return len(self.items)


class BaseSpider(ABC):
    """爬虫基类，定义通用接口和功能"""

    def __init__(self, config: SpiderConfig):
        self.config = config
        self.request_manager = RequestManager(config)
        self.data_processor = DataProcessor()
        self.storage = DataStorage()
        self.logger = logger

        # 分页相关
        self.current_page = 1
        self.total_pages = 0
        self.has_next_page = True

    def should_filter_title(self, title: str) -> bool:
        """
        检查标题是否应该被过滤

        Args:
            title: 标题文本

        Returns:
            True表示应该过滤，False表示不过滤
        """
        for filter_word in self.config.title_filters:
            if filter_word in title:
                self.logger.info(f"标题被过滤: {title} (包含关键词: {filter_word})")
                return True
        return False

    def should_filter_content(self, content: str) -> bool:
        """
        检查内容是否应该被过滤

        Args:
            content: 内容文本

        Returns:
            True表示应该过滤，False表示不过滤
        """
        for filter_word in self.config.content_filters:
            if filter_word in content:
                self.logger.info(f"内容被过滤 (包含关键词: {filter_word})")
                return True
        return False

    @abstractmethod
    def parse_list_page(self, response: Union[str, Dict]) -> List[str]:
        """
        解析列表页，提取详情页链接

        Args:
            response: 列表页响应内容

        Returns:
            详情页链接列表
        """
        pass

    @abstractmethod
    def parse_detail_page(self, response: Union[str, Dict], url: str) -> Optional[SpiderItem]:
        """
        解析详情页，提取具体数据

        Args:
            response: 详情页响应内容
            url: 详情页URL

        Returns:
            解析后的数据项，如果解析失败返回None
        """
        pass

    @abstractmethod
    def build_search_url(self, keyword: str, page: int, **kwargs) -> str:
        """
        构建搜索URL

        Args:
            keyword: 搜索关键词
            page: 页码
            **kwargs: 其他参数

        Returns:
            搜索URL
        """
        pass

    def run(self) -> None:
        """
        执行爬虫主流程
        """
        self.logger.info(f"开始执行爬虫: {self.config.name}")
        start_time = time.time()

        try:
            for keyword in self.config.keywords:
                self.logger.info(f"开始搜索关键词: {keyword}")
                self._crawl_keyword(keyword)

            # 保存数据
            self.storage.save_to_excel()

            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"爬虫执行完成，耗时: {duration:.2f}秒，共获取 {self.storage.get_data_count()} 条数据")

        except Exception as e:
            self.logger.error(f"爬虫执行失败: {e}")
            raise

    def _crawl_keyword(self, keyword: str) -> None:
        """
        爬取指定关键词的数据

        Args:
            keyword: 搜索关键词
        """
        self.current_page = 1
        self.has_next_page = True

        while self.has_next_page:
            try:
                self.logger.info(f"爬取关键词 '{keyword}' 第 {self.current_page} 页")

                # 构建搜索URL并请求
                search_url = self.build_search_url(keyword, self.current_page)
                response = self.request_manager.get(search_url)

                # 解析列表页
                detail_urls = self.parse_list_page(response)

                if not detail_urls:
                    self.logger.info(f"第 {self.current_page} 页没有数据")
                    self.has_next_page = False
                    continue

                # 爬取详情页
                for detail_url in detail_urls:
                    try:
                        detail_response = self.request_manager.get(detail_url)
                        item = self.parse_detail_page(detail_response, detail_url)

                        if item and not self.should_filter_title(item.title) and not self.should_filter_content(
                                item.content):
                            self.storage.add_item(item)
                            self.logger.info(f"成功获取数据: {item.title}")

                        # 请求间隔
                        if self.config.request_delay > 0:
                            time.sleep(self.config.request_delay)

                    except Exception as e:
                        self.logger.error(f"处理详情页失败 {detail_url}: {e}")
                        continue

                # 检查是否有下一页
                self._check_next_page()

            except Exception as e:
                self.logger.error(f"处理第 {self.current_page} 页失败: {e}")
                self.has_next_page = False

    def _check_next_page(self) -> None:
        """
        检查是否有下一页，子类可以重写此方法
        """
        if self.total_pages > 0 and self.current_page >= self.total_pages:
            self.has_next_page = False
        else:
            self.current_page += 1


class TianjinSpider(BaseSpider):
    """天津市公共资源交易网爬虫实现"""

    def __init__(self):
        config = SpiderConfig(
            name="天津市公共资源交易网",
            website="ggzy.zwfwb.tj.gov.cn",
            base_url="http://ggzy.zwfwb.tj.gov.cn"
        )
        super().__init__(config)

        # 天津网站特有配置
        self.search_api_template = "http://ggzy.zwfwb.tj.gov.cn/queryContent_{}-jyxx.jspx"
        self.channel_ids = {
            "政府采购权": "76",
            "工程建设": "75",
            "土地使用权": "237",
            "国有产权": "78",
            "农村产权": "255",
            "矿业权交易": "247",
            "二类疫苗": "303",
            "药品采购": "240",
            "碳排放权": "308",
            "排污权": "311",
            "林权交易": "266",
            "知识产权": "314",
            "用水权": "368",
            "其他": "243",
        }
        self.current_channel_id = "76"  # 默认使用政府采购权

    def build_search_url(self, keyword: str, page: int, **kwargs) -> str:
        """
        构建天津网站的搜索URL
        """
        return self.search_api_template.format(page)

    def parse_list_page(self, response: str) -> List[str]:
        """
        解析天津网站的列表页
        """
        urls = []
        try:
            sele = etree.HTML(response)

            # 获取总页数
            page_data = sele.xpath(".//div[@class='page-list']/ul/li[1]/a/text()")
            if page_data:
                self.total_pages = int(re.findall("/([0-9]+?)页", page_data[0])[0].strip())

            # 提取链接
            div_eles = sele.xpath(".//div[@class='article-list3-t']")
            for div in div_eles:
                title_ele = div.xpath("./a")[0]
                encrypted_url = div.xpath("./a/@url")[0]

                title = etree.tostring(title_ele, method="text", encoding="utf8").decode("utf8")

                # 标题过滤
                if not self.should_filter_title(title):
                    url = self._encrypt_url(encrypted_url)
                    urls.append(url)

        except Exception as e:
            self.logger.error(f"解析列表页失败: {e}")

        return urls

    def parse_detail_page(self, response: str, url: str) -> Optional[SpiderItem]:
        """
        解析天津网站的详情页
        """
        try:
            sele = etree.HTML(response)
            content_ele = sele.xpath(".//div[@id='content']")[1]

            # 提取标题、时间、来源
            title = content_ele.xpath("./table/tbody/tr/td/div/p[1]/font/b/text()")[0]
            time_origin = content_ele.xpath("./table/tbody/tr/td/div/p[2]/font/text()")[0]
            release_time, origin = time_origin.split("    ")
            release_time = release_time.strip("发布日期：")
            origin = origin.strip("发布来源：")

            # 删除标题和时间来源元素
            elements_to_remove = content_ele.xpath("./table/tbody/tr/td/div/p[position()>0 and position()<3]")
            for element in elements_to_remove:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)

            # 提取正文
            text_ele = content_ele.xpath("./table/tbody/tr/td/div")[0]
            text = self.data_processor.element_to_text(text_ele)

            return SpiderItem(
                title=title,
                date=release_time,
                origin=origin,
                content=text,
                link=url,
                website=self.config.name
            )

        except Exception as e:
            self.logger.error(f"解析详情页失败 {url}: {e}")
            return None

    def _encrypt_url(self, url: str) -> str:
        """
        天津网站URL加密逻辑

        Args:
            url: 原始URL

        Returns:
            加密后的URL
        """
        try:
            u_id = url.rstrip("/").split("/")[-1].replace(".jhtml", "")
            plaintext = u_id.encode()
            key = "qnbyzzwmdgghmcnm".encode()

            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
            new_id = base64.b64encode(ciphertext).decode().strip("==").replace("/", "^")

            new_url = re.sub(r"/(\w+?)\.jhtml", lambda m: f"/{new_id}.jhtml", url)
            return new_url

        except Exception as e:
            self.logger.error(f"URL加密失败: {e}")
            return url

    def run(self) -> None:
        """
        重写运行方法，支持多渠道爬取
        """
        self.logger.info(f"开始执行爬虫: {self.config.name}")
        start_time = time.time()

        try:
            # 遍历所有渠道
            for channel_name, channel_id in self.channel_ids.items():
                self.logger.info(f"开始爬取渠道: {channel_name} (ID: {channel_id})")
                self.current_channel_id = channel_id

                # 遍历所有关键词
                for keyword in self.config.keywords:
                    self.logger.info(f"在渠道 '{channel_name}' 中搜索关键词: {keyword}")
                    self._crawl_keyword_with_channel(keyword, channel_id)

            # 保存数据
            self.storage.save_to_excel()

            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"爬虫执行完成，耗时: {duration:.2f}秒，共获取 {self.storage.get_data_count()} 条数据")

        except Exception as e:
            self.logger.error(f"爬虫执行失败: {e}")
            raise

    def _crawl_keyword_with_channel(self, keyword: str, channel_id: str) -> None:
        """
        在指定渠道中爬取关键词数据

        Args:
            keyword: 搜索关键词
            channel_id: 渠道ID
        """
        self.current_page = 1
        self.has_next_page = True

        while self.has_next_page:
            try:
                self.logger.info(f"爬取关键词 '{keyword}' 渠道 '{channel_id}' 第 {self.current_page} 页")

                # 构建请求参数
                params = {
                    "title": keyword,
                    "inDates": "",
                    "ext": "",
                    "ext1": "",
                    "origin": "",
                    "channelId": channel_id,
                    "beginTime": self.config.start_time,
                    "endTime": self.config.end_time
                }

                # 请求列表页
                search_url = self.build_search_url(keyword, self.current_page)
                response = self.request_manager.get(search_url, params=params)

                # 解析列表页
                detail_urls = self.parse_list_page(response)

                if not detail_urls:
                    self.logger.info(f"第 {self.current_page} 页没有数据")
                    self.has_next_page = False
                    continue

                # 爬取详情页
                for detail_url in detail_urls:
                    try:
                        detail_response = self.request_manager.get(detail_url)
                        item = self.parse_detail_page(detail_response, detail_url)

                        if item and not self.should_filter_content(item.content):
                            self.storage.add_item(item)
                            self.logger.info(f"成功获取数据: {item.title}")

                        # 请求间隔
                        if self.config.request_delay > 0:
                            time.sleep(self.config.request_delay)

                    except Exception as e:
                        self.logger.error(f"处理详情页失败 {detail_url}: {e}")
                        continue

                # 检查是否有下一页
                self._check_next_page()

            except Exception as e:
                self.logger.error(f"处理第 {self.current_page} 页失败: {e}")
                self.has_next_page = False


if __name__ == "__main__":
    # 使用示例
    spider = TianjinSpider()
    spider.run()