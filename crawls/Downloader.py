import requests
from bs4 import BeautifulSoup


class Downloader:
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    @classmethod
    def download(cls, url, headers=None, timeout=10):
        final_headers = headers or cls.DEFAULT_HEADERS
        try:
            response = requests.get(url, headers=final_headers, timeout=timeout)
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            encoding = cls.detect_encoding(response.content, response.headers)

            # 关键点：直接传 content 和 from_encoding 给 BeautifulSoup
            soup = BeautifulSoup(
                response.content, "html.parser", from_encoding=encoding
            )
            return (soup, response.url)

        except Exception as e:
            print(f"[Downloader] Failed to download {url}: {e}")
            return None

    @staticmethod
    def detect_encoding(content, response_headers=None):
        """检测内容的编码"""
        encoding = None

        # 1. 检查HTTP响应头中的编码声明
        if response_headers:
            content_type = response_headers.get("Content-Type", "").lower()
            if "charset=" in content_type:
                encoding = content_type.split("charset=")[-1].split(";")[0].strip()

        # 2. 检查HTML meta标签中的编码声明
        if not encoding:
            try:
                # 使用BeautifulSoup查找meta标签
                soup = BeautifulSoup(content[:4096], "html.parser")  # 只分析前4KB
                meta_tag = soup.find("meta", attrs={"charset": True})
                if meta_tag:
                    encoding = meta_tag["charset"]
                else:
                    # 查找http-equiv的meta标签
                    meta_tag = soup.find("meta", attrs={"http-equiv": "Content-Type"})
                    if meta_tag and "content" in meta_tag.attrs:
                        content_meta = meta_tag["content"].lower()
                        if "charset=" in content_meta:
                            encoding = (
                                content_meta.split("charset=")[-1].split(";")[0].strip()
                            )
            except Exception:
                pass
        return encoding
