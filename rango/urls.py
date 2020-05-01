from django.contrib.auth.decorators import login_required
from django.urls import path

from rango.views import (
    AboutView,
    AddCategoryView,
    AddPageView,
    IndexView,
    RegisterProfileView,
    ShowCategoryView,
    goto_url,
    restricted,
    show_user_profile,
)

app_name = "rango"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path(
        "category/<slug:category_name_slug>/",
        ShowCategoryView.as_view(),
        name="show_category",
    ),
    path(
        "add_category/", login_required(AddCategoryView.as_view()), name="add_category"
    ),
    path(
        "category/<slug:category_name_slug>/add_page/",
        login_required(AddPageView.as_view()),
        name="add_page",
    ),
    path("restricted/", restricted, name="restricted"),
    path("goto/<int:page_id>/", goto_url, name="goto"),
    path(
        "register_profile/",
        login_required(RegisterProfileView.as_view()),
        name="register_profile",
    ),
    path("profile/", show_user_profile, name="profile"),
]
