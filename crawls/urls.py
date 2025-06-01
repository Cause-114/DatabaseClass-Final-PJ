from django.urls import path

from . import views


urlpatterns = [
    path("", views.user_input_view, name="user_input"),
    path("webpages/", views.show_webpages, name="show_webpages"),
    path(
        "webpage/<path:url>/images/", views.webpage_images_view, name="webpage_images"
    ),
    path(
        "webpage/<path:url>/contents/",
        views.webpage_content_view,
        name="webpage_contents",
    ),
    path("search/", views.search_content_view, name="search_content"),
    path(
        "website/<str:domain>/pages/", views.website_webpages_view, name="website_pages"
    ),
]
