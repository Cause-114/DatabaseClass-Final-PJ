import threading
from urllib.parse import urlparse
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


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
            website, _ = Website.objects.get_or_create(domain=domain, user=request.user)
            task = CrawlTask.objects.create(
                website=website, status="crawling", user=request.user
            )
            t = threading.Thread(
                target=run_crawler_async, args=(base_url, max_page, timeout, task.id)
            )
            t.start()
            return redirect("Add_Status")
    else:
        form = UserInputForm()
    return render(request, "crawls/Add_Input.html", {"form": form})

####################### 删 ############################


####################### 查 ############################
# 搜索内容（关键字）
@login_required
def search_content_view(request):
    query = request.GET.get("q", "")
    if request.user.is_superuser:
        results = (
            Content.objects.filter(keywords__icontains=query).select_related("webpage")
            if query
            else []
        )
        recent_pages = Webpage.objects.select_related("website").order_by(
            "-crawl_time"
        )[:10]
    else:
        results = (
            Content.objects.filter(
                keywords__icontains=query, webpage__website__user=request.user
            ).select_related("webpage")
            if query
            else []
        )
        recent_pages = (
            Webpage.objects.filter(website__user=request.user)
            .select_related("website")
            .order_by("-crawl_time")[:10]
        )

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
@login_required
def recent_websites(request):
    if request.user.is_superuser:
        websites = (
            Website.objects.filter(crawl_tasks__status="complete")
            .distinct()
            .annotate(page_count=Count("webpages", distinct=True))
            .order_by("-domain")
        )
    else:
        websites = (
            Website.objects.filter(crawl_tasks__status="complete", user=request.user)
            .distinct()
            .annotate(page_count=Count("webpages", distinct=True))
            .order_by("-domain")
        )
    return render(request, "crawls/Query_Website.html", {"websites": websites})


# 展示已经爬取的网页
@login_required
def recent_webpages(request):
    if request.user.is_superuser:
        webpages = Webpage.objects.all().distinct().order_by("-crawl_time")
    else:
        webpages = (
            Webpage.objects.filter(website__user=request.user)
            .distinct()
            .order_by("-crawl_time")
        )
    return render(request, "crawls/Query_Webpage.html", {"webpages": webpages})


# 展示所有爬取状态
@login_required
def crawl_task_status_view(request):
    if request.user.is_superuser:
        running_tasks = CrawlTask.objects.filter(status="crawling").select_related(
            "website"
        )
        completed_tasks = CrawlTask.objects.filter(status="complete").select_related(
            "website"
        )
        failed_tasks = CrawlTask.objects.filter(status="fail").select_related("website")
    else:
        running_tasks = CrawlTask.objects.filter(
            user=request.user, status="crawling"
        ).select_related("website")
        completed_tasks = CrawlTask.objects.filter(
            user=request.user, status="complete"
        ).select_related("website")
        failed_tasks = CrawlTask.objects.filter(
            user=request.user, status="fail"
        ).select_related("website")

    context = {
        "running_tasks": running_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
    }
    return render(request, "crawls/Add_Status.html", context)


# 展示某个网站的所有网页
@login_required
def website_webpages_view(request, site_id):
    website = get_object_or_404(Website, id=site_id)
    pages = website.webpages.all().order_by("-crawl_time")
    return render(
        request,
        "crawls/Query_SitePages.html",
        {"website": website, "pages": pages},
    )


# 展示某网页的所有图片
@login_required
def webpage_images_view(request, page_id):
    webpage = get_object_or_404(Webpage, id=page_id)
    images = webpage.images.all()
    return render(
        request,
        "crawls/Query_PageImages.html",
        {"webpage": webpage, "images": images},
    )


# 展示某网页的所有内容
@login_required
def webpage_content_view(request, page_id):
    webpage = get_object_or_404(Webpage, id=page_id)
    contents = webpage.contents.all()
    return render(
        request,
        "crawls/Query_PageContents.html",
        {"webpage": webpage, "contents": contents},
    )


@login_required
def view_full_content(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    return render(request, "crawls/view_full_content.html", {"content": content})


#####################用户###########################
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 注册后自动登录
            return redirect("Main")
    else:
        form = UserCreationForm()
    return render(request, "crawls/User_register.html", {"form": form})


def about_us_view(request):
    return render(request, "crawls/About_us.html")
