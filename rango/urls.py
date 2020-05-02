from django.contrib.auth.decorators import login_required
from django.urls import path

from rango.views import (
    AboutView,
    AddCategoryView,
    AddPageView,
    CategorySuggestionView,
    IndexView,
    LikeCategoryView,
    ProfileListView,
    ProfileView,
    RegisterProfileView,
    SearchAddPageView,
    ShowCategoryView,
    goto_url,
    restricted,
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
    path(
        "profile/<str:username>/", login_required(ProfileView.as_view()), name="profile"
    ),
    path(
        "list_profiles/",
        login_required(ProfileListView.as_view()),
        name="list_profiles",
    ),
    path(
        "like_category/",
        login_required(LikeCategoryView.as_view()),
        name="like_category",
    ),
    path("suggest/", CategorySuggestionView.as_view(), name="suggest"),
    path(
        "search_add_page/",
        login_required(SearchAddPageView.as_view()),
        name="search_add_page",
    ),
]
