from django.db import models


# 网站模型
class Website(models.Model):
    DOMAIN_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("manual", "Manual"),
    ]
    CRAWL_STATUS_CHOICES = [
        ("complete", "Complete"),
        ("crawling", "Crawling"),
        ("fail", "Fail"),
    ]

    domain = models.CharField(max_length=255, primary_key=True)  # 域名
    company = models.CharField(max_length=100)  # 所属公司
    contact = models.CharField(max_length=100)  # 联系信息
    crawl_freq = models.CharField(max_length=10, choices=DOMAIN_CHOICES)  # 爬取频率
    crawl_status = models.CharField(
        max_length=10, choices=CRAWL_STATUS_CHOICES
    )  # 爬取状态
    err = models.CharField(max_length=255, null=True)
    def __str__(self):
        return self.domain


# 网页模型
class Webpage(models.Model):
    id = models.AutoField(primary_key=True) 
    url = models.CharField(max_length=500, unique=True)  # URL
    crawl_time = models.DateTimeField()  # 抓取时间
    website = models.ForeignKey(
        Website, related_name="webpages", on_delete=models.CASCADE
    )  # 所属网站（外键）

    def __str__(self):
        return self.url


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
