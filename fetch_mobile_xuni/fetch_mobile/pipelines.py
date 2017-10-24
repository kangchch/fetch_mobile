# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from scrapy import log
from scrapy.conf import settings

class FetchMobilePipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def open_spider(self, spider):
        mongo_info = settings.get('MONGO_INFO', {})
        self.mongo_db_Conn = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).fetch_mobile

    def close_spider(self, spider):
        # self.mongo_db_Conn.close()
        pass

    def process_item(self, item, spider):
        #insert mongo
        province = item['province']
        city = item['city']
        mobile = item['mobile']
        # for i in city:
        for j in mobile:
            try:
                self.mongo_db_Conn.mobiles_one.insert_one(
                    {
                        'province': province,
                        'city': city,
                        'mobile': j,
                        'insert_time': datetime.datetime.now()
                    }
                )
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception, e:
                spider.log('insert mongo failed! mobile=%d (%s)' % (j, str(e)), level=log.ERROR)

            spider.log('piplines insert mongo succed. pro:%s cty:%s mobile:%s' %
                (province, city, j), level=log.INFO)
