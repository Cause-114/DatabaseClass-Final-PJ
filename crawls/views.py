from django.shortcuts import render, get_object_or_404
from .Crawler import Crawler
from django import forms
from django.core.paginator import Paginator
from django.db.models import Count

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


def main_view(request):
    # 查询统计数据
    website_count = Website.objects.count()
    page_count = Webpage.objects.count()
    keyword_count = Content.objects.count()

    # 查询最近 5 条网页爬取记录，按时间倒序
    recent_pages = Webpage.objects.select_related("website").order_by("-crawl_time")[:5]

    context = {
        "website_count": website_count,
        "page_count": page_count,
        "keyword_count": keyword_count,
        "recent_pages": recent_pages,
    }
    return render(request, "crawls/Main.html", context)


####################### 增/改 ############################
# 从用户输入的website对应URL新增数据到数据库
def user_input_view(request):
    if request.method == "POST":
        form = UserInputForm(request.POST)
        if form.is_valid():
            # 处理有效的表单数据
            base_url = form.cleaned_data["URL"]
            MaxPage = form.cleaned_data["MaxPage"]
            Delay = form.cleaned_data["Delay"]
            crawler = Crawler(base_url)
            domain=crawler.crawl(MaxPage, Delay)
            return render(request, "crawls/Add_Complete.html", {"Domain": domain})
    else:
        form = UserInputForm()  # 创建一个空的表单实例

    return render(request, "crawls/Add_Input.html", {"form": form})
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
    return render(
        request,
        "crawls/Query_KeywordSearch.html",
        {
            "query": query,
            "results": results,
        },
    )

# 展示已经爬取的网站
def recent_websites(request):
    # 查询最近10个完成爬取的网站，并统计各自网页数
    websites = (
        Website.objects.filter(crawl_status="complete")
        .annotate(page_count=Count("webpages"))
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
def webpage_images_view(request, page_id):
    webpage = get_object_or_404(Webpage, id=page_id)
    images = webpage.images.all()
    return render(
        request, "crawls/Query_PageImages.html", {"webpage": webpage, "images": images}
    )


# 展示某网页的所有内容
def webpage_content_view(request, page_id):
    webpage = get_object_or_404(Webpage, id=page_id)
    contents = webpage.contents.all()
    return render(
        request,
        "crawls/Query_PageContents.html",
        {
            "webpage": webpage,
            "contents": contents,
        },
    )
