from rapid_api_interface import fetch_countries, QuerystringLanguage, fetch_categories
import logging
import streamlit as st


def get_countries():
    try:
        fetch_countries(QuerystringLanguage.en)
        fetch_countries(QuerystringLanguage.fr)
    except Exception as e:
        logging.error("app::get_countries", e)


download_categories = st.button('Download categories')
download_all = st.button('Download All')


def get_categories():
    '''
    :return: None, fetch cats from APIs sources
    '''
    fetch_categories(QuerystringLanguage.en)
    fetch_categories(QuerystringLanguage.fr)

if download_all:
    get_countries()
    get_categories()

if download_categories:
    get_categories()
