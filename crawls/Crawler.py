from urllib.parse import urlparse, urljoin
from .models import Website
from .Saver import Saver
from url_normalize import url_normalize
from .Downloader import Downloader
import logging
import time


class Crawler:
    def __init__(self, base_url):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()],
        )
        self.base_url = url_normalize(base_url)
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.queue = [self.base_url]
        self.error_occurred = False
        self.error_message = ""
        self.stats = {"pages_crawled": 0}
        self.init_website()

    def init_website(self):
        try:
            Website.objects.get_or_create(
                domain=self.domain,
                defaults={"crawl_freq": "manual", "crawl_status": "crawling"},
            )
        except Exception as e:
            self.handle_fatal_error(f"网站初始化失败: {e}")
            self.update_crawl_status("fail", self.error_message)

    def handle_fatal_error(self, message):
        self.error_occurred = True
        self.error_message = message

    def crawl(self, max_pages=10, delay=1):
        try:
            if self.error_occurred:
                print("爬取已中止：初始化阶段发生错误")
                return

            count = 0
            while self.queue and count < max_pages:
                url = self.queue.pop(0)
                if url in self.visited:
                    continue
                result = Downloader.download(url)
                if result is None:
                    print("114514")
                    logging.warning(f"跳过无法下载页面: {url}")
                    continue

                soup, url_ = result
                normalized_url = url_normalize(url_)
                if normalized_url in self.visited:
                    continue
                self.visited.add(normalized_url)

                count += 1
                self.stats["pages_crawled"] += 1
                logging.info(f"[{count}/{max_pages}] Crawling: {url}")

                try:
                    Saver.save(self.domain, normalized_url, soup)
                    self.extract_links(normalized_url, soup)
                except Exception as e:
                    logging.error(f"保存或链接提取失败: {normalized_url}: {e}")

                time.sleep(delay)
        except Exception as e:
            print(e)
        finally:
            self.update_crawl_status(
                "fail" if self.error_occurred else "complete", self.error_message
            )

    def extract_links(self, url, soup):
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == self.domain and full_url not in self.visited:
                self.queue.append(full_url)

    def update_crawl_status(self, status, error_message=None):
        try:
            website_obj = Website.objects.filter(domain=self.domain)
            if status == "fail":
                website_obj.update(crawl_status="fail", err=error_message)
            else:
                website_obj.update(crawl_status="complete")
            logging.info(f"爬取状态更新为: {status}")
        except Exception as e:
            logging.error(f"更新状态失败: {e}")
            print(f"[Crawler] 状态更新失败: {e}")
