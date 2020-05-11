from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from registration.backends.simple.views import RegistrationView

from rango.bing_search import run_query
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.helpers import (
    get_category,
    get_category_list,
    get_or_create_user_profile,
    get_user,
    get_user_profile,
)
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
            page.last_visit = timezone.now()
            page.save()
            return redirect(page.url)

    return redirect(reverse("rango:index"))


class RegisterProfileView(View):
    class_form = UserProfileForm
    template_name = "rango/profile_registration.html"

    def get_user_and_profile(self, request):
        user = request.user
        user_profile = get_user_profile(user)
        return user, user_profile

    def get(self, request):
        user, user_profile = self.get_user_and_profile(request)
        # if cant find user or user already has a profile
        if user is None or user_profile:
            return redirect(reverse("rango:index"))

        form = self.class_form()

        return render(request, self.template_name, {"form": form})

    def post(self, request):
        user, user_profile = self.get_user_and_profile(request)
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


class ProfileView(View):
    class_form = UserProfileForm
    template_name = "rango/profile.html"

    def get(self, request, username):
        user = get_user(username)
        if not user:
            return redirect(reverse("rango:index"))

        user_profile = get_or_create_user_profile(user)

        form = self.class_form(
            initial={"website": user_profile.website, "picture": user_profile.picture}
        )

        context_dict = {
            "user": request.user,
            "selected_user": user,
            "user_profile": user_profile,
            "form": form,
        }

        return render(request, self.template_name, context=context_dict)

    def post(self, request, username):
        user = get_user(username)
        if not user or not request.user == user:
            return redirect(reverse("rango:index"))

        user_profile = get_user_profile(user)

        form = self.class_form(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
        else:
            print(form.errors)

        context_dict = {
            "user": request.user,
            "selected_user": user,
            "user_profile": user_profile,
            "form": form,
        }

        return render(request, self.template_name, context=context_dict)


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse("rango:register_profile")


class ProfileListView(View):
    template_name = "rango/list_profiles.html"

    def get(self, request):
        profile_list = UserProfile.objects.all()
        return render(
            request, self.template_name, context={"user_profile_list": profile_list}
        )


class LikeCategoryView(View):
    def get(self, request):
        category_id = request.GET["category_id"]

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes += 1
        category.save()

        return HttpResponse(category.likes)


class CategorySuggestionView(View):
    def get(self, request):
        if "suggestion" in request.GET:
            suggestion = request.GET["suggestion"]
        else:
            suggestion = ""

        category_list = get_category_list(max_results=8, starts_with=suggestion)

        if len(category_list) == 0:
            category_list = Category.objects.order_by("-likes")

        return render(request, "rango/categories.html", {"categories": category_list})


class SearchAddPageView(View):
    def get(self, request):
        category_id = request.GET["category_id"]
        page_title = request.GET["page_title"]
        page_url = request.GET["page_url"]

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return HttpResponse("Error - invalid category")

        Page.objects.get_or_create(category=category, title=page_title, url=page_url)

        pages = Page.objects.order_by("-views").filter(category=category)

        return render(request, "rango/list_pages.html", {"pages": pages})
