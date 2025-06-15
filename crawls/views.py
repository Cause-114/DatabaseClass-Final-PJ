import threading
from urllib.parse import urlparse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django import forms
from django.core.paginator import Paginator
from django.db.models import Count,Q
from .Crawler import Crawler
from .models import (
    Website,
    CrawlTask,
    Webpage,
    Content,
    Image,
    DataSource,
    DataSourceContent,
)


class UserInputForm(forms.Form):
    URL = forms.URLField(
        label="URL",
        max_length=200,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "请输入网址全程,如：https://www.baidu.com",
            }
        ),
    )
    MaxPage = forms.IntegerField(
        label="最大页数",
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "例如：5"}
        ),
    )
    TimeOut = forms.IntegerField(
        label="每页最大时间限制（秒）",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "例如：3"}
        ),
    )

    def clean_URL(self):
        url = self.cleaned_data["URL"]
        if not url.startswith(("https://", "http://")):
            raise forms.ValidationError("URL须为全称，须包含https或http协议等 ")
        return url


def main_view(request):
    # 查询统计数据
    website_count = Website.objects.count()
    page_count = Webpage.objects.count()
    keyword_count = Content.objects.count()

    # 查询最近 5 条网页爬取记录，按时间倒序

    context = {
        "website_count": website_count,
        "page_count": page_count,
        "keyword_count": keyword_count,
    }
    return render(request, "crawls/Main.html", context)


####################### 增/改 ############################
# 从用户输入的website对应URL新增数据到数据库
def run_crawler_async(base_url, max_page, timeout, task_id):
    crawler = Crawler(base_url, task_id=task_id)
    crawler.crawl(max_page, timeout)


def user_input_view(request):
    if request.method == "POST":
        form = UserInputForm(request.POST)
        if form.is_valid():
            base_url = form.cleaned_data["URL"]
            max_page = form.cleaned_data["MaxPage"]
            timeout = form.cleaned_data["TimeOut"]
            domain = urlparse(base_url).netloc
            website, _ = Website.objects.get_or_create(domain=domain)
            task = CrawlTask.objects.create(website=website, status="crawling")
            t = threading.Thread(
                target=run_crawler_async, args=(base_url, max_page, timeout, task.id)
            )
            t.start()
            return HttpResponseRedirect("/Add/Tasks")
    else:
        form = UserInputForm()

    return render(request, "crawls/Add_Input.html", {"form": form})


def crawl_task_status_view(request):
    running_tasks = (
        CrawlTask.objects.filter(status="crawling")
        .select_related("website")
        .order_by("-start_time")
    )
    completed_tasks = (
        CrawlTask.objects.filter(status="complete")
        .select_related("website")
        .order_by("-start_time")
    )
    failed_tasks = (
        CrawlTask.objects.filter(status="fail")
        .select_related("website")
        .order_by("-start_time")
    )

    context = {
        "running_tasks": running_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
    }
    return render(request, "crawls/Add_Status.html", context)


####################### 删 ############################


####################### 查 ############################
# 搜索内容（关键字）
def search_content_view(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = Content.objects.filter(keywords__icontains=query).select_related(
            "webpage"
        )
    recent_pages = Webpage.objects.select_related("website").order_by("-crawl_time")[
        :10
    ]
    return render(
        request,
        "crawls/Query_KeywordSearch.html",
        {
            "query": query,
            "results": results,
            "recent_pages": recent_pages,
        },
    )


# 展示已经爬取的网站
def recent_websites(request):
    # 找出至少有一个已完成爬取任务的 Website
    websites = (
        Website.objects.filter(crawl_tasks__status="complete")
        .distinct()
        .annotate(page_count=Count("webpages", distinct=True))
        .order_by("-domain")
    )
    return render(request, "crawls/Query_Website.html", {"websites": websites})


# 展示某个网站的所有网页
def website_webpages_view(request, domain):
    website = get_object_or_404(Website, domain=domain)
    pages = website.webpages.all().order_by("-crawl_time")
    return render(
        request,
        "crawls/Query_SitePages.html",
        {
            "website": website,
            "pages": pages,
        },
    )


# 展示某网页的所有图片
def webpage_images_view(request, url):
    webpage = get_object_or_404(Webpage, url=url)
    images = webpage.images.all()
    return render(
        request,
        "crawls/Query_PageImages.html",
        {
            "webpage": webpage,
            "images": images,
        },
    )


# 展示某网页的所有内容
def webpage_content_view(request, url):
    webpage = get_object_or_404(Webpage, url=url)
    contents = webpage.contents.all()
    return render(
        request,
        "crawls/Query_PageContents.html",
        {
            "webpage": webpage,
            "contents": contents,
        },
    )


def view_full_content(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    return HttpResponse(content.text, content_type="text/plain; charset=utf-8")
