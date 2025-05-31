import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from django.utils import timezone
import json
from .models import (
    Website,
    Webpage,
    Content,
    Image,
    DataSource,
    DataSourceContent,
)


class StaticCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.queue = [base_url]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # 初始化网站信息
        self.init_website()

    def init_website(self):
        """初始化网站信息"""
        Website.objects.get_or_create(
            domain=self.domain,
            defaults={"crawl_freq": "manual", "crawl_status": "crawling"},
        )

    def crawl(self, max_pages=10, delay=1):
        count = 0
        while self.queue and count < max_pages:
            url = self.queue.pop(0)
            if url in self.visited:
                continue

            try:
                response = self.session.get(url, timeout=10)
                if "charset=gbk" in response.text.lower():
                    response.encoding = "gbk"
                else:
                    response.encoding = response.apparent_encoding

                response.raise_for_status()
                self.visited.add(url)
                count += 1
                print(f"Crawling ({count}/{max_pages}): {url}")

                soup = BeautifulSoup(response.text, "html.parser")

                # 保存网页信息
                self.save_webpage(url)

                # 处理文本内容
                self.save_text(url, soup)

                # 处理图片
                self.process_images(url, soup)

                # 处理API数据
                self.find_api_data(url, soup)

                # 提取链接
                self.extract_links(url, soup)

                time.sleep(delay)

            except requests.RequestException as e:
                print(f"Request failed for {url}: {e}")
            except Exception as e:
                print(f"Error processing {url}: {e}")
        # 更新爬取状态
        self.update_crawl_status()

    def save_webpage(self, url):
        """保存网页信息到Webpage表"""
        website_instance,_ = Website.objects.get_or_create(domain=self.domain)
        Webpage.objects.update_or_create(
            url=url,
            defaults={"crawl_time": timezone.now(), "website": website_instance},
        )

    def save_text(self, url, soup):
        """保存文本内容到Content表"""
        text = soup.get_text(separator="\n", strip=True)

        # 确保 webapge_url 是一个 Webpage 实例
        webpage_instance,_ = Webpage.objects.get_or_create(url=url)

        Content.objects.create(text=text, webpage=webpage_instance, type="text")

    def process_images(self, url, soup):
        """处理图片信息"""
        img_tags = soup.find_all("img")
        for img in img_tags:
            img_url = urljoin(url, img.get("src"))
            if not img_url.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                continue

            alt_text = img.get("alt", "").strip()[:250]  # 限制长度符合字段要求
            width = img.get("width", "unknown")
            height = img.get("height", "unknown")
            resolution = f"{width}x{height}"[:50]

            # 保存到DataSource
            ds,_ = DataSource.objects.get_or_create(data_source_url=img_url)
            webpage_instance,_ = Webpage.objects.get_or_create(url=url)

            # 保存到Image表
            Image.objects.update_or_create(
                url=ds,
                webpage=webpage_instance,
                defaults={"description": alt_text, "resolution": resolution},
            )

    def find_api_data(self, url, soup):
        """处理API数据"""
        script_tags = soup.find_all("script", type="application/json")
        for script in script_tags:
            try:
                data = json.loads(script.string)
                data_str = json.dumps(data, ensure_ascii=False)[:65535]
                webpage_instance,_= Webpage.objects.get_or_create(url=url)
                # 保存到DataSource
                ds,_=DataSource.objects.get_or_create(data_source_url=url)
                # 保存到Content
                content = Content.objects.create(
                    text=data_str, webpage=webpage_instance, type="link"
                )

                # 保存关联关系
                DataSourceContent.objects.get_or_create(data_source=ds, content=content)

            except json.JSONDecodeError:
                pass

    def extract_links(self, url, soup):
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == self.domain and full_url not in self.visited:
                self.queue.append(full_url)

    def update_crawl_status(self):
        """更新爬取状态"""
        Website.objects.filter(domain=self.domain).update(crawl_status="complete")
