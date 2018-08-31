# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuUserItem(scrapy.Item):
    # define the fields for your item here like:
    userid = scrapy.Field()         # 目标字段是“id”，这里改成“userid”了。
    url_token = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    answer_count = scrapy.Field()
    articles_count = scrapy.Field()
    gender = scrapy.Field()
    headline = scrapy.Field()
    follower_count = scrapy.Field()
    badge = scrapy.Field()
    employments = scrapy.Field()
    updatetime = scrapy.Field()     # 自己增加的字段
