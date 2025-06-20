# 用前须知
本项目为基于 Django 框架开发的网页爬虫系统，支持用户注册、登录后提交网站链接进行网页内容抓取，包括文字与图片，并可在网页端系统中查询、管理相关数据。

---

## 一、开发环境说明
- **操作系统**：推荐使用 Windows 10以上（我本地为`Windows11`） 或 macOS / Linux（x86 架构）`(对于macOS与Linux用户，终端运行python命令行时请使用python全称，而不是简单的py)`
- **Python**：版本推荐 $\geq$ 3.11.x（我本地为`python 3.12.6`）
- **MySQL**：版本推荐 $\geq$ 8.0.x（我本地为`mysql ver 8.0.41 for Win64 on x86_64 (MySQL Community Server - GPL)`）
- **依赖包**（可通过 `pip install -r requirements.txt` 安装）：
  - django
  - mysqlclient（或 pymysql 替代）
  - django-environ
  - urllib
  - beautifulsoup4 (bs4)
  - requests
  - url_normalize
  - jieba

若遇到 `mysqlclient` 编译问题：
- 安装 `pymysql` 替代
- 并在 `./mysite/__init__.py` 中添加：
  ```python
  import pymysql
  pymysql.install_as_MySQLdb()
  ```

---

## 二、数据库初始化流程
1. **启动 MySQL 服务**，确认账号密码无误
2. 在 `mysite` 目录下创建 `.env` 文件，内容如下：
   ```env
   DB_NAME=your_database_name
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```
   需要注意的是，在运行本项目前，你需要确保你的database确实存在，否则，你可以通过`CREATE DATABASE your_database_nam;`来创建一个新数据库。
3. 执行数据库建表操作(`py`这样的的简略写法仅限Windows用户，其它请使用`python`全称，下略)：
   ```bash
   py manage.py makemigrations crawls
   py manage.py migrate
   ```
   每次修改 `models.py` 后均需执行上述命令。

如需参考建表逻辑，也可参见 `built.sql` 中的 SQL 示例。

---

## 三、测试数据导入方法

- 方法一：通过 Django Shell 导入数据（快速模拟后端数据库状态）步骤：
    1. 确保数据库已初始化：

    ```bash
    py manage.py makemigrations
    py manage.py migrate
    ```

    2. 创建超级用户（可跳过，若已存在）：

    ```bash
    py manage.py createsuperuser
    ```

    3. 启动 Django Shell：

    ```bash
    py manage.py shell
    ```

    4. 在交互式终端中执行如下代码导入一组完整数据：

    ```python
    from django.contrib.auth.models import User
    from crawls.models import Website, Webpage, Content, CrawlTask, DataSource, Image
    from datetime import datetime

    # 创建测试用户
    user = User.objects.create_user(username='testuser', password='123456')

    # 创建网站
    website = Website.objects.create(
        user=user,
        domain='example.com',
        title='示例网站',
        description='这是一个测试站点',
        homepage='https://example.com'
    )

   # 创建爬取任务
    task = CrawlTask.objects.create(
       website=website,
       user=user,
       status='complete'
    )

    # 创建网页
    page = Webpage.objects.create(
       url='https://example.com/page1',
       crawl_time=datetime.now(),
       website=website
    )

    # 创建文本内容
    Content.objects.create(
       text='这是首页的介绍内容。',
       webpage=page,
       keywords='首页,介绍',
       type='text'
    )

    # 创建数据源
    ds = DataSource.objects.create(
        data_source_url='https://example.com/img1.jpg',
        publisher='测试发布者',
        publish_time=datetime.now()
    )

    # 创建图片并关联数据源
    Image.objects.create(
        url=ds,
        webpage=page,
        description='测试图片',
        resolution='1920x1080'
    )
    ```

    5. 启动项目并访问页面验证数据展示是否正常：

    ```
    http://127.0.0.1:8000
    ```

    ---

- 方法二：通过前端网页创建爬取任务（完整模拟使用流程）步骤：
    1. 启动开发服务器：

    ```bash
    py manage.py runserver
    ```

    2. 在浏览器中打开主页：

    ```
    http://127.0.0.1:8000
    ```

    3. 点击导航栏中的“新建爬取任务”或“新增数据”按钮，进入新增爬取界面。

    4. 填写以下字段内容：

    * **URL**：完整网址（必须包含 http\:// 或 https\://）
        例如：`https://example.com`
    * **最大页数**：设为 `1` 或任意你要测试的值（如 `3`）
    * **每页最大时间限制（秒）**：建议填 `3`～`5`

    5. 点击“提交”，后台将自动创建：

    * 对应的网站对象（`Website`）
    * 对应的爬取任务（`CrawlTask`）
    * 后续由爬虫自动保存网页、内容、图片等数据

    6. 页面跳转至任务状态列表，可观察任务是否正在运行或已完成。

    7. 在导航栏点击“爬取网站”、“关键字搜索”等功能页，即可查看新创建的爬取结果与相关数据。


---

## 四、项目运行步骤

在经过以上的安装依赖库、数据库结构初始化后就可以在根目录终端运行以下代码来启动服务了：
（当然你也可以先在终端创建一个superuser管理员再登录；或者更一般地你只需要在网页端注册一个用户）
```bash
py manage.py runserver
```
系统将运行在 `http://127.0.0.1:8000` 上。

### 页面功能简介：
- **主界面**：展示爬取数量统计，欢迎词等
- **新增任务(增、改数据)**：输入 URL 开始爬取任务
- **查数据**：关键词搜索、网站列表、网页列表、图片与文本内容查看
- **删数据**：支持网站、网页、文本、图片的删除操作
- **后台管理**：需要管理员权限（superuser）输入创建的超级用户信息登录
  ```bash
  py manage.py createsuperuser
  ```
- **报错自查**：如果不幸遇到爬取任务失败的情况，你可以在项目根目录下找到`crawler.log`，在这里你可以查看日志与报错信息。（不过这种情况应该几乎没有吧，hhh）
### 用户创建与权限说明：
    
访问`http://127.0.0.1:8000/`，可以看到右上角的登录/注册按钮，点击即可登录或者注册。但在该界面注册的用户无管理员权限。只能看到自己曾经爬取或创建的内容，也只能对自己的内容进行修改。但在如上述方法终端注册的`superuser`将拥有管理员权限，能够管理、抽查他人的数据。

---

## 五、项目文件结构说明
```
project_root/
├── mysite/
│   ├── settings.py         # 项目配置
│   ├── urls.py             # 主路由配置
│   ├── .env                # 环境变量配置
│   └── ...
│
├── static/
│   ├── css/                # CSS 样式文件
│   └── picture/            # 图片资源
│
├── crawls/
│   ├── models.py           # 数据模型
│   ├── urls.py             # 子路由
│   ├── views.py            # 视图逻辑
│   ├── Crawler.py          # 爬虫主类
│   ├── Downloader.py       # 页面下载器
│   ├── Saver.py            # 数据保存模块
│   └── templates/
│       ├── base.html       # 模板html，渲染主界面
│       └── crawls/         # 具体界面，大多继承base.html
│
├── Explain.sql            # 说明文档：SQL操作、删除逻辑、建表语句等
├── README.md              # 使用说明
└── manage.py              # 启动/管理脚本
```

---

## 六、小组成员与分工
| 成员   | 职责说明 |
|--------|----------|
| 陈远洋 | 项目框架设计与搭建，功能整合与核心功能实现，前端设计优化与README等编写 |
| 方昱凯 | 爬虫功能开发，数据库表结构优化与设计，期末汇报 PPT 制作，网页样式优化 |
| 郭轩岩 | 网页数据删除模块开发，网页html样式优化，elearning提交版本文档整理 |
| 王艺涵 | 爬虫功能支持，首页与团队页设计，数据表索引设计，期中、期末汇报展示 |


---

## 七、后续开发功能
- 增加用户需要不同网页爬取顺序的功能（当前为广度优先搜索，比如用户需要针对某一特殊网页进行深度优先搜索我们没有提供接口）。
- 优化解析数据源的逻辑（某些网站的meta头不能够解析出作者等信息，我们需要增强这部分解析适配性，争取多渠道解析）。
- 加强一些需要认证登录、验证码的网站解析（如复旦的jwfw需要提供用户名，密码等信息；后期可以加上这些内容让用户输入）。
- 更加结构化解析网页内容（当前只是简单地将所有文字内容进行保存，而没有针对某一具体化网站结构进行解析）。

---

## 八、新建网页（功能）方法（以删除为例）
1. 在 `views.py` 中添加视图函数
2. 在 `urls.py` 的 `urlpatterns` 中注册对应路径
3. 在 `templates/crawls` 下创建 HTML 模板，继承 `base.html`
4. （可选）在导航栏中添加链接 `<a class="nav-link" href="{% url 'Delete_Data' %}">删除数据</a>`

页面之间链接跳转方式：
```html
<a href="{% url '视图名' 参数 %}">显示文字</a>
```
## 九、导出测试数据
若需要加载已爬取的数据，建议以 `.sql`格式导出文件。
在终端中输入以下命令：
```bash
mysqldump -u root -p your_database > sample_data.sql
```
导入方式:
```bash
mysql -u root -p your_database < sample_data.sql
```