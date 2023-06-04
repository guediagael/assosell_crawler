from typing import Union

from asos_mappers import asos_item_details_to_assosell_item_details, asos_list_item_to_assosell_list_item, \
    asos_brand_category_to_assosell_brand_category

__ASOS_ID__ = 1

from external_models import BrandListItem, Product, ProductDetailsResponse


def _map_from_asos_gender(asos_gender: str) -> str:
    if asos_gender == 'Women':
        return 'W'
    if asos_gender == 'Men':
        return 'M'
    if asos_gender == 'Unisex':
        return 'U'


def _map_to_asos_gender(assosell_gender: str) -> str:
    if assosell_gender == 'W':
        return 'Women'
    if assosell_gender == 'M':
        return 'Men'
    if assosell_gender == 'U':
        return 'Unisex'


def map_asos_brand_category_to_assosell_brand_category(source_id: int, brand_list_item: Union[BrandListItem]) -> dict:
    result = asos_brand_category_to_assosell_brand_category(brand_list_item)
    result['source_id'] = __ASOS_ID__
    return result


def map_asos_list_item_to_assosell_list_item(product: Union[Product]) -> dict:
    result = asos_list_item_to_assosell_list_item(product)
    result['tag'] = result['gender_at_source']
    result['source_id'] = __ASOS_ID__
    return result


def map_asos_product_detail_to_assosell_product_details(product_details: ProductDetailsResponse) -> dict:
    result = asos_item_details_to_assosell_item_details(product_details)
    result['gender'] = _map_from_asos_gender(result['gender_at_source'])
    result['source_id'] = __ASOS_ID__
    return result
