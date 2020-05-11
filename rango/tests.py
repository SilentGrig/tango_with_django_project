from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rango.models import Category, Page


class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
    Ensures the number of views recevied from a Category are positive or zero.
    """
        category = add_category(name="test", views=-1, likes=0)

        self.assertEqual((category.views >= 0), True)

    def test_slug_line_creation(self):
        """
    Checks to make sure that when a category is created, an
    appropraite slug is created.
    Example: "Rangom Category String" should be "random-category-string".
    """
        category = add_category(name="Random Category String")

        self.assertEqual(category.slug, "random-category-string")


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        """
    If no categories exist, the appropriate message should be displayed.
    """
        response = self.client.get(reverse("rango:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context["categories"], [])

    def test_index_view_with_categories(self):
        """
    Checks whether categories are displayed correctly when present
    """
        add_category("Python", 1, 1)
        add_category("C++", 1, 1)
        add_category("Erlang", 1, 1)

        response = self.client.get(reverse("rango:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")
        self.assertContains(response, "C++")
        self.assertContains(response, "Erlang")

        num_categories = len(response.context["categories"])
        self.assertEquals(num_categories, 3)


class PageAccessTests(TestCase):
    def test_page_last_visit_date_not_in_future(self):
        """
    Checks to ensure that the last_visit date isn't in the future
    """
        category = add_category("JavaScript", 1, 1)
        page = add_page(category, "NodeJS", "https://nodejs.org/en/")

        self.assertTrue(page.last_visit < timezone.now())

    def test_page_list_visit_is_updated(self):
        """
    Checks that a page's last visit date is updated when viewed
    """
        category = add_category("Games", 1, 1)
        page = add_page(
            category,
            "Data-Oriented Design",
            "https://www.dataorienteddesign.com/dodbook/",
        )
        created_date = page.last_visit

        self.client.get(reverse("rango:goto", kwargs={"page_id": page.id}))

        page.refresh_from_db()

        self.assertTrue(page.last_visit > created_date)


def add_category(name, views=0, likes=0):
    category = Category.objects.get_or_create(name=name)[0]
    category.views = views
    category.likes = likes

    category.save()
    return category


def add_page(category, title, url):
    return Page.objects.get_or_create(category=category, title=title, url=url)[0]
