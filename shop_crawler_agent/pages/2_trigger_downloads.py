from rapid_api_interface import fetch_countries, QuerystringLanguage
import logging
import streamlit as st


def get_countries():
    try:
        fetch_countries(QuerystringLanguage.en)
        fetch_countries(QuerystringLanguage.fr)
    except Exception as e:
        logging.error("app::get_countries", e)


download_all = st.button('Download All')


def get_categories():
    pass


if download_all:
    get_countries()
