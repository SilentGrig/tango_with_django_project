from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from rango.bing_search import run_query
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page, UserProfile


class IndexView(View):
    def get(self, request):
        category_list = Category.objects.order_by("-likes")[:5]
        pages_list = Page.objects.order_by("-views")[:5]
        visitor_cookie_handler(request)

        context_dict = {
            "boldmessage": "Crunchy, creamy, cookie, candy, cupcake!",
            "categories": category_list,
            "pages": pages_list,
        }
        return render(request, "rango/index.html", context=context_dict)


class AboutView(View):
    def get(self, request):
        visitor_cookie_handler(request)
        context_dict = {
            "your_name": "Gregory Thomas",
            "visits": request.session["visits"],
        }
        return render(request, "rango/about.html", context=context_dict)


class ShowCategoryView(View):
    query = ""
    result_list = []
    template_name = "rango/category.html"

    def get(self, request, category_name_slug):
        context_dict = self.generate_context(request, category_name_slug)
        return render(request, self.template_name, context=context_dict)

    def post(self, request, category_name_slug):
        self.search(request)
        context_dict = self.generate_context(request, category_name_slug)
        return render(request, self.template_name, context=context_dict)

    def search(self, request):
        if request.method == "POST":
            self.query = request.POST.get("query").strip()
            if self.query:
                self.result_list = run_query(self.query)

    def generate_context(self, request, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.order_by("-views").filter(category=category)
            context_dict["pages"] = pages
            context_dict["category"] = category
        except Category.DoesNotExist:
            context_dict["category"] = None
            context_dict["pages"] = None

        context_dict["query"] = self.query
        context_dict["result_list"] = self.result_list
        return context_dict


class AddCategoryView(View):
    form_class = CategoryForm
    template_name = "rango/add_category.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse("rango:index"))
        else:
            print(form.errors)

        return render(request, self.template_name, context={"form": form})


class AddPageView(View):
    form_class = PageForm
    template_name = "rango/add_page.html"

    def get(self, request, category_name_slug):
        category = get_category(category_name_slug)

        if category is None:
            return redirect(reverse("rango:index"))

        form = self.form_class()

        context_dict = {"form": form, "category": category}
        return render(request, self.template_name, context=context_dict)

    def post(self, request, category_name_slug):
        category = get_category(category_name_slug)

        if category is None:
            return redirect(reverse("rango:index"))

        form = self.form_class(request.POST)

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
        return render(request, self.template_name, context=context_dict)


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


class RegisterProfileView(View):
    class_form = UserProfileForm
    template_name = "rango/profile_registration.html"

    def get(self, request):
        user = get_user(request)
        user_profile = get_user_profile(user)
        # if cant find user or user already has a profile
        if user is None or user_profile:
            return redirect(reverse("rango:index"))

        form = self.class_form()

        return render(request, self.template_name, {"form": form})

    def post(self, request):
        user = get_user(request)
        user_profile = get_user_profile(user)

        # if cant find user or user already has a profile
        if user is None or user_profile:
            return redirect(reverse("rango:index"))

        form = self.class_form(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            return redirect(reverse("rango:index"))
        else:
            print(form.errors)

        return render(request, self.template_name, {"form": form})


def show_user_profile(request):
    user = get_user(request)
    if not user:
        return redirect(reverse("rango:index"))

    context_dict = {}
    user_form = UserForm()
    user_profile_form = UserProfileForm()

    if request.method == "POST":
        user_form = UserForm(request.POST)
        user_profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid():
            user_form.save(commit=True)
            return redirect(reverse("rango:index"))

    context_dict["user_form"] = user_form
    context_dict["user_profile_form"] = user_profile_form
    return render(request, "rango/profile.html", context=context_dict)


def get_user(request):
    try:
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None
    return user


def get_user_profile(user):
    try:
        user_profile = UserProfile.objects.get(user_id=user.id)
    except UserProfile.DoesNotExist:
        user_profile = None
    return user_profile


def get_category(category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    return category
