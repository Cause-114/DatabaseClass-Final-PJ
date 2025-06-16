from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path("", views.main_view, name="Main"),
    ####################### 增 ############################
    path("Add/", views.user_input_view, name="Add_Input"),
    path("Add/Tasks/", views.crawl_task_status_view, name="Add_Status"),
    ####################### 删 ############################
    path("Delete/", views.website_delete_list_view, name="Delete_List"),
    path("Delete/Website/<int:id>/", views.delete_webstie_view, name="Delete_Website"),
    path("Delete/SitePages/<int:id>/", views.delete_site_page_view, name="Delete_SitePage"),
    path("Delete/Webpage/Delete/<int:webpage_id>/", views.delete_webpage_view, name="Delete_Webpage"),
    path("Delete/Webpage/<int:webpage_id>/Contents/", views.view_webpage_contents, name="Delete_PageContent"),
    path("Delete/Webpage/Content/Delete/<int:content_id>/", views.delete_content_view, name="Delete_ContentItem"),
    path("Delete/Webpage/Image/Delete/<path:url>/", views.delete_image_view, name="Delete_ImageItem"),
    path("Delete/Webpage/Images/<int:webpage_id>/", views.view_webpage_images, name="Delete_PageImage"),
    ####################### 改 ############################
    ####################### 查 ############################
    path("Query/KeySearch/", views.search_content_view, name="Query_KeywordSearch"),
    path("Query/Websites/", views.recent_websites, name="Query_Website"),
    path("Query/Webpages/", views.recent_webpages, name="Query_Webpage"),
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
