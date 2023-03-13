from typing import List

import streamlit as st
from PIL import Image
from rapid_api_interface import QuerystringLanguage, QuerystringCurrency, QueryStringCountry, fetch_product_details
from controllers import asos as asos_controller
from external_models import asos as asos_model
import urllib.request

selected_language = st.radio("Select language", ('Fr', 'En'))

if selected_language == 'Fr':
    lang = QuerystringLanguage.fr
else:
    lang = QuerystringLanguage.en


def load_first_10_products() -> List[asos_model.Product]:
    language = asos_controller.Language.french if lang == QuerystringLanguage.fr \
        else asos_controller.Language.english
    # st.text(f'selected language {selected_language} and language is {language.value}')
    return asos_controller.get_items(language=language, limit=10)


def load_products_details(product_id) -> dict:
    language = asos_controller.Language.french if lang == QuerystringLanguage.fr \
        else asos_controller.Language.english
    product_details = asos_controller.get_product_details(language, product_id)
    return {'images': [i.url for i in product_details.media.images], 'gender': product_details.gender,
            "price": product_details.price.current.value, "price_currency": product_details.price.currency,
            "variants": [{"color": var.colour, "size": var.brandSize} for var in product_details.variants]}


def set_images(urls: List[str]):
    cols = st.columns(len(urls))
    for col in range(0, len(cols)):
        urllib.request.urlretrieve(f'https://{urls[col]}', f'asos_img_{col}')
        img = Image.open(f'asos_img_{col}')
        cols[col].image(img, caption=f'Image {col + 1}')


products = load_first_10_products()

if products and len(products) > 0:
    choices = [{'name': p.name, 'brand': p.brandName, 'id': p.id} for p in products]
    options = [c['name'] for c in choices]
    selected_option = st.selectbox("select and item to fetch details for:", options)

if st.button("fetch"):
    prod_id = None
    if selected_option:
        for choice in choices:
            if choice['name'] == selected_option:
                downloaded = fetch_product_details(choice['id'], lang)
                if downloaded:
                    st.text(f"downloaded details for {choice}")
                    downloaded_details = load_products_details(choice['id'])
                    set_images(downloaded_details['images'])
                    st.text(f"Gender: {downloaded_details['gender']}")
                    st.text(f"Price: {downloaded_details['price']} {downloaded_details['price_currency']}")
                    st.text(f"Variants: {downloaded_details['variants']}")
                    break
                else:
                    st.text(f"Can't download details for {choice}")
                    break
    else:
        st.text("not option selected")
