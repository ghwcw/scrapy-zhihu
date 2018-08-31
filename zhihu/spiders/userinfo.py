# -*- coding: utf-8 -*-
import json
import scrapy

from zhihu.items import ZhihuUserItem


class UserinfoSpider(scrapy.Spider):
    name = 'userinfo'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    custom_settings = {
        'ITEM_PIPELINES': {'zhihu.pipelines.ZhihuPipeline': 300, }
    }

    # 知乎用户URL，获取用户的基本信息。  入口地址 https://www.zhihu.com/people/excited-vczh/following?page=1
    start_username = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{username}?include={user_query}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 关注列表URL，进一步获取被关注者的基本信息
    followees_url = 'https://www.zhihu.com/api/v4/members/{username}/followees?include={followees_query}&offset={offset}&limit={limit}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    # 关注他的人（粉丝）列表URL，进一步获取关注者的基本信息
    fans_url = 'https://www.zhihu.com/api/v4/members/{username}/followers?include={fans_query}&offset={offset}&limit={limit}'
    fans_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # 知乎用户请求URL
        yield scrapy.Request(url=self.user_url.format(username=self.start_username, user_query=self.user_query),
                             callback=self.parse_user)
        # 关注列表请求URL
        yield scrapy.Request(
            url=self.followees_url.format(username=self.start_username, followees_query=self.followees_query, offset=0,
                                          limit=20), callback=self.parse_followees)

        # 关注他的人（粉丝）列表请求URL
        yield scrapy.Request(
            url=self.fans_url.format(username=self.start_username, fans_query=self.fans_query, offset=0, limit=20),
            callback=self.parse_fans)

    def parse_user(self, response):
        """
        解析用户的基本信息
        :param response:
        :return:
        """
        result = json.loads(response.text)
        item = ZhihuUserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field, '')
            if 'id' in result.keys():
                item['userid'] = result.get('id', '')

        yield item
        # print(item)

        # 解析出关注列表请求URL放入调度器
        yield scrapy.Request(
            url=self.followees_url.format(username=result.get('url_token'), followees_query=self.followees_query,
                                          offset=0, limit=20), callback=self.parse_followees)

        # 解析出关注他的人（粉丝）列表请求URL放入调度器
        yield scrapy.Request(
            url=self.fans_url.format(username=result.get('url_token'), fans_query=self.fans_query,
                                     offset=0, limit=20), callback=self.parse_fans)

    def parse_followees(self, response):
        """
        解析关注列表基本信息
        :param response:
        :return:
        """
        result = json.loads(response.text)

        # 关注列表的基本信息
        if 'data' in result.keys():
            for user in result.get('data'):
                yield scrapy.Request(
                    url=self.user_url.format(username=user.get('url_token'), user_query=self.user_query),
                    callback=self.parse_user)

        # 下一页是关注列表
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse_followees)

    def parse_fans(self, response):
        """
        解析关注他的人（粉丝）的基本信息
        :param response:
        :return:
        """
        result = json.loads(response.text)

        # 关注他的人（粉丝）的基本信息
        if 'data' in result.keys():
            for user in result.get('data'):
                yield scrapy.Request(
                    url=self.user_url.format(username=user.get('url_token'), user_query=self.user_query),
                    callback=self.parse_user)

        # 下一页是关注他的人（粉丝）的列表
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse_fans)
