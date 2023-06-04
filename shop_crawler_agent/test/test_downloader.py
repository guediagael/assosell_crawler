from unittest import TestCase
from unittest.mock import patch, MagicMock
from pymongo import MongoClient
from pymongo.database import Database
import json
from controllers import asos as asos_controllers
from typing import List

from rapid_api_interface import QuerystringLanguage
from downloader import _download_countries, _download_categories, _download_products, _download_product_details


class TestDownloader(TestCase):
    def setUp(self) -> None:
        self.db_client = MongoClient()
        self.db: Database = self.db_client.assosell_crawler_test
        asos_controllers.init(self.db)
        self.collections: List[str] = list()

        with open('../dummy_data/category_list_response.json', 'r') as categories_json_file:
            categories_json = json.load(categories_json_file)
            json_mock = MagicMock(return_value=categories_json)
            self.categories = MagicMock(json=json_mock)
            self.brands = categories_json['brands']
            self.navigation = categories_json['navigation']

        with open('../dummy_data/country_list_response.json', 'r') as countries_json_file:
            countries_json = json.load(countries_json_file)
            json_mock = MagicMock(return_value=countries_json)
            self.countries = MagicMock(json=json_mock)

        with open('../dummy_data/product_details_response.json', 'r') as product_details_json_file:
            product_details_json = json.load(product_details_json_file)
            self.product_details_id = product_details_json['id']
            json_mock = MagicMock(return_value=product_details_json)
            self.product_details = MagicMock(json=json_mock)

        with open('../dummy_data/product_list_response.json', 'r') as product_list_json_file:
            product_list_json = json.load(product_list_json_file)
            json_mock = MagicMock(return_value=product_list_json)
            self.product_list = MagicMock(json=json_mock)
            self.product_list_item_count = product_list_json['itemCount']

    def tearDown(self) -> None:
        for collection in self.collections:
            self.db[collection].drop()
        self.db_client.close()

    @patch("requests.request")
    def test_download_countries(self, mock_request):
        mock_request.return_value = self.countries
        self.collections.append('countries')
        self.assertTrue(_download_countries(), True)

    @patch("requests.request")
    def test_download_countries_duplicates(self, mock_request):
        mock_request.return_value = self.countries
        self.collections.append('countries')
        self.assertTrue(_download_countries(), True)
        self.assertTrue(_download_countries(), True)

    @patch("requests.request")
    def test_download_categories(self, mock_request):
        mock_request.return_value = self.categories
        self.collections.append("brands_fr")
        self.collections.append("brands_en")
        self.collections.append("navigation_fr")
        self.collections.append("navigation_en")
        self.assertTrue(_download_categories(), True)

    @patch("requests.request")
    def test_download_categories_updates(self, mock_request):
        mock_request.return_value = self.categories
        self.collections.append("brands_fr")
        self.collections.append("brands_en")
        self.collections.append("navigation_fr")
        self.collections.append("navigation_en")
        self.assertTrue(_download_categories(), True)
        self.assertTrue(_download_categories(), True)

    @patch("requests.request")
    def test_download_products(self, mock_request):
        mock_request.return_value = self.product_list
        self.collections.append("products_en")
        self.assertEqual(_download_products(1, QuerystringLanguage.en, offset=0),
                         (48, self.product_list_item_count - 48))
        self.collections.append("products_fr")
        self.assertEqual(_download_products(1, QuerystringLanguage.fr, offset=0),
                         (48, self.product_list_item_count - 48))

    @patch("requests.request")
    def test_download_products_update(self, mock_request):
        mock_request.return_value = self.product_list
        self.collections.append("products_en")
        next_offset_en, remaining_en = _download_products(1, QuerystringLanguage.en, offset=0)
        final_offset_en, remaining_en = _download_products(1, QuerystringLanguage.en, offset=next_offset_en)
        self.assertEqual((final_offset_en, remaining_en),
                         (48 * 2, self.product_list_item_count - (48 * 2)))

        self.collections.append("products_fr")

        next_offset, remaining = _download_products(1, QuerystringLanguage.fr, offset=0)
        final_offset, remaining = _download_products(1, QuerystringLanguage.fr, offset=next_offset)

        self.assertEqual((final_offset, remaining),
                         (48 * 2, self.product_list_item_count - (48 * 2)))

    @patch("requests.request")
    def test_download_product_details(self, mock_request):
        mock_request.return_value = self.product_details
        self.collections.append("product_details_en")
        self.assertTrue(_download_product_details(1, QuerystringLanguage.en), True)

        self.collections.append("product_details_fr")
        self.assertTrue(_download_product_details(1, QuerystringLanguage.fr), True)

    @patch("requests.request")
    def test_download_product_details_updates(self, mock_request):
        mock_request.return_value = self.product_details
        self.collections.append("product_details_en")
        details_downloaded = _download_product_details(1, QuerystringLanguage.en)
        details_updated = _download_product_details(1, QuerystringLanguage.en)
        self.assertTrue(details_downloaded, details_updated)
        products = self.db['product_details_en'].count_documents({"id": self.product_details_id})
        self.assertTrue(1, products)

        self.collections.append("product_details_fr")
        details_downloaded = _download_product_details(1, QuerystringLanguage.fr)
        details_updated = _download_product_details(1, QuerystringLanguage.fr)
        self.assertTrue(details_downloaded, details_updated)
        products = self.db['product_details_fr'].count_documents({"id": self.product_details_id})
        self.assertTrue(1, products)
