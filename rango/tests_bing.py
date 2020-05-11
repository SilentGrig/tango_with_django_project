from unittest.mock import patch

from django.test import TestCase

from rango.views import ShowCategoryView


class MyTests(TestCase):
    @patch("rango.views.run_query", return_value=["test"])
    def test_with_mock(self, mock_bing_call):
        categoryView = ShowCategoryView()
        categoryView.search(Request("POST", Post()))
        # self.assertEqual(mock_bing_call.call_count, 1)
        self.assertEqual(categoryView.result_list, ["test"])

    def test_with_stub(self):
        categoryView = ShowCategoryView()
        categoryView.search(Request("POST", Post()), True)
        self.assertEqual(categoryView.result_list, ["first result", "second result"])


class Request:
    def __init__(self, method, POST):
        self.method = method
        self.POST = POST


class Post:
    def __init__(self):
        self.query = "test"

    def get(self, query):
        return self.query
