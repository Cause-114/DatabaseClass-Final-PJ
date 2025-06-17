import re
import json
import logging
import jieba.analyse
from urllib.parse import urljoin
from django.utils import timezone
from url_normalize import url_normalize
from .models import Website, Webpage, Content, Image, DataSource
from dateutil import parser
from .Downloader import Downloader


class Saver:
    @classmethod
    def save(cls, id, url, soup):
        cls.save_webpage(id, url)
        cls.save_text(url, soup)
        cls.process_images(url, soup)


    @staticmethod
    def save_webpage(id, url):
        website_obj, _ = Website.objects.get_or_create(id=id)
        Webpage.objects.update_or_create(
            url=url,
            defaults={"crawl_time": timezone.now(), "website": website_obj},
        )

    @staticmethod
    def save_text(url, soup):
        try:
            for element in soup(
                ["nav", "header", "footer", "aside", "script", "style"]
            ):
                element.decompose()

            main_content = None
            for selector in [
                "#main",
                "#content",
                ".main-content",
                ".article",
                ".content",
                "main",
            ]:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            text_source = main_content if main_content else soup
            text = re.sub(
                r"\n\s*\n", "\n\n", text_source.get_text(separator="\n", strip=True)
            )

            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            paragraph_keywords = []
            for para in paragraphs:
                if para:
                    # 提取每段top1关键词
                    keywords = jieba.analyse.extract_tags(para, topK=5)
                    if keywords:
                        for k in keywords:
                            paragraph_keywords.append(k)

            # 合并所有关键词
            keywords_str = ",".join(set(paragraph_keywords))  # 去重处理

            webpage_qs = Webpage.objects.filter(url=url)
            if webpage_qs.exists():
                Content.objects.update_or_create(
                    webpage=webpage_qs.first(),
                    defaults={
                        "keywords": keywords_str,
                        "type": "text",
                        "text": "\n\n".join(paragraphs),
                    },
                )
            ds, _ = DataSource.objects.get_or_create(data_source_url=url)
            Saver.process_data_source(url,soup)
        except Exception as e:
            logging.error(f"保存文本失败 {url}: {e}")

        

    @staticmethod
    def process_images(url, soup):
        try:
            img_tags = soup.find_all("img")
            webpage, _ = Webpage.objects.get_or_create(url=url)
            if not webpage:
                return
            for img in img_tags:
                img_url = url_normalize(urljoin(url, img.get("src")))
                if not img_url.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    continue
                alt = img.get("alt", "").strip()[:250]
                width = img.get("width", "unknown")
                height = img.get("height", "unknown")
                resolution = f"{width}x{height}"[:50]
                ol=logging.root.level
                logging.root.setLevel(logging.ERROR)
                try:
                    result=Downloader.download(img_url)
                finally:
                    logging.root.setLevel(ol)
                if result is None:
                    continue
                img_soup,_ = result
                ds, _ = DataSource.objects.get_or_create(data_source_url=img_url)
                Saver.process_data_source(img_url,img_soup)
                Image.objects.update_or_create(
                    url=ds,
                    defaults={
                        "webpage": webpage,
                        "description": alt,
                        "resolution": resolution,
                    },
                )
        except Exception as e:
            logging.error(f"处理图片失败 {url}: {e}")
   
    @staticmethod
    def process_data_source(url, soup):
        try:
            #webpage_instance, _ = Webpage.objects.get_or_create(url=url)
            # 1. 提取数据源基本信息
            ds, _ = DataSource.objects.get_or_create(data_source_url=url)
            
            # 2. 提取发布者和发布时间
            publisher, publish_time = Saver.extract_metadata(soup)
            
            # 3. 更新数据源元数据
            if publisher or publish_time:

                
                # 仅更新有变化的字段
                if not ds.publisher and publisher:
                    ds.publisher = publisher
                if not ds.publish_time and publish_time:
                    ds.publish_time = publish_time
                ds.save()
            
            return ds
            
        except Exception as e:
            logging.error(f"提取数据源信息失败 {url}: {e}")
            return None

    @staticmethod
    def extract_metadata(soup):
        """
        从soup中提取发布者和发布时间
        """
        publisher = None
        publish_time = None
        
        # 提取发布者
        publisher_tags = [
            soup.find('meta', attrs={'property': 'og:site_name'}),
            soup.find('meta', attrs={'name': 'author'}),
            soup.find('meta', attrs={'name': 'publisher'}),
            soup.find('meta', attrs={'property': 'article:publisher'})
        ]
        
        for tag in publisher_tags:
            if tag and tag.get('content'):
                publisher = tag['content'].strip()[:100]
                break
        
        # 提取发布时间
        time_tags = [
            soup.find('meta', attrs={'property': 'article:published_time'}),
            soup.find('meta', attrs={'property': 'article:modified_time'}),
            soup.find('meta', attrs={'name': 'pubdate'}),
            soup.find('time', attrs={'datetime': True}),
            soup.find('meta', attrs={'itemprop': 'datePublished'})
        ]
        
        for tag in time_tags:
            if tag:
                time_str = tag.get('content') or tag.get('datetime')
                if time_str:
                    try:
                        publish_time = parser.parse(time_str)
                        break
                    except (ValueError, TypeError):
                        continue
        
        return publisher, publish_time