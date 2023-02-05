from pymongo import MongoClient

from .asos import *


def init(db_client: MongoClient):
    asos.init(db_client)

