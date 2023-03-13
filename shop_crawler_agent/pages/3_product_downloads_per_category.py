from rapid_api_interface import QuerystringLanguage, load_categories, fetch_product_list, QuerystringCurrency
import logging
import streamlit as st
from typing import List, Tuple
from external_models import asos as asos_models

selected_language = st.radio("Select Language", ('Fr', 'EN'))


def show_categories(language: QuerystringLanguage) -> Tuple[List, List]:
    '''
    :param language: The language in the database to return categories from
    :return: A tuple containing the navigation list and the brands list
    '''
    nav_list, brand_list = load_categories(language)
    # navs = [
    #     {'id': n.id, 'name': n.alias,
    #      'children': [{'id': subcat.id, 'name': subcat.content.title} for subcat in n.children]}
    #     for n in nav_list]
    brands = [{"id": b.id, 'name': b.content.title,
               'children': [{'id': subbrand.link.categoryId, 'name': subbrand.content.title} for subbrand in
                            b.children]} for b in
              brand_list]
    return brands


if selected_language == 'Fr':
    lang = QuerystringLanguage.fr
else:
    lang = QuerystringLanguage.en

brands = show_categories(lang)

expander = st.expander("Chose Category below:")
selection = expander.selectbox('Brands', [b['name'] for b in brands])
options = []
for b in brands:
    if b['name'] == selection:
        options.extend([c['name'] for c in b['children']])
brand_selection = expander.radio(selection, options)
for b in brands:
    if b['name'] == selection:
        for bc in b['children']:
            if bc['name'] == brand_selection:
                cat_id = bc['id']
                break


def get_products(category_id: str, language: QuerystringLanguage, offset):
    if language == QuerystringLanguage.en:
        currency = QuerystringCurrency.USD
    else:
        currency = QuerystringCurrency.EUR
    item_count, result_count = fetch_product_list(currency, language, category_id, offset)
    if item_count:
        next_offset = result_count + offset
        remaining = item_count - offset
        return next_offset, remaining
    return None, None


def trigger_load(cat: str):
    key = f'products_cat_pointer_{cat}'
    if key in st.session_state:
        offset = st.session_state[key]
    else:
        offset = 0
    next_offset, remaining_count = get_products(cat, lang, offset)
    st.session_state[key] = next_offset
    return remaining_count


if st.button('Load'):
    if cat_id is not None:
        remaining_items = trigger_load(cat_id)
        st.text(f"There's {remaining_items} samples for the selected cat")
    else:
        st.text("No cat selected")
