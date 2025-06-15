from django.urls import path

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
        "Query/<str:domain>/pages/", views.website_webpages_view, name="Query_SitePages"
    ),
    path(
        "Query/<path:url>/images/", views.webpage_images_view, name="Query_PageImages"
    ),
    path(
        "Query/<path:url>/contents/",
        views.webpage_content_view,
        name="Query_PageContents",
    ),
    path(
        "content/<int:content_id>/text/",
        views.view_full_content,
        name="view_full_content",
    ),
]
