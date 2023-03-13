from typing import List
from external_models import asos as asos_models
from pymongo import MongoClient
from enum import Enum

db: MongoClient


class Language(Enum):
    french = 'fr'
    english = 'en'


def init(database: MongoClient):
    global db
    db = database


def get_languages() -> List[asos_models.Language]:
    return [asos_models.Language(**language) for language in db.languages]


def get_currencies() -> List[asos_models.Currency]:
    return [asos_models.Currency(**currency) for currency in db.currencies.find()]


def get_countries() -> List[asos_models.CountryListItem]:
    return [asos_models.CountryListItem(**country) for country in db.countries.find()]


def get_size_schemas(country: str) -> List[asos_models.SizeSchema]:
    countries = db.countries.find({'country': country})
    cntry = asos_models.CountryListItem(**countries)
    return cntry.sizeSchemas


def get_categories(language: Language) -> asos_models.CategoriesResponse:
    cat_response_navigation = [asos_models.NavigationList(**nl) for nl in db[f'navigations_{language.value}'].find()]
    cat_response_brands = [asos_models.BrandList(**br) for br in db[f'brands_{language.value}'].find()]
    cat_response = {'brands': cat_response_brands, 'navigation': cat_response_navigation}
    # cat_response = asos_models.CategoriesResponse()

    # cat_response.navigation = [asos_models.NavigationList(**nl) for nl in db[f'navigations_{language.value}'].find()]
    # cat_response.brands = [asos_models.NavigationList(**br) for br in db[f'brands_{language.value}'].find()]
    return asos_models.CategoriesResponse(** cat_response)


def get_items(language: Language, brand_name: str = None, category: str = None, country: str = None, size_schema: str = None,
              color: str = None, page: int = 0, limit: int = 100) -> List[asos_models.Product]:
    filters = dict()
    if brand_name:
        filters['brandName'] = brand_name
    if color:
        filters['colour'] = color
    print(f"loading product from products_{language.value}")
    return [asos_models.Product(**product) for product in
            db[f'products_{language.value}'].find(filters).skip(page * limit)]


def get_product(language: Language, product_id: str) -> asos_models.Product:
    return asos_models.Product(**db[f'products_{language.value}'].find_one({'id': product_id}))


def get_product_details(language: Language, product_id: str) -> asos_models.ProductDetailsResponse:
    return asos_models.ProductDetailsResponse(**db[f'product_details_{language.value}'].find_one({'id': product_id}))


def add_products(products: dict, language: Language) -> bool:
    product_list_response = asos_models.ProductListResponse(**products)
    products = product_list_response.products
    added = False
    if products and len(products) > 0:
        added = db[f'products_{language.value}'].insert_many(
            [product.dict() for product in product_list_response.products])

    return added


def add_product_details(product_details_response: dict, language: Language) -> bool:
    product_details = asos_models.ProductDetailsResponse(**product_details_response)
    added = False
    if product_details:
        added = db[f'product_details_{language.value}'].insert_one(product_details.dict())
    return added


def add_countries(countries_response: dict, language: Language) -> bool:
    country_list_response: List[asos_models.CountryListItem] = [asos_models.CountryListItem(**country) for country in
                                                                countries_response]
    added = False
    if country_list_response and len(country_list_response) > 0:
        added = db[f'countries_{language.value}'].insert_many([country.dict() for country in country_list_response])

    return added


def add_navigation_categories(language: Language, navigation_categories: List) -> bool:
    categories: List[asos_models.NavigationList] = [asos_models.NavigationList(**cat) for cat in navigation_categories]
    added = False
    if categories and len(categories) > 0:
        added = db[f'navigations_{language.value}'].insert_many([category.dict() for category in categories])
    return added


def add_brands_categories(language: Language, brand_categories: List) -> bool:
    categories: List[asos_models.BrandList] = [asos_models.BrandList(**cat) for cat in brand_categories]

    added = False
    if categories and len(categories) > 0:
        added = db[f'brands_{language.value}'].insert_many([category.dict() for category in categories])

    return added
