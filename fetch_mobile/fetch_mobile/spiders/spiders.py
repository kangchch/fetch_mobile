#! coding: utf-8

import requests
import os
import pymongo
from pymongo import MongoClient
import datetime
import logging
import scrapy
import re
import time
import traceback
from scrapy import log
import sys
from scrapy.conf import settings
from fetch_mobile.items import JiHaoBaItem
from scrapy.selector import Selector
from lxml import etree
from ipdb import set_trace


reload(sys)
sys.setdefaultencoding('utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1;WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Connection': 'keep-alive'
}

class FetchMobileSpider(scrapy.Spider):
    name = "mobile"

    def __init__(self, settings, *args, **kwargs):
        super(FetchMobileSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):
        try:
            i = JiHaoBaItem()
            i['status'] = 0
            url = 'http://www.jihaoba.com/tools/haoduan/'
            meta = {'dont_redirect': True, 'item': i, 'dont_retry': True}
            yield scrapy.Request(
                    url=url,
                    meta=meta,
                    callback=self.parse,
                    dont_filter=True)
        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    ##解析首页获取省和城市，
    def parse(self, response):
        i = response.meta['item']
        sel = Selector(response)
        
        i['status'] = response.status
        if response.status != 200:
            self.log('fetch failed! status=%d' % (i['status']), level=log.WARNING)

        xpath_handles = sel.xpath('//div[@class="hd_result1"]/div[@class="hd_mar"]')
        for each in xpath_handles:
            province = each.xpath('p/span/text()')[0].extract() ##省
            print province
            city_xpaths = each.xpath('div[@class="hd_number1"]/a')##城市
            for city_xpath in city_xpaths:
                city_url = city_xpath.xpath('@href')[0].extract()
                meta = {'dont_redirect': True, 'dont_retry': True, 'province': province}
                self.log('province=%s city_url=%s' % (province, city_url), level=log.INFO)
                yield scrapy.Request(
                    url = 'http://www.jihaoba.com' + city_url,
                    meta = meta,
                    callback = self.parse_list_page,
                    dont_filter = True)

    ##解析城市号段页(http://www.jihao.com/haoduan/'beijing')，存储号段对应url
    def parse_list_page(self, response):
        sel = Selector(response)

        # xpath_num = sel.xpath("//div[@class='hd_number']/a/@href")
        xpath_num = sel.xpath("//div[@class='haoduan-hd main'][1]/div[@class='hd_result']/div[@class='hd_mar']/div[@class='hd_number']/a")
        # pattern = r'/haoduan/[1-9].*/.*\.htm'
        # reg = re.compile(pattern)
        # num_area_urls = re.findall(reg, str(xpath_num))
        for each in xpath_num:
            num_area_url = each.xpath('@href')[0].extract() ##某个城市号段的url
            self.log('num_area_url=%s' % (num_area_url), level=log.INFO)
            yield scrapy.Request(
                    url='http://www.jihaoba.com' + num_area_url,
                    meta=response.meta,
                    callback=self.parse_item_page,
                    dont_filter=True)


    ##解析终结页面('http://www.jihaoba.com/haoduan/139/beijing.htm'), 返回到item存储
    def parse_item_page(self, response):
        i = JiHaoBaItem()
        res = requests.get(response.url, headers=headers)
        print response.url
        html = res.text
        selector = etree.HTML(html)

        xpath_handles = selector.xpath('//div[@class="haoduan-hd main"][2]/ul[@class="hd-city"]')

        for xpath_handle in xpath_handles:
            i = JiHaoBaItem()
            i['province'] = response.meta['province']
            i['city'] = xpath_handle.xpath('li[@class="hd-city03"]/text()')[0]
            i['mobile'] = xpath_handle.xpath('li[@class="hd-city01"]/a/text()')

            self.log('province:%s city:%s mobile:%s' %
                (i['province'], i['city'], i['mobile']), level=log.INFO)

            yield i


