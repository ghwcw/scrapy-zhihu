# -*- coding: utf-8 -*-
import scrapy


class UserinfoSpider(scrapy.Spider):
    name = 'userinfo'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # 知乎用户URL，获取用户基本信息
    start_username = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{username}?include={user_query}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 知乎用户关注列表，获取被关注者信息
    followees_url = 'https://www.zhihu.com/api/v4/members/{username}/followees?include={followees_query}&offset={offset}&limit={limit}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # 知乎用户请求Url
        yield scrapy.Request(url=self.user_url.format(username=self.start_username, user_query=self.user_query),
                             callback=self.parse_user)
        # 用户关注列表请求URL
        yield scrapy.Request(
            url=self.followees_url.format(username=self.start_username, followees_query=self.followees_query, offset=20,
                                          limit=20), callback=self.parse_followees)

    def parse_user(self, response):
        print(response.text)

    def parse_followees(self, response):
        print(response.text)
