from django.shortcuts import render
from .CoreCrawler import StaticCrawler
from django import forms
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
            crawler=StaticCrawler(base_url)
            crawler.crawl(MaxPage,Delay)
            return render(request, "crawls/thank_you.html",{"URL":base_url})
    else:
        form = UserInputForm()  # 创建一个空的表单实例

    return render(request, "crawls/user_input.html", {"form": form})


def show_webpages(request):
    webpages = Webpage.objects.select_related("website").order_by("-crawl_time")[
        :100
    ]  # 可加分页
    return render(request, "crawls/webpages.html", {"webpages": webpages})
