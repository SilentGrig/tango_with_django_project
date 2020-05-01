from django.urls import path

from rango.views import (
    AboutView,
    IndexView,
    add_category,
    add_page,
    goto_url,
    register_profile,
    restricted,
    show_category,
    show_user_profile,
)

app_name = "rango"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("category/<slug:category_name_slug>/", show_category, name="show_category"),
    path("add_category/", add_category, name="add_category"),
    path("category/<slug:category_name_slug>/add_page/", add_page, name="add_page"),
    path("restricted/", restricted, name="restricted"),
    path("goto/<int:page_id>/", goto_url, name="goto"),
    path("register_profile/", register_profile, name="register_profile"),
    path("profile/", show_user_profile, name="profile"),
]
