import logging
from typing import List, Dict, Tuple, Optional

import requests
from controllers import asos as asos_controller
from external_models import asos as asos_models
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


def fetch_categories(language: QuerystringLanguage):
    if language == QuerystringLanguage.fr:
        store = QueryStringCountry.france
    else:
        store = QueryStringCountry.canada
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


def fetch_product_list(currency: QuerystringCurrency, language: QuerystringLanguage,
                       category_id: int, offset=0) -> Tuple[Optional[int], Optional[int]]:
    '''
    :param currency:
    :param language: The store will be derived from the chosen language. Fr-FR will query the french store and en-US will query canda store
    :param category_id:
    :param offset: use for pagination. Number of items to skip
    :return: the number of available items left to be downloaded
    '''
    try:
        if language == QuerystringLanguage.fr:
            store = QueryStringCountry.france
        else:
            store = QueryStringCountry.canada
        querystring = {'lang': language.value, 'country': store.value, "store": store.value, "currency": currency.value,
                       "categoryId": category_id, 'offset': offset, 'limit': 48, "sort": "freshness",
                       "sizeSchema": "US"}

        url = f"{ROOT_URL}/products/v2/list"
        try:
            response = requests.request("GET", url, headers=HEADERS, params=querystring)
            if response.ok:
                controller_language = get_controller_language(language)
                product_list_response = response.json()
                if product_list_response:
                    added_categories = asos_controller.add_product_categories(product_list_response,
                                                                              controller_language)
                    added = asos_controller.add_products(product_list_response, controller_language)
                    if added:
                        product_list = product_list_response
                        return product_list['itemCount'], len(product_list['products'])
                else:
                    logging.error(f"no response from rapid api {querystring}", response.json())
                    return None, None
            else:
                logging.error(f"rapid api response error: {response.request}", response.reason)
                return None, None
        except Exception as e:
            logging.error(f"url: {url}, query:{querystring}", e)
            return None, None
    except Exception as appException:
        logging.error(f"something wrong happened", appException)
        return None, None


def fetch_products_on_sale():
    pass


def fetch_product_details(product_id: int, language: QuerystringLanguage):
    if language == QuerystringLanguage.fr:
        store = QueryStringCountry.france
        currency = QuerystringCurrency.EUR
    else:
        store = QueryStringCountry.canada
        currency = QuerystringCurrency.USD
    url = f'{ROOT_URL}/products/v3/detail'
    query_string = {"id": product_id, "lang": language.value, "store": store.value, "currency": currency.value}

    response = requests.request("GET", url, headers=HEADERS, params=query_string)

    added = asos_controller.add_product_details(response.json(), get_controller_language(language))

    return added


def load_categories(language: QuerystringLanguage) -> Tuple[
    List[asos_models.NavigationList], List[asos_models.BrandList]]:
    categories = asos_controller.get_categories(get_controller_language(language))

    return categories.navigation, categories.brands
