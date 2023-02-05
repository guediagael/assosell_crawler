import requests
from controllers import asos as asos_controller
from enum import Enum

HEADERS = {
    'X-RapidAPI-Key': 'a5011b9a09msh55296d35961e1b9p114a63jsn96497fd694a5',
    'X-RapidAPI-Host': 'asos2.p.rapidapi.com'
}

ROOT_URL = "https://asos2.p.rapidapi.com"


class QuerystringLanguage(Enum):
    fr = 'fr-FR'
    en = 'en-US'


class QueryStringCountry(Enum):
    france = 'FR'
    canada = 'US'


class QuerystringCurrency(Enum):
    # CAD = 'CAD'
    EUR = 'EUR'
    USD = 'USD'


def get_controller_language(query_string: QuerystringLanguage) -> asos_controller.Language:
    if query_string == QuerystringLanguage.fr:
        return asos_controller.Language.french
    elif query_string == QuerystringLanguage.en:
        return asos_controller.Language.english
    raise ValueError(f"Unknown language {query_string}")


def fetch_countries(language: QuerystringLanguage):
    querystring = {"lang": language.value}
    controller_language = get_controller_language(language)
    url = f'{ROOT_URL}/countries/list'
    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    country_list = response.json()
    return asos_controller.add_countries(country_list, controller_language)


def fetch_categories(store: QueryStringCountry, language: QuerystringLanguage):
    querystring = {'lang': language.value, 'country': store.value}
    controller_language = get_controller_language(language)
    url = f'{ROOT_URL}/categories/list'
    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    category_response = response.json()
    navigation_categories = category_response['navigation']
    brand_categories = category_response['brands']
    navigation_added = asos_controller.add_navigation_categories(controller_language, navigation_categories)
    brands_added = asos_controller.add_brands_categories(controller_language, brand_categories)
    return navigation_added and brands_added


def fetch_product_list(store: QueryStringCountry, currency: QuerystringCurrency, language: QuerystringLanguage,
                       category_id: str):
    offset = 0
    querystring = {'lang': language.value, 'country': store.value, "store": store.value, "currency": currency,
                   "categoryId": category_id, 'offset': offset, 'limit': 100, "sort": "freshness", "sizeSchema": "US"}

    url = f"{ROOT_URL}/products/v2/list"

    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    #TODO: the currency and sizeschema must match ( I think shoud match the store as well). Check if the params get be taken based on the provided category id


