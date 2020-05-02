from django.contrib.auth.models import User

from rango.models import Category, Page, UserProfile


def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def get_user_profile(user):
    return UserProfile.objects.get_or_create(user_id=user.id)[0]


def get_category(category_name_slug):
    try:
        return Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        return None


def get_category_list(max_results=0, starts_with=""):
    category_list = []

    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]

    return category_list
