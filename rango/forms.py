from django import forms
from django.contrib.auth.models import User

from rango.models import Category, Page, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=Category.NAME_MAX_LENGTH, help_text="Please enter the category name."
    )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})


class PageForm(forms.ModelForm):
    title = forms.CharField(
        max_length=Page.TITLE_MAX_LENGTH,
        help_text="Please enter the title of the page.",
    )
    url = forms.URLField(
        max_length=Page.URL_MAX_LENGTH, help_text="Please enter the URL of the page."
    )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        exclude = ("category",)

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["url"].widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get("url")

        if url and not url.startswith("http://"):
            url = f"http://{url}"
            cleaned_data["url"] = url
        return cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(required=False)
    email = forms.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(
        max_length=Page.URL_MAX_LENGTH,
        help_text="Please enter the URL of your website:",
        required=False,
    )
    picture = forms.ImageField(required=False, help_text="Picture:")

    class Meta:
        model = UserProfile
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields["website"].widget.attrs.update({"class": "form-control"})
        self.fields["picture"].widget.attrs.update({"class": "form-control"})
