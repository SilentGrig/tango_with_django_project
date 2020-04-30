from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse

from rango.bing_search import run_query
from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.models import Category, Page, UserProfile


def index(request):
    category_list = Category.objects.order_by("-likes")[:5]
    pages_list = Page.objects.order_by("-views")[:5]
    visitor_cookie_handler(request)

    context_dict = {
        "boldmessage": "Crunchy, creamy, cookie, candy, cupcake!",
        "categories": category_list,
        "pages": pages_list,
    }
    return render(request, "rango/index.html", context=context_dict)


def about(request):
    visitor_cookie_handler(request)
    context_dict = {
        "your_name": "Gregory Thomas",
        "visits": request.session["visits"],
    }
    return render(request, "rango/about.html", context=context_dict)


def show_category(request, category_name_slug):
    query, result_list = search(request)

    context_dict = {
        "query": query if query else "",
        "result_list": result_list,
    }

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.order_by("-views").filter(category=category)
        context_dict["pages"] = pages
        context_dict["category"] = category
    except Category.DoesNotExist:
        context_dict["category"] = None
        context_dict["pages"] = None

    return render(request, "rango/category.html", context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse("rango:index"))
        else:
            print(form.errors)
    return render(request, "rango/add_category.html", {"form": form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse("rango:index"))

    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(
                    reverse(
                        "rango:show_category",
                        kwargs={"category_name_slug": category_name_slug},
                    )
                )
        else:
            print(form.errors)

    context_dict = {"form": form, "category": category}
    return render(request, "rango/add_page.html", context=context_dict)


@login_required
def restricted(request):
    return render(request, "rango/restricted.html")


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))
    last_visit_cookie = get_server_side_cookie(
        request, "last_visit", str(datetime.now())
    )
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")

    # if it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session["last_visit"] = str(datetime.now())
    else:
        request.session["last_visit"] = last_visit_cookie

    request.session["visits"] = visits


def search(request):
    result_list = []
    query = None

    if request.method == "POST":
        query = request.POST.get("query").strip()
        if query:
            result_list = run_query(query)

    return query, result_list


def goto_url(request, page_id):
    if request.method == "GET":
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            page = None

        if page:
            page.views += 1
            page.save()
            return redirect(page.url)

    return redirect(reverse("rango:index"))


def register_profile(request):
    form = UserProfileForm()

    try:
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    try:
        user_profile = UserProfile.objects.get(user_id=user.id)
    except UserProfile.DoesNotExist:
        user_profile = None

    # if cant find user or user already has a profile
    if user is None or user_profile:
        return redirect(reverse("rango:index"))

    if request.method == "POST":
        form = UserProfileForm(request.POST)

        if form.is_valid():
            user_profile = form.save(commit=False)

            if "picture" in request.FILES:
                user_profile.picture = request.FILES["picture"]

            user_profile.user = user
            user_profile.save()
            return redirect(reverse("rango:index"))
        else:
            print(form.errors)

    return render(request, "rango/profile_registration.html", {"form": form})
