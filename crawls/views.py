from django.shortcuts import render, get_object_or_404
from .Crawler import Crawler
from django import forms
from django.core.paginator import Paginator
from .models import (
    Website,
    Webpage,
    Content,
    Image,
    DataSource,
    DataSourceContent,
)


class UserInputForm(forms.Form):
    URL = forms.CharField(label="URL", max_length=100)
    MaxPage = forms.IntegerField(label="MaxPage")
    Delay = forms.IntegerField(label="Delay")


def user_input_view(request):
    if request.method == "POST":
        form = UserInputForm(request.POST)
        if form.is_valid():
            # 处理有效的表单数据
            base_url = form.cleaned_data["URL"]
            MaxPage = form.cleaned_data["MaxPage"]
            Delay = form.cleaned_data["Delay"]
            crawler = Crawler(base_url)
            crawler.crawl(MaxPage, Delay)
            return render(request, "crawls/thank_you.html", {"URL": base_url})
    else:
        form = UserInputForm()  # 创建一个空的表单实例

    return render(request, "crawls/user_input.html", {"form": form})


def show_webpages(request):
    webpages = Webpage.objects.select_related("website").order_by("-crawl_time")[
        :100
    ]  # 可加分页
    return render(request, "crawls/webpages.html", {"webpages": webpages})


# 展示最近网页
def show_webpages(request):
    webpages = Webpage.objects.select_related("website").order_by("-crawl_time")[
        :100
    ]  # 可加分页
    return render(request, "crawls/webpages.html", {"webpages": webpages})


# 展示某网页的所有图片
def webpage_images_view(request, url):
    webpage = get_object_or_404(Webpage, url=url)
    images = webpage.images.all()
    return render(
        request,
        "crawls/webpage_images.html",
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
        "crawls/webpage_contents.html",
        {
            "webpage": webpage,
            "contents": contents,
        },
    )


# 搜索内容（关键字）
def search_content_view(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = Content.objects.filter(keywords__icontains=query).select_related(
            "webpage"
        )
    return render(
        request,
        "crawls/search_results.html",
        {
            "query": query,
            "results": results,
        },
    )


# 展示某个网站的所有网页
def website_webpages_view(request, domain):
    website = get_object_or_404(Website, domain=domain)
    pages = website.webpages.all().order_by("-crawl_time")
    return render(
        request,
        "crawls/website_pages.html",
        {
            "website": website,
            "pages": pages,
        },
    )
