# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class ZhihuPipeline(object):
    def __init__(self, mongo_host, mongo_port, mongo_db, mongo_collection):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGO_HOST'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item = dict(item)
        if int(item['gender']) == 1:
            item['gender'] = '男'
        elif int(item['gender']) == 0:
            item['gender'] = '女'
        else:
            item['gender'] = '未知'

        # 更新或插入文档
        self.collection.update_one({'url_token': item['url_token']}, {'$set': item}, True)

        return item
