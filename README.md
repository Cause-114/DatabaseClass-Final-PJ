# 用法
在根目录下 输入：py manage.py runserver 启动本地127.0.0.1:8000的服务，然后在浏览器访问该地址。然后可以访问/crawl与/admin.二者分别对应展示出来的网页与管理数据的网页。

/admin界面：admin用户密码：（如果提示没有则需要在根目录下输入`py manage.py createsuperuer`创建管理员）完事就可以登陆管理数据库了。
- 用户名：admin
- 邮箱： 114514@1919.com
- 密码： 1145141919810

对于/crawls,可以根据提示尝试输入查看效果。（这就是我们到时候展示的主界面）。

如果你想改变路径，请到`mysite/urls.py`.

*重要：*  在运行前，请先执行`py manage.py makemigrations crawls`与`py manage.py migrate`用以创建或改变数据库中的表结构，如果已经改过了不必再改但是一旦改变了models.py必须更改。
---
# 文件结构

```
mysite/
├── settings.py         # 项目配置
├── urls.py             # 主路由配置
├── .env                # 环境变量配置
└── ...

crawls/
├── models.py           # 数据模型
├── urls.py             # 子路由
├── views.py            # 视图逻辑
├── Crawler.py          # 爬虫主类
├── Downloader.py       # 页面下载器
├── Saver.py            # 数据保存模块
└── templates/
    ├── base.html       # 模板html，渲染主界面
    └── crawls/         # 具体界面，大多继承base.html
origin.py # 王与方的原始代码（已嵌入 Crawler.py,Downloader.py,Saver.py）
built.sql # 数据库建表 SQL
manage.py # 主要的控制文件
```
---

# 数据库接口

保存数据可以用`xx.objects.update_or_create(key=xx,default={:,:})`注意外键保存必须要保存对象而不能保存字符串。
具体可见crwals/saver.py源码。
---

# 前端
针对你想要优化的界面直接改html，或者加点CSS、Image。网上搜一下教程。
------

# 更新（by CYY 6.1 2pm）：
- 增加网页前端，现在有三大主界面，
    - 爬取任务：（输入想要爬取的网址信息）
    - 展示已爬取的网页（Webpage）对应的有Website与Content,Image的子界面
    - 搜索界面（根据关键词查找Content内容），现在只是壳子，后面加上Contens加上keywords就能实现。
- 融合新的爬取数据模块，增强对Error的捕获、增强URL的规范性、增强对Encoding的判断

# *重要* ： 后面不要交给我单个的pj.py了，真的很难改，推荐看看上面的说明吧，很简单的。后面加的内容可以继续添加到这个README.md下，commit的内容能写的东西很少

# TODO: 保存数据时加上关键词(Keywords 用于关键字查找)。只要这块保证了，搜索界面就能出东西。