from django.urls import path

from . import views


urlpatterns = [
    path("", views.main_view, name="Main"),
    ####################### 增 ############################
    path("Add/", views.user_input_view, name="Add_Input"),
    ####################### 删 ############################
    ####################### 改 ############################
    ####################### 查 ############################
    path("Query/KeySearch/", views.search_content_view, name="Query_KeywordSearch"),
    path("Query/Websites/", views.recent_websites, name="Query_Website"),
    path(
        "Query/<str:domain>/pages/", views.website_webpages_view, name="Query_SitePages"
    ),
    path(
        "Query/page/<int:page_id>/images/",
        views.webpage_images_view,
        name="Query_PageImages",
    ),
    path(
        "Query/page/<int:page_id>/contents/",
        views.webpage_content_view,
        name="Query_PageContents",
    ),
]
