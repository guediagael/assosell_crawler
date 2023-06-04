import logging

from controllers import asos as asos_controller
from typing import List, Dict, Tuple
from external_models import asos
import random
from psycopg2 import connect, DatabaseError
from datetime import datetime

pg_conn: None


def _split_list_into_chunks(chunk_size: int, elements: list):
    for el in range(0, len(elements), chunk_size):
        yield elements[el: el + chunk_size]


def init():
    from pymongo import MongoClient

    db = MongoClient()
    asos_controller.init(db.assosell_crawler)

    global pg_conn
    pg_conn = connect(database="jpkhwxyj",
                      host="balarama.db.elephantsql.com",
                      user="jpkhwxyj",
                      password="7KNdbWexZRvb1zirlQ9pIkGMihqfFjN0")

    user_name = "assosell"
    password = "4ss0se11"
    full_name = "Assosell Vendor"
    address = "We're online only"
    update_source_in_house_vendor = """INSERT INTO web.user (username, password, full_name, address) 
    VALUES (%s, %s, %s, %s) 
    ON CONFLICT (username) 
    DO UPDATE SET password = excluded.password, full_name = excluded.full_name, address = excluded.address"""
    sql_cursor = pg_conn.cursor()
    sql_cursor.execute(update_source_in_house_vendor, (user_name, password, full_name, address))
    pg_conn.commit()
    sql_cursor.close()


def _get_items(limit: int, offset: int, language: str, count: int = None) -> Tuple[
    List[asos.ProductDetailsResponse], int]:
    products = []
    if count is None:
        count = asos_controller.db[f'product_details_{language}'].count_documents({'isInStock': True})
    if offset < count:
        products = asos_controller.db[f'product_details_{language}'].find({'isInStock': True}).skip(offset).limit(limit)
    return [asos.ProductDetailsResponse(**product) for product in products], count


def _get_categories(limit: int, offset: int, language: str, count: int = None) -> Tuple[List[asos.FacetValue], int]:
    categories = []
    if count is None:
        count = asos_controller.db[f'categories_{language}'].count_documents()
    if offset < count:
        categories = asos_controller.db[f'categories_{language}'].find().skip(offset).limit(limit)
    return [asos.FacetValue(**category) for category in categories], count


def _upload_tags(language, tags: List[str]):
    if tags and len(tags) > 0:
        sql_values = []
        for item in tags:
            sql_values.append((item, item))
        try:
            cursor = pg_conn.cursor()
            sql_query = """INSERT INTO web.tag (name, source_name) VALUES (%s, %s)
            ON CONFLICT (name)
            DO NOTHING"""
            cursor.executemany(sql_query, sql_values)
            pg_conn.commit()
        except DatabaseError as de:
            logging.error("uploader::_upload_tags::database_error", de)
        except Exception as ex:
            logging.error("uploader::_upload_tags::general_exception", ex)
        finally:
            cursor.close()


def _upload_categories(language: str):
    has_more = True
    page = 0
    count = None
    while has_more:
        items, total_items = _get_categories(limit=100, offset=page, language=language, count=count)
        count = total_items
        page += 1
        if items and len(items) > 0:
            sql_values = []
            for item in items:
                sql_values.append((item.id, item.name,))
            try:
                cursor = pg_conn.cursor()
                sql_query = """INSERT INTO web.category (source_id, source_name) VALUES (%s, %s)"""
                cursor.executemany(sql_query, sql_values)
                pg_conn.commit()
            except DatabaseError as de:
                logging.error("uploader::_upload_categories::database_error", de)
            except Exception as ex:
                logging.error("uploader::_upload_categories::general_exception", ex)
            finally:
                cursor.close()
        else:
            has_more = False


def _upload_items(language: asos_controller.Language, vendor_id: int):
    lang_suffix = 'fr' if language == asos_controller.Language.french else 'en'

    has_more = True
    page = 0
    count = None
    while has_more:
        items, total_items = _get_items(limit=100, offset=page, language=lang_suffix, count=count)
        count = total_items
        page += 1
        if items and len(items) > 0:
            sql_values = []
            tags = set()
            tags_items = dict()
            for item in items:
                tags.add(item.pdpLayout)
                if item.pdpLayout not in tags_items:
                    tags_items[item.pdpLayout] = [item.id]
                else:
                    tags_items[item.pdpLayout].append(item.id)
                list_detail = asos_controller.get_product(language, item.id)
                item_price = convert_price(item.price.current.value, item.price.currency)
                description = str(item.info).replace(",", "\n").replace("'", "").strip("{}")
                color = "-" + list_detail.colour if list_detail.colour is not None else ""
                sql_values.append(
                    (vendor_id, item.name + color, random.randint(5, 20), item_price, description,
                     list_detail.imageUrl, 1,
                     item.id,
                     item.brand.name, list_detail.colour, lang_suffix, datetime.now(),))
            try:
                if len(tags) > 100:
                    for chunk in _split_list_into_chunks(100, list(tags)):
                        _upload_tags(lang_suffix, chunk)
                else:
                    _upload_tags(lang_suffix, tags)
                cursor = pg_conn.cursor()
                sql = """INSERT INTO 
                    web.product(vendor, title,qty, price_in_cents, description, thumbnail, source_id, 
                    id_at_source, brand, color,lang, date_added)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
                     ON CONFLICT (title)
                     DO UPDATE SET qty= excluded.qty, price_in_cents = excluded.price_in_cents, 
                     description = excluded.description, source_id = excluded.source_id, 
                     id_at_source = excluded.id_at_source, brand = excluded.brand, color = excluded.color, 
                     date_added =excluded.date_added"""
                cursor.executemany(sql, sql_values)
                pg_conn.commit()
                cursor.close()
                logging.info(f"uploader::_upload_items::uploaded {len(sql_values)} items")
                for item in items:
                    _upload_item_related_attributes(item)
            except DatabaseError as de:
                logging.error("uploader::fetch_and_upload::database_error", de)
            except Exception as ex:
                logging.error("uploader::fetch_and_upload:general_exception", ex)
            break
        else:
            has_more = False


def _upload_item_variants(item_id: int, variants: List[asos.Variant]):
    sql_values = set()
    for variant in variants:
        if variant.isInStock and variant.isAvailable:
            sql_values.add((item_id, variant.id, variant.brandSize, variant.colour,
                            convert_price(variant.price.current.value, variant.price.currency),))
    sql_query = """INSERT INTO web.product_variant(product_id, variant_id, size, color, price) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (product_id,variant_id) 
                DO UPDATE SET size =excluded.size, color =excluded.color, price =excluded.price"""
    try:
        cursor = pg_conn.cursor()
        cursor.executemany(sql_query, sql_values)
        pg_conn.commit()
    except DatabaseError as de:
        logging.error("uploader::_upload_item_variants::database_error", de)
    except Exception as ex:
        logging.error("uploader::_upload_item_variants:general_exception", ex)
    finally:
        cursor.close()


def _upload_item_images(dest_id: int, image_urls: List[str]):
    sql_query = """INSERT INTO web.productimage(product, image_url)  
    VALUES (%s, %s) 
    ON CONFLICT (product, image_url) DO NOTHING"""
    sql_values = []
    for image_url in image_urls:
        sql_values.append((dest_id, image_url,))
    try:
        cursor = pg_conn.cursor()
        cursor.executemany(sql_query, sql_values)
        pg_conn.commit()
    except DatabaseError as de:
        logging.error("uploader::_upload_item_images::database_error", de)
    except Exception as ex:
        logging.error("uploader::_upload_item_images:general_exception", ex)
    finally:
        cursor.close()


def _upload_item_tags(dest_id: int, tag: str):
    sql_query = """SELECT id FROM web.tag WHERE source_name = %s"""
    try:
        cursor = pg_conn.cursor()
        cursor.execute(sql_query, (tag,))
        tag_id = cursor.fetchone()[0]
        if tag_id:
            sql_query = """INSERT INTO web.tag_product_through(product_id, tag_id) VALUES (%s, %s) 
            ON CONFLICT (product_id, tag_id) DO NOTHING"""
            sql_values = (dest_id, tag_id,)
            cursor.execute(sql_query, sql_values)
            pg_conn.commit()
    except DatabaseError as de:
        logging.error("uploader::_upload_item_tags::database_error", de)
    except Exception as ex:
        logging.error("uploader::_upload_item_tags:general_exception", ex)
    finally:
        cursor.close()


def _upload_item_categories(item_source_id: int, cat_ids: List[int]):
    pass


def _upload_item_related_attributes(item: asos.ProductDetailsResponse):
    sql_query = """SELECT prod_id FROM web.product WHERE source_id =%s AND id_at_source=%s LIMIT 1"""
    item_id = None
    item_source_id = item.id
    try:
        cursor = pg_conn.cursor()
        cursor.execute(sql_query, (1, item_source_id,))
        item_id = cursor.fetchall()[0][0]
        pg_conn.commit()
    except DatabaseError as de:
        logging.error("uploader::_upload_item_related_attributes::database_error", de)
    except Exception as ex:
        logging.error("uploader::_upload_item_related_attributes:general_exception", ex)
    finally:
        cursor.close()

    if item_id:
        _upload_item_variants(item_id, item.variants)
        _upload_item_images(item_id, [image.url for image in item.media.images])
        _upload_item_tags(item_id, item.pdpLayout)


def convert_price(price: int, currency: str) -> float:
    if currency == 'EUR':
        return price * 100 * 700
    elif currency == 'USD':
        return price * 100 * 620


def fetch_and_upload(language: asos_controller.Language, vendor_id: int):
    lang_suffix = 'fr' if language == asos_controller.Language.french else 'en'
    # _upload_categories(lang_suffix)
    _upload_items(language, vendor_id)


def start_upload():
    sql_cursor = pg_conn.cursor()
    user_name = "assosell"
    sql = """SELECT user_id FROM web.user WHERE username=%s LIMIT 1"""
    sql_cursor.execute(sql, (user_name,))
    user_id = sql_cursor.fetchall()[0][0]
    pg_conn.commit()
    sql_cursor.close()

    fetch_and_upload(asos_controller.Language.french, user_id)
    # fetch_and_upload(asos_controller.Language.english, user_id)
    pg_conn.close()


if __name__ == "__main__":
    init()
    start_upload()
