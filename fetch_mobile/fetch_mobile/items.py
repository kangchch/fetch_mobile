# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JiHaoBaItem(scrapy.Item):
    # define the fields for your item here like:
    status = scrapy.Field()
    mobile = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    # area_code = scrapy.Field()
    # operator = scrapy.Field()
    # card_type = scrapy.Field()

    # city_url = scrapy.Field()
    # num_area_url = scrapy.Field()
