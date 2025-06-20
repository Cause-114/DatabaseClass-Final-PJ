import threading
from urllib.parse import urlparse, unquote, quote
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages


from .Crawler import Crawler
from .models import (
    Website,
    CrawlTask,
    Webpage,
    Content,
    Image,
    DataSource,
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

@login_required
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
@login_required
def website_delete_list_view(request):
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
    return render(request, "crawls/Delete_List.html", {"websites": websites})


def delete_webstie_view(request, id):
    if request.method == "POST":
        try:
            website = get_object_or_404(Website, id=id)
            webpages = Webpage.objects.filter(website=website)
            for webpage in webpages: 
                DataSource.objects.filter(data_source_url=webpage.url).delete()  
                image_urls = Image.objects.filter(webpage=webpage).values_list('url', flat=True)
                DataSource.objects.filter(data_source_url__in=image_urls).delete()
            Webpage.objects.filter(website=website).delete()
            website.delete()
            messages.success(request, f"网站 {id} 已成功删除。")
        except Exception as e:
            messages.error(request, f"删除失败: {e}")
        return redirect('Delete_List')
    return redirect('Delete_List')

@login_required
def delete_site_page_view(request, id):
    website = get_object_or_404(Website, id=id)
    pages = Webpage.objects.filter(website=website).order_by("-crawl_time")
    return render(request, "crawls/Delete_SitePage.html", {
        "website": website,
        "pages": pages
    })


def delete_webpage_view(request, webpage_id):
    webpage = get_object_or_404(Webpage, id=webpage_id)

    if request.method == "POST":
        id = webpage.website.id
        ds=get_object_or_404(DataSource, data_source_url=webpage.url)
        ds.delete()
        image_urls = Image.objects.filter(webpage=webpage).values_list('url', flat=True)
        DataSource.objects.filter(data_source_url__in=image_urls).delete()
        Content.objects.filter(webpage=webpage).delete()
        Image.objects.filter(webpage=webpage).delete()
        webpage.delete()
        messages.success(request, "该网页及相关内容已成功删除")
        return redirect("Delete_SitePage", id=id)
    return redirect("Delete_List")


# 显示网页的所有文本内容
@login_required
def delete_page_content_view(request, content_id):
    content = get_object_or_404(Content, content_id=content_id)
    webpage = content.webpage
    contents = Content.objects.filter(webpage=webpage)

    return render(request, "crawls/Delete_PageContent.html", {
        "webpage": webpage,
        "contents": contents,
    })

def view_webpage_contents(request, webpage_id):
    webpage = get_object_or_404(Webpage, id=webpage_id)
    contents = Content.objects.filter(webpage=webpage)

    return render(request, "crawls/Delete_PageContent.html", {
        "webpage": webpage,
        "contents": contents,
    })


# 删除单个文本内容后返回该网页内容列表
def delete_content_view(request, content_id):
    content = get_object_or_404(Content, content_id=content_id)
    webpage_id = content.webpage.id
    ds=get_object_or_404(DataSource, data_source_url=content.webpage.url)
    if request.method == "POST":
        content.delete()
        ds.delete() 
        messages.success(request, "该文本内容已成功删除。")
    return redirect("Delete_PageContent", webpage_id=webpage_id)


# 显示网页的所有图片
@login_required
def delete_page_image_view(request, url):
    data_source = get_object_or_404(DataSource, data_source_url=url)
    image = get_object_or_404(Image, url=data_source)
    webpage = image.webpage
    images = Image.objects.filter(webpage=webpage)

    return render(request, "crawls/Delete_PageImage.html", {
        "webpage": webpage,
        "images": images,
    })


# 删除单张图片后返回该网页图片列表
def delete_image_view(request, url):
    url = unquote(url)
    data_source = get_object_or_404(DataSource, data_source_url=url)
    image = get_object_or_404(Image, url=data_source)
    webpage_id = image.webpage.id
    if request.method == "POST":
        image.delete()
        data_source.delete()
        messages.success(request, "该图片已成功删除。")
    return redirect("Delete_PageImage", webpage_id=webpage_id)


@login_required
def view_webpage_images(request, webpage_id):
    webpage = get_object_or_404(Webpage, id=webpage_id)
    images = Image.objects.filter(webpage=webpage)
    return render(request, "crawls/Delete_PageImage.html", {
        "webpage": webpage,
        "images": images,
    })


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
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("Main")
    return render(request, "crawls/User_register.html", {"form": form})


def about_us_view(request):
    return render(request, "crawls/About_us.html")
