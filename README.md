# 用前须知
本项目依赖于MYSQL数据库服务与Python解释器，在运行前请确保二者正确安装并添加到环境变量中。

首先，如果你是从GitHub远程仓库下载下来。请先在`./mysite`目录下创建`.env`文件该文件包含以下内容：
```
DB_NAME=your database name
DB_USER=root
DB_PASSWORD=your password
DB_HOST=localhost
DB_PORT=3306
```
在启动项目前，请保证你的mysql(`8.0.xx`以上)数据库服务正常启动。

同时本项目要求python版本在`3.11.x`以上。项目运行依赖的包包括：
```
django, mysqlclient, environ, urllib, bs4, requests, url_normalize, jieba
```
如果在`pip install mysqlclient`过程中遇到提示编译问题。请安装包`pymysql`作为替代，并在`./mysite/__init__.py` 文件中
添加如下代码:
```
import pymysql
pymysql.install_as_MySQLdb()
```

在运行前，请先执行`py manage.py makemigrations crawls`与`py manage.py migrate`用以创建或改变数据库中的表结构，如果已经改过了不必再改但是一旦改变了models.py必须更改。

---

# 运行方法
打开终端(cmd, powershell都可以，但是要保证python在你的环境变量中)，在根目录路径下输入：`py manage.py runserver` 启动本地127.0.0.1:8000的服务，然后在浏览器访问该地址。在新建爬取任务时，状态栏的URL请一律输入网站全称，如`https://www.baidu.com`。

/admin界面：这是一个后台管理界面，如果需要查看，请在根目录下输入`py manage.py createsuperuser`创建管理员，然后就可以登陆管理数据库，查看爬取的具体数据了！

如果你想改变路径，请到`mysite/urls.py`.

---

# 文件结构
```
project_root/
├── mysite/
    ├── settings.py         # 项目配置
    ├── urls.py             # 主路由配置
    ├── .env                # 环境变量配置
    └── ...

├── static/
    ├── css/                # 静态网页格式渲染文件
    └── picture/            # 网页图片（暂时没有）

├── crawls/
    ├── models.py           # 数据模型
    ├── urls.py             # 子路由
    ├── views.py            # 视图逻辑
    ├── Crawler.py          # 爬虫主类
    ├── Downloader.py       # 页面下载器
    ├── Saver.py            # 数据保存模块
    └── templates/
        ├── base.html       # 模板html，渲染主界面
        └── crawls/         # 具体界面，大多继承base.html
    built.sql # 数据库建表 SQL
    manage.py # 主要的控制文件
```
---

# 更新（6.15 1pm）：
- 优化网页前端逻辑，现在有四大主界面，
    - 主界面，欢迎词与项目介绍，展示最近爬取内容。
    - 增、改数据——新建爬取任务
    - 查数据——关键字搜索
    - 查数据——爬取过的网站（website）展示。
    - 删数据——（有待实现）
- 在每一次爬取数据后可以变成只跳到独对应domain（本次新增）的website列表。
- 现在admin可以不用手动输入，只需要在单击右上角即可跳转后台管理；并且直接打开`127.0.0.1:8000`即可跳转主界面。
- 添加基于结巴分词的关键词提取，完整实现查数据界面的关键字搜索

后面加的内容可以继续添加到这个README.md下，commit的内容能写的东西很少

---

# TODO: 
- 增加删除界面的业务逻辑
- 优化CSS格式

---

新建网页方法：(均在crawls文件夹下)
1. 在views.py对应部分添加视图函数。包含的参数有`request, xxx(可能有，看该网页是否需要传一个参数)`，进行一系列操作后返回`render(request, 到html模板的路径, 返回给html的参数列表)`。直接去我注释的“删”部分加函数。
2. 在urls.py文件的`urlpatterns`里面添加一条path，path包含的三个参数从左到右为网页端相对的路径、对应1中的视图函数名称、被其他html引用时的名字。（为了风格统一，建议命名为Delete_Xxx）.
3. 在templates\crawls文件夹下创建对应的html，为了保证整体网页端风格一致，你需要继承base.html文件（相当于头尾不用你写，你只需要在“{% extends "base.html" %}{% block content %}”与“{% endblock %}”中间加上你要在html展示的部分。）。不过鉴于“增删改查”是数据库的四个常见平级操作，建议在base.html的nav里面加上该部分.html的连接`<a class="nav-link" href="{% url 'Delete_Data' %}">删除数据</a>`（假设你在2中为改功能命名为'Delete_Data'）。我觉得基于美观考量，可以只添加主要的Detele这样一个壳子，然后再壳子下面再分别加上选择删除网站(website)，网页(webpage)，文本(content)，图片(Image)，数据源(DataSourse)等操作。看时间与具体情况，可以选择完成部分功能，可以参考Explain.sql里面删除部分选择若干功能进行实现。
4. 此为说明，不是必要步骤。在html之间添加链接跳转逻辑时，格式为`<a href="{% url '名字' % 参数 }">一段文字</a>`。名字时你在urls.py里面定义的；参数是可选的（取决于对应视图函数是否需要除了request之外的参数）；一段文字是对应超链接的显示文字。