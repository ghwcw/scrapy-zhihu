# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

import pymongo
import pymysql
import sqlalchemy
from sqlalchemy import Integer, String, func, DateTime, exists, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ZhihuPipeline(object):
    """
    输出到MongoDB中
    """

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

        # 更新或插入文档，与MongoDB shell命令类似
        self.collection.update_one({'url_token': item['url_token']}, {'$set': item}, True)

        return item


class ZhihuPipelineToMySQL(object):
    """
    输出到MySQL中
    """

    def __init__(self, mysql_user, mysql_password, mysql_host, mysql_port, mysql_db, mysql_table):
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db
        self.mysql_table = mysql_table

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
            mysql_table=crawler.settings.get('MYSQL_TABLE'),
        )

    def open_spider(self, spider):
        self.client = pymysql.Connect(user=self.mysql_user, password=self.mysql_password, host=self.mysql_host,
                                      port=self.mysql_port, database=self.mysql_db, charset='utf8')
        self.cursor = self.client.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.client.close()

    def process_item(self, items, spider):
        item = dict(items)
        if int(item['gender']) == 1:
            item['gender'] = '男'
        elif int(item['gender']) == 0:
            item['gender'] = '女'
        else:
            item['gender'] = '未知'

        # 将数据插入MySQL
        try:
            sql = "insert into {0}(userid,url_token,`name`,`type`,answer_count,articles_count,gender,headline,follower_count,badge,employments) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
                self.mysql_table)

            self.cursor.execute(sql,
                                (item['userid'], item['url_token'], item['name'], item['type'], item['answer_count'],
                                 item['articles_count'], item['gender'], item['headline'], item['follower_count'],
                                 str(item['badge']), str(item['employments'])))

            self.client.commit()
            self.cursor.scroll(0)
        except Exception as e:
            print('MySQL操作失败！->%s' % e)

        return item


class ZhihuPipelineToMySQLORM(object):
    """
    使用SQLAlchemy保存数据
    """

    def __init__(self, mysql_user, mysql_password, mysql_host, mysql_port, mysql_db):
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
        )

    def open_spider(self, spider):
        # 创建引擎
        self.engine = sqlalchemy.create_engine(
            'mysql+pymysql://{root}:{password}@{host}:{port}/{db}?charset=utf8'.format(root=self.mysql_user,
                                                                                       password=self.mysql_password,
                                                                                       host=self.mysql_host,
                                                                                       port=self.mysql_port,

                                                                                       db=self.mysql_db), echo=False)
        # 构建实体表
        Base.metadata.create_all(self.engine)
        # 建立会话
        Session = sessionmaker(bind=self.engine)
        self.ses = Session()

    def close_spider(self, spider):
        self.ses.close()

    def process_item(self, items, spider):
        item = dict(items)
        if int(item['gender']) == 1:
            item['gender'] = '男'
        elif int(item['gender']) == 0:
            item['gender'] = '女'
        else:
            item['gender'] = '未知'

        try:
            user_obj = ZhihuUsersOrm()
            user_obj.userid = item['userid']
            user_obj.url_token = item['url_token']
            user_obj.name = item['name']
            user_obj.type = item['type']
            user_obj.answer_count = item['answer_count']
            user_obj.articles_count = item['articles_count']
            user_obj.gender = item['gender']
            user_obj.headline = item['headline']
            user_obj.follower_count = item['follower_count']
            user_obj.badge = str(item['badge'])
            user_obj.employments = str(item['employments'])

            # 判断是否已存在
            boo = self.ses.query(ZhihuUsersOrm).filter(ZhihuUsersOrm.userid == item['userid']).all()
            if not boo:
                self.ses.add(user_obj)
                self.ses.commit()
        except Exception as err:
            print('SQLAlchemy操作失败！->%s' % err)

        return item


# 建模型表
# 声明基类，用于创建模型
Base = declarative_base()
class ZhihuUsersOrm(Base):
    __tablename__ = 'zhihu_users_orm'
    rowid = sqlalchemy.Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    userid = sqlalchemy.Column(String(128), unique=True, nullable=False, index=True)
    url_token = sqlalchemy.Column(String(64), nullable=False, unique=True)
    name = sqlalchemy.Column(String(128), nullable=False, index=True)
    type = sqlalchemy.Column(String(16))
    answer_count = sqlalchemy.Column(Integer)
    articles_count = sqlalchemy.Column(Integer)
    gender = sqlalchemy.Column(String(8))
    headline = sqlalchemy.Column(String(256))
    follower_count = sqlalchemy.Column(Integer)
    badge = sqlalchemy.Column(Text)
    employments = sqlalchemy.Column(Text)
    updatetime = sqlalchemy.Column(TIMESTAMP, nullable=False, default=datetime.datetime.now().isoformat())


