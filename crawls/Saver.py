import re
import json
import logging
import jieba.analyse
from urllib.parse import urljoin
from django.utils import timezone
from url_normalize import url_normalize
from .models import Website, Webpage, Content, Image, DataSource, DataSourceContent


class Saver:
    @classmethod
    def save(cls, domain, url, soup):
        cls.save_webpage(domain, url)
        cls.save_text(url, soup)
        cls.process_images(url, soup)
        cls.find_api_data(url, soup)

    @staticmethod
    def save_webpage(domain, url):
        website_obj, _ = Website.objects.get_or_create(domain=domain)
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
                    keywords = jieba.analyse.extract_tags(para, topK=1)
                    if keywords:
                        paragraph_keywords.append(keywords[0])
            
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
                ds, _ = DataSource.objects.get_or_create(data_source_url=img_url)
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
    def find_api_data(url, soup):
        try:
            script_tags = soup.find_all("script", type="application/json")
            webpage_instance, _ = Webpage.objects.get_or_create(url=url)
            for script in script_tags:
                print(114514)
                try:
                    data = json.loads(script.string)
                    data_str = json.dumps(data, ensure_ascii=False)[:65535]
                    # 保存到DataSource
                    ds, _ = DataSource.objects.get_or_create(data_source_url=url)
                    # 保存到Content
                    content = Content.objects.create(
                        text=data_str, webpage=webpage_instance, type="link"
                    )
                    # 保存关联关系
                    DataSourceContent.objects.get_or_create(
                        data_source=ds, content=content
                    )
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logging.error(f"API数据提取失败 {url}: {e}")
