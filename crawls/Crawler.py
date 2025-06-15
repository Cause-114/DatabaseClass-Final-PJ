from .models import Website, CrawlTask
from .Downloader import Downloader
from .Saver import Saver
from django.utils import timezone
from urllib.parse import urlparse, urljoin
from url_normalize import url_normalize
import logging


class Crawler:
    def __init__(self, base_url, task_id=None):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()],
        )
        self.base_url = url_normalize(base_url)
        self.domain = urlparse(base_url).netloc
        self.visited = set()
        self.queue = [self.base_url]
        self.task = CrawlTask.objects.get(id=task_id) if task_id else None
        self.website = (
            Website.objects.get_or_create(domain=self.domain, user=self.task.user)[0]
            if self.task and self.task.user
            else None
        )
        self.error_occurred = False
        self.error_message = ""
        if self.task:
            self.task.start_time = timezone.now()
            self.task.save()
    def handle_fatal_error(self, error_msg):
        self.error_occurred = True
        self.error_message = error_msg
        logging.error(f"致命错误：{error_msg}")
        if self.task:
            self.task.status = "fail"
            self.task.error_msg = error_msg
            self.task.end_time = timezone.now()
            self.task.save()

    def crawl(self, max_pages=10, TimeOut=1):
        try:
            if self.error_occurred:
                print("爬取已中止：初始化阶段发生错误")
                return
            count = 0
            while self.queue and count < max_pages:
                url = self.queue.pop(0)
                if url in self.visited:
                    continue
                result = Downloader.download(url=url, timeout=TimeOut)
                if result is None:
                    logging.warning(f"跳过无法下载页面: {url}")
                    continue

                soup, url_ = result
                normalized_url = url_normalize(url_)
                if normalized_url in self.visited:
                    continue
                self.visited.add(normalized_url)

                count += 1
                logging.info(f"[{count}/{max_pages}] Crawling: {url}")
                Saver.save(self.domain, normalized_url, soup)
                if count == 1:
                    self.extract_website_info(soup)  # 抽取站点信息
                # if(len(self.queue)<max_pages-count):
                #     print(len(self.queue),count)
                self.extract_links(normalized_url, soup)
            print(len(self.queue))
        except Exception as e:
            self.handle_fatal_error(str(e))
        finally:
            self.finish_task()

    def extract_website_info(self, soup):
        try:
            title = soup.title.string.strip() if soup.title else ""
            desc_tag = soup.find("meta", attrs={"name": "description"})
            description = (
                desc_tag["content"].strip()
                if desc_tag and "content" in desc_tag.attrs
                else ""
            )

            self.website.title = title
            self.website.description = description
            self.website.homepage = self.base_url
            self.website.save()
        except Exception as e:
            logging.warning(f"提取网站信息失败: {e}")

    def extract_links(self, url, soup):
        links = soup.find_all("a", href=True)
        for link in links:
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == self.domain and full_url not in self.visited:
                self.queue.append(full_url)

    def finish_task(self):
        status = "fail" if self.error_occurred else "complete"
        if self.task:
            self.task.status = status
            self.task.end_time = timezone.now()
            if self.error_occurred:
                self.task.error_msg = self.error_message
            self.task.save()
        logging.info(f"任务完成: {status}")
