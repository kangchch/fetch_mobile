#! coding:utf-8

import pymongo
from pymongo import MongoClient
import datetime

mongo_db = pymongo.MongoClient('192.168.60.65', 10010).fetch_mobile

db_mobile = mongo_db.mobiles_one

db_mobile.insert_one({
    'mobile': '',
    'province': '',
    'city': '',
    'insert_time': datetime.datetime.now()
})
