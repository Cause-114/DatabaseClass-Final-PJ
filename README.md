# 用法
在根目录下 输入：py manage.py runserver 启动本地127.0.0.1:8000的服务，然后在浏览器访问该地址。
然后可以访问/crawl与/admin.二者分别对应展示出来的网页与管理数据的网页。admin用户密码：
- 用户名：admin
- 邮箱： 114514@1919.com
- 密码： 1145141919810

对于/crawls,可以根据提示尝试输入查看效果。

*重要：*  在运行前，请先执行`py manage.py makemigrations crawls`与`py manage.py migrate`
---

# mysite文件夹：
## setting.py：
一些简单设置，比如数据库配置，语言、时区、注册的app（除了mysite，其它同级文件要用都得在setting里注册）
## urls.py: 
当前网站的站点的包含的网页，比如目前包含了/crawls与/admin
## .env 
数据库连接环境变量配置，具体可以参考一下我gitignore里面写的注释或者郑翔的那个教程
## 其他文件暂时不用考虑
---

# crawls文件夹
## models.py 
定义数据库表结构
## urls.py 
当前路径下的网页（必须接到mysite文件的urls.py下）
## 
views.py 对应网页的视图（要接到mysite）
## CoreCrawler.py
对外提供一个爬取数据的类（StaticCrwaler）
## templates/crawls
该文件夹下放了一些html模板，后面可以继续考虑加static文件夹放一些图片、JS、CSS渲染前端
---

# origin.py: 
王与方的原始代码（嵌入到crawls/CoreCrawler.py）
# built.sql: 
models.py 定义表的实际SQL语句，可供参考。

---

# 数据库接口
保存数据可以用`xx.objects.update_or_create(key=xx,default={:,:})`注意外键保存必须要保存对象而不能保存字符串。
具体可见CoreCralwer.py源码。
---

# 前端
可以先写起来html，想好我们需要哪些模板与展示的网页，后面导到templates里面就行。接口我来改。


# *后面家的内容可以继续添加到这个README.md下，commit的内容能写的东西很少*