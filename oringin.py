# 这是最初前面写的PJ.py的代码
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import pymysql

config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Windows1",  # 输入密码
    "database": "samp_db",  # 输入数据库名称
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


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

        # 初始化数据库连接
        self.connection = pymysql.connect(**config)
        self.cursor = self.connection.cursor()

        # 初始化网站信息
        self.init_website()

    def init_website(self):
        """初始化网站信息"""
        insert_website = """
        INSERT IGNORE INTO Website (domain, crawl_freq, crawl_status)
        VALUES (%s, 'manual', 'crawling')
        """
        self.cursor.execute(insert_website, (self.domain,))
        self.connection.commit()

    def crawl(self, max_pages=10, delay=1):
        try:
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
        finally:
            # 更新爬取状态并关闭连接
            self.update_crawl_status()
            self.cursor.close()
            self.connection.close()

    def save_webpage(self, url):
        """保存网页信息到Webpage表"""
        insert_webpage = """
        INSERT INTO Webpage (url, crawl_time, website_domain)
        VALUES (%s, NOW(), %s)
        ON DUPLICATE KEY UPDATE crawl_time = NOW()
        """
        self.cursor.execute(insert_webpage, (url, self.domain))
        self.connection.commit()

    def save_text(self, url, soup):
        """保存文本内容到Content表"""
        # 初始版本
        text = soup.get_text(separator="\n", strip=True)
        insert_content = """
        INSERT INTO Content (text, webpage_url, type)
        VALUES (%s, %s, 'text')
        """
        self.cursor.execute(insert_content, (text, url))
        self.connection.commit()

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
            insert_data_source = """
            INSERT IGNORE INTO DataSource (data_source_url)
            VALUES (%s)
            """
            self.cursor.execute(insert_data_source, (img_url,))

            # 保存到Image表
            insert_image = """
            INSERT INTO Image (image_url, webpage_url, description, resolution)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                webpage_url = VALUES(webpage_url),
                description = VALUES(description),
                resolution = VALUES(resolution)
            """
            self.cursor.execute(insert_image, (img_url, url, alt_text, resolution))
            self.connection.commit()

    def find_api_data(self, url, soup):
        """处理API数据"""
        script_tags = soup.find_all("script", type="application/json")
        for script in script_tags:
            try:
                data = json.loads(script.string)
                data_str = json.dumps(data, ensure_ascii=False)[
                    :65535
                ]  # 限制长度符合TEXT字段

                # 保存到DataSource
                insert_data_source = """
                INSERT IGNORE INTO DataSource (data_source_url)
                VALUES (%s)
                """
                self.cursor.execute(insert_data_source, (url,))

                # 保存到Content
                insert_content = """
                INSERT INTO Content (text, webpage_url, type)
                VALUES (%s, %s, 'link')
                """
                self.cursor.execute(insert_content, (data_str, url))
                content_id = self.cursor.lastrowid

                # 保存关联关系
                insert_relation = """
                INSERT IGNORE INTO DataSource_Content (url, content_id)
                VALUES (%s, %s)
                """
                self.cursor.execute(insert_relation, (url, content_id))
                self.connection.commit()
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
        update_status = """
        UPDATE Website 
        SET crawl_status = 'complete' 
        WHERE domain = %s
        """
        self.cursor.execute(update_status, (self.domain,))
        self.connection.commit()


if __name__ == "__main__":
    crawler = StaticCrawler("https://jwc.fudan.edu.cn/")
    crawler.crawl(max_pages=35, delay=2)
