from django.test import TestCase

from rango.views import IndexView, ShowCategoryView


class ShowCategoryViewTests(TestCase):
    def test_category_view_with_stub(self):
        """
        If no categories exist, the appropriate message should be displayed.
        """
        showCategoryView = ShowCategoryView()
        ShowCategoryView.get_category = lambda slug_name: FakeCategory(
            1, "Test Category", "test-category"
        )
        ShowCategoryView.get_pages = lambda category: [
            FakePage(1, "test", "http://www.test.com/", 1)
        ]

        response = showCategoryView.get({}, "test")

        self.assertContains(response, "Test Category")

    # def test_index_view_with_categories(self):
    #     """
    #     Checks whether categories are displayed correctly when present
    #     """
    #     add_category("Python", 1, 1)
    #     add_category("C++", 1, 1)
    #     add_category("Erlang", 1, 1)

    #     response = self.client.get(reverse("rango:index"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Python")
    #     self.assertContains(response, "C++")
    #     self.assertContains(response, "Erlang")

    #     num_categories = len(response.context["categories"])
    #     self.assertEquals(num_categories, 3)


class FakeCategory:
    def __init__(self, id, name, slug, views=0, likes=0):
        self.id = id
        self.name = name
        self.slug = slug
        self.views = views
        self.likes = likes


class FakePage:
    def __init__(self, id, title, url, category, views=0):
        self.id = id
        self.title = title
        self.url = url
        self.category = category
        self.views = views
