from django.test import TestCase

from rango.views import AddCategoryView, IndexView, ShowCategoryView


class ShowCategoryViewStubTests(TestCase):
    def test_category_view_with_category_and_page_returned_stub(self):
        """
        If category exists with pages, then both should be displayed in the response.
        """
        showCategoryView = ShowCategoryView()
        ShowCategoryView.get_category = lambda self, slug_name: StubCategory(
            1, "Test Category", "test-category"
        )
        ShowCategoryView.get_pages = lambda self, category: [
            StubPage(1, "Test Page", "http://www.test.com/", 1)
        ]

        response = showCategoryView.get({}, "test")

        self.assertContains(response, "Test Category")
        self.assertContains(response, "Test Page")

    def test_category_view_with_stub_invalid_category(self):
        """
        If no categories exist, the appropriate message should be displayed.
        """
        showCategoryView = ShowCategoryView()
        ShowCategoryView.get_category = lambda self, slug_name: None
        ShowCategoryView.get_pages = lambda self, category: []

        response = showCategoryView.get({}, "test")

        self.assertContains(response, "The specified category does not exist.")


class CategoryViewFakeTests(TestCase):
    class FakeCategories:
        def __init__(self):
            self.categories = []

        def add(self, category):
            self.categories.append(category)

        def get(self):
            return self.categories[:]  # return a copy of category instead of original

        def remove(self, category):
            self.categories.remove(category)

        def clear(self):
            self.categories = []

        def get_category(self, category_slug_name):
            for category in self.categories:
                if category.slug == category_slug_name:
                    return category
            return None

    class FakePages:
        def __init__(self):
            self.pages = []

        def add_page(self, page):
            self.pages.append(page)

        def get_pages(self, category):
            pages = []
            for page in self.pages:
                if page.category == category:
                    pages.append(page)
            return pages

    # Create Fake Categories

    fakeCategories = FakeCategories()
    fakePages = FakePages()

    def test_can_add_new_category(self):
        """
        If category exists with pages, then both should be displayed in the response.
        """
        addCategoryView = AddCategoryView()
        addCategoryView.add_category = self.add_category

        addCategoryView.post(Request("test"))

        self.assertTrue(len(self.fakeCategories.get()), 1)

    def test_can_retrieve_added_cateogry(self):
        """
        Can retrive a category after it has been added.
        """
        addCategoryView = AddCategoryView()
        addCategoryView.add_category = self.add_category

        addCategoryView.post(Request("test"))

        showCategoryView = ShowCategoryView()
        ShowCategoryView.get_category = self.get_category
        ShowCategoryView.get_pages = self.get_pages

        response = showCategoryView.get({}, "test-category")

        self.assertContains(response, "Test Category")

    # helper functions
    def add_category(self, request):
        self.fakeCategories.add(StubCategory(1, "Test Category", "test-category"))
        return True

    def get_category(self, category_slug_name):
        return self.fakeCategories.get_category(category_slug_name)

    def get_pages(self, category):
        return self.fakePages.get_pages(category)


class StubCategory:
    def __init__(self, id, name, slug, views=0, likes=0):
        self.id = id
        self.name = name
        self.slug = slug
        self.views = views
        self.likes = likes


class StubPage:
    def __init__(self, id, title, url, category, views=0):
        self.id = id
        self.title = title
        self.url = url
        self.category = category
        self.views = views


class Request:
    def __init__(self, META):
        self.META = {}
