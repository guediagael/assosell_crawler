from typing import List

from controllers import asos as asos_controllers
from external_models import asos as asos_models

import unittest
from pymongo import MongoClient
import json


class TestAsosController(unittest.TestCase):
    def setUp(self) -> None:
        self.db_client = MongoClient()
        self.db = self.db_client.assosell_crawler_test
        asos_controllers.init(self.db)
        self.collections: List[str] = list()

        with open('../dummy_data/category_list_response.json', 'r') as categories_json_file:
            categories_json = json.load(categories_json_file)
            # categories_response_template = asos_models.CategoriesResponse(**categories_json)
            self.brands = categories_json['brands']
            self.navigation = categories_json['navigation']

        with open('../dummy_data/country_list_response.json', 'r') as countries_json_file:
            countries_json = json.load(countries_json_file)
            self.countries = countries_json

        with open('../dummy_data/product_details_response.json', 'r') as product_details_json_file:
            product_details_json = json.load(product_details_json_file)
            self.product_details = product_details_json

        with open('../dummy_data/product_list_response.json', 'r') as product_list_json_file:
            product_list_json = json.load(product_list_json_file)
            self.product_list = product_list_json

    def test_add_countries(self):
        self.collections.append('countries')
        self.assertTrue(asos_controllers.add_countries(self.countries, asos_controllers.Language.english))

    def test_add_navigation_categories(self):
        self.collections.append(f'navigations_{asos_controllers.Language.english.value}')
        self.assertTrue(asos_controllers.add_navigation_categories(asos_controllers.Language.english, self.navigation))

    def test_add_brands_categories(self):
        self.collections.append(f'brands_{asos_controllers.Language.english.value}')
        self.assertTrue(asos_controllers.add_brands_categories(asos_controllers.Language.english, self.brands))

    def test_add_products(self):
        self.collections.append(f'products_{asos_controllers.Language.english.value}')
        self.assertTrue(
            asos_controllers.add_products(products=self.product_list, language=asos_controllers.Language.english))

    def test_add_product_details(self):
        self.collections.append(f'product_details_{asos_controllers.Language.english.value}')
        self.assertTrue(asos_controllers.add_product_details(self.product_details, asos_controllers.Language.english))

    def tearDown(self) -> None:
        for collection in self.collections:
            self.db[collection].drop()
        self.db_client.close()
