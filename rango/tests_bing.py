from unittest.mock import patch

from django.test import TestCase

from rango.views import ShowCategoryView


class BingSearchTests(TestCase):
    @patch(
        "rango.views.run_query",
        return_value=["Bing Result 1", "Big Result 2", "Big Result 3"],
    )
    def test_bing_call_with_mock_returning_results(self, mock_bing_call):
        categoryView = ShowCategoryView()
        categoryView.search(Request("POST", Post()))
        # self.assertEqual(mock_bing_call.call_count, 1)
        self.assertEqual(
            categoryView.result_list, ["Bing Result 1", "Big Result 2", "Big Result 3"]
        )

    @patch("rango.views.run_query", return_value=[])
    def test_bing_call_with_mock_returning_empty_list(self, mock_bing_call):
        categoryView = ShowCategoryView()
        categoryView.search(Request("POST", Post()))
        # self.assertEqual(mock_bing_call.call_count, 1)
        self.assertEqual(categoryView.result_list, [])

    def test_with_stub(self):
        categoryView = ShowCategoryView()
        categoryView.search(Request("POST", Post()), TESTING=True)
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
