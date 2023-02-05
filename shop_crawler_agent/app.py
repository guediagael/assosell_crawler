from pymongo import MongoClient
from controllers import asos
from rapid_api_interface import fetch_countries, QuerystringLanguage
import logging
import streamlit as st

db = MongoClient()

asos.init(db.assosell_crawler)


def get_current_index():
    if st.session_state.lang == 'fr-FR':
        return 1
    elif st.session_state.lang == 'en-EN':
        return 2
    return 0


if 'lang' not in st.session_state:
    st.session_state.lang = 'both'
    global current_index

selected_language = st.radio('lang', ('both', 'fr-FR', 'en-EN'), index=get_current_index(), horizontal=True)

st.session_state['lang'] = selected_language

# if __name__ == '__main__':
#     get_countries()
