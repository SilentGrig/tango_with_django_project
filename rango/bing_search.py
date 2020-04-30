import json

import requests


def read_bing_key():
    """
    Reads the BING API key from a file called 'bing.key'
    returns: a string which is either None, i.e. no key found or with a key
    """

    bing_api_key = None
    try:
        with open("bing.key", "r") as f:
            bing_api_key = f.readline().strip()
    except IOError:
        try:
            with open(".../bing.key", "r") as f:
                bing_api_key = f.readline().strip()
        except IOError:
            raise IOError("bing.key file not found")

    if not bing_api_key:
        raise KeyError("Bing key not found")

    return bing_api_key


def run_query(search_terms):
    """
    See Microsoft's documentation on other parameters that you can set.
    http://bit.ly/twd-bing-api
    """
    bing_key = read_bing_key()
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": bing_key}
    params = {"q": search_terms, "textDecorations": True, "textForm": "HTML"}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    results = []
    for result in search_results["webPages"]["value"]:
        results.append(
            {
                "title": result["name"],
                "link": result["url"],
                "summary": result["snippet"],
            }
        )
    return results


def main():
    search_terms = input("Please enter search term: ")
    search_results = run_query(search_terms)
    print(search_results)


if __name__ == "__main__":
    main()
