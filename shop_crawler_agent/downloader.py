from rapid_api_interface import fetch_countries, QuerystringLanguage, QuerystringCurrency, fetch_categories, \
    load_categories, fetch_product_list, fetch_product_details

from controllers import asos as asos_controller
import logging
from typing import List, Tuple, Dict
import copy

RELEVANT_BRANDS = ['ADIDAS', 'NIKE', "Reebok", 'Converse', "Vans", 'Crocs', "Puma", 'Fila', "New Balance", "Levi's",
                   'Diesel', 'Lacoste', 'Calvin Klein', 'Calvin Klein Jeans', "Quiksilver", 'ARMANI', 'ARMANI EXCHANGE',
                   'BOSS', "Tommy Hilfiger", 'Caterpillar', 'Ray-Ban', "The North Face", "Timberland", 'BERSHKA',
                   'ellesse', 'Emporio Armani', "O'Neill", 'Champion', "Under Armour", "Wrangler", 'HUGO']


def _download_countries():
    try:
        countries_fr_downloaded = fetch_countries(QuerystringLanguage.en)
        countries_en_downloaded = fetch_countries(QuerystringLanguage.fr)
        return countries_fr_downloaded and countries_en_downloaded
    except Exception as e:
        logging.error("app::get_countries", e)


def _download_categories():
    """
    :return: None, fetch cats from APIs sources
    """
    categories_downloaded_en = fetch_categories(QuerystringLanguage.en)
    categories_downloaded_fr = fetch_categories(QuerystringLanguage.fr)
    return categories_downloaded_en and categories_downloaded_fr


def _load_brands(language: QuerystringLanguage) -> Dict[int, str]:
    """
    :param language: The language in the database to return categories from
    :return: A tuple containing the navigation list and the brands list
    """
    nav_list, brand_list = load_categories(language)

    lookout_brands = [b.lower() for b in RELEVANT_BRANDS[:15]]

    # brands = [{"id": b.id, 'name': b.content.title,
    #            'children': [{'id': subbrand.link.categoryId, 'name': subbrand.content.title} for subbrand in
    #                         b.children]} for b in
    #           brand_list]
    result = dict()
    for brand in brand_list:
        for child in brand.children:
            if child.content.title.lower() in lookout_brands:
                result[child.link.categoryId] = child.content.title

    return result


def _download_products(category_id: int, language: QuerystringLanguage, offset):
    if language == QuerystringLanguage.en:
        currency = QuerystringCurrency.USD
    else:
        currency = QuerystringCurrency.EUR
    item_count, result_count = fetch_product_list(currency, language, category_id, offset)
    if item_count:
        next_offset = result_count + offset
        remaining = item_count - next_offset
        return next_offset, remaining
    return 0, 0


def _download_product_details(product_id: int, language: QuerystringLanguage):
    return fetch_product_details(product_id, language)


def _check_product_exist_in_different_language(product_id: int, language_check: QuerystringLanguage,
                                               language_existing: QuerystringLanguage) -> bool:
    language_to_load = asos_controller.Language.french if language_existing == QuerystringLanguage.fr \
        else asos_controller.Language.english

    language_to_check = language_check.value
    language_to_add = asos_controller.Language.french \
        if language_to_check == QuerystringLanguage.fr \
        else asos_controller.Language.english

    try:
        product_details = asos_controller.get_product_details(language_to_load, product_id)
        if product_details is not None and product_details.alternateNames is not None:
            for name in product_details.alternateNames:
                if name.locale == language_to_check:
                    translated_item = copy.deepcopy(product_details)
                    translated_item.name = name.title
                    return asos_controller.add_product_details(translated_item.dict(), language_to_add)
    except Exception as e:
        logging.error("crawler_agent::_check_product_exist_in_different_language:: ", e)
        return False
    return False


def start_download_job():
    _download_countries()
    _download_categories()

    brands = _load_brands(QuerystringLanguage.fr) | _load_brands(QuerystringLanguage.en)

    next_offset_en = 0
    remaining_en = True  # could be any number higher than 0

    next_offset_fr = 0
    remaining_fr = True  # could be any number higher  than 0

    for brand in brands.keys():
        while remaining_en is not None and remaining_en is True:
            next_offset, remaining = _download_products(brand, QuerystringLanguage.en, next_offset_en)
            remaining_en = remaining > 0
            next_offset_en = next_offset

        while remaining_fr is not None and remaining_fr is True:
            next_offset, remaining = _download_products(brand, QuerystringLanguage.en, next_offset_fr)
            next_offset_fr = next_offset
            remaining_fr = remaining > 0

    downloading_product_fr = True
    page = 0
    while downloading_product_fr:
        items = asos_controller.get_items(asos_controller.Language.french, limit=48, page=page)
        if items and len(items) > 0:
            for item in items:
                _download_product_details(item.id, QuerystringLanguage.fr)
                page += 1
        else:
            downloading_product_fr = False
            page = 0

    downloading_product_en = True
    while downloading_product_en:
        items = asos_controller.get_items(asos_controller.Language.english, limit=48, page=page)
        if items and len(items) > 0:
            for item in items:
                if not _check_product_exist_in_different_language(product_id=item.id,
                                                                  language_check=QuerystringLanguage.en,
                                                                  language_existing=QuerystringLanguage.fr):
                    _download_product_details(item.id, QuerystringLanguage.en)
                    page += 1
        else:
            downloading_product_en = False
            page = 0


if __name__ == '__main__':
    from pymongo import MongoClient

    db = MongoClient()
    asos_controller.init(db.assosell_crawler)
