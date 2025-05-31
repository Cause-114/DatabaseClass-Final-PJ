from django.urls import path

from . import views


urlpatterns = [
    path("", views.user_input_view, name="user_input"),
    path("webpages/", views.show_webpages, name="show_webpages"),
]
