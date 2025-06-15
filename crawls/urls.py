from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path("", views.main_view, name="Main"),
    ####################### 增 ############################
    path("Add/", views.user_input_view, name="Add_Input"),
    path("Add/Tasks", views.crawl_task_status_view, name="Add_Status"),
    ####################### 删 ############################
    ####################### 改 ############################
    ####################### 查 ############################
    path("Query/KeySearch/", views.search_content_view, name="Query_KeywordSearch"),
    path("Query/Websites/", views.recent_websites, name="Query_Website"),
    path(
        "Query/<int:site_id>/pages/",
        views.website_webpages_view,
        name="Query_SitePages",
    ),
    path(
        "Query/page/<int:page_id>/images/",
        views.webpage_images_view,
        name="Query_PageImages",
    ),
    path(
        "Query/<int:page_id>/contents/",
        views.webpage_content_view,
        name="Query_PageContents",
    ),
    path(
        "content/<int:content_id>/text/",
        views.view_full_content,
        name="view_full_content",
    ),
    ###########################用户#########################
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="crawls/User_Login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register_view, name="register"),
    path(
        "About/us/",
        views.about_us_view,
        name="About_us",
    ),
]
