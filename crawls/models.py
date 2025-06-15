from django.db import models
from django.contrib.auth.models import User  # 加入导入


# 网站模型
class Website(models.Model):
    id = models.AutoField(primary_key=True)  # 可省略，Django 默认就是这个
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="websites"
    )  # 用户归属
    domain = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)  # 网站标题
    description = models.TextField(null=True, blank=True)  # 网站描述
    homepage = models.URLField(null=True, blank=True)  # 首页地址

    class Meta:
        unique_together = ("user", "domain")  # 每个用户下 domain 唯一

    def __str__(self):
        return f"{self.domain} ({self.user.username})"


class CrawlTask(models.Model):
    STATUS_CHOICES = [
        ("crawling", "Crawling"),
        ("complete", "Complete"),
        ("fail", "Failed"),
    ]

    id = models.AutoField(primary_key=True)
    website = models.ForeignKey(
        "Website", on_delete=models.CASCADE, related_name="crawl_tasks"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_msg = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ← 新增

    def __str__(self):
        return f"{self.website.domain} - {self.status} ({self.start_time})"


# 网页模型
class Webpage(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=500)  # URL
    crawl_time = models.DateTimeField()  # 抓取时间
    website = models.ForeignKey(
        Website, related_name="webpages", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("url", "website")

    def __str__(self):
        return f"{self.url}-{self.website.user.username}"


# 内容模型
class Content(models.Model):
    CONTENT_TYPE_CHOICES = [
        ("text", "Text"),
        ("link", "Link"),
    ]

    content_id = models.AutoField(primary_key=True)  # 内容ID
    text = models.TextField()  # 文本内容
    webpage = models.ForeignKey(
        Webpage, related_name="contents", on_delete=models.CASCADE
    )  # 所属网页URL（外键）
    keywords = models.CharField(max_length=500)  # 关键字
    type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)  # 内容类型

    def __str__(self):
        return f"Content {self.content_id} from {self.webpage.url}"


# 数据源模型
class DataSource(models.Model):
    data_source_url = models.CharField(max_length=500, primary_key=True)  # 数据源URL
    publisher = models.CharField(max_length=100, null=True)  # 发布者
    publish_time = models.DateTimeField(null=True)  # 发布时间

    def __str__(self):
        return self.data_source_url


# 图片模型
class Image(models.Model):
    url = models.OneToOneField(
        DataSource, related_name="images", on_delete=models.CASCADE, primary_key=True
    )  # 数据源（外键）
    webpage = models.ForeignKey(
        Webpage, related_name="images", on_delete=models.CASCADE
    )  # 所属网页URL（外键）
    description = models.CharField(max_length=255)  # 图片描述
    resolution = models.CharField(max_length=50)  # 分辨率

    def __str__(self):
        return self.url.data_source_url


# 数据源与内容的中间表
class DataSourceContent(models.Model):
    data_source = models.ForeignKey(
        DataSource, related_name="content", on_delete=models.CASCADE
    )  # 数据源URL（外键）
    content = models.ForeignKey(
        Content, related_name="data_sources", on_delete=models.CASCADE
    )  # 内容ID（外键）

    class Meta:
        unique_together = ("data_source", "content")  # 复合主键

    def __str__(self):
        return f"{self.data_source.data_source_url} - {self.content.content_id}"
