# -*- coding: utf-8 -*-
# @Time    : 2020/2/28 21:59
# @Author  : Deng Wenxing
# @Email   : dengwenxingae86@163.com
# @File    : models.py
# @Software: PyCharm
import sys

from peewee import *
from scrapy_demo.common.libs.PropertiesUtil import Properties
from datetime import date

props = Properties('mysql.properties').properties
props["port"] = int(props["port"])
db = MySQLDatabase(**props)

class BaseModel(Model):
    class Meta:
        database = db


##设计数据表有几个重要点
class Topic(BaseModel):

    topic_id = IntegerField(primary_key=True)
    title = CharField()
    content = TextField(default="")
    author = CharField()
    create_time = DateTimeField()
    last_pub_time = DateTimeField()
    answer_nums = IntegerField(default=0)
    click_nums = IntegerField(default=0)
    praised_nums = IntegerField(default=0)
    jtl = FloatField(default=0.0)
    score = IntegerField(default=0)
    status = CharField()

class Answer(BaseModel):

    topic_id = IntegerField()
    author = CharField()
    quthor = CharField()
    content = TextField(default="")
    create_time = DateTimeField()
    parised_nums = IntegerField(default=0)

class Author(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)
    click_nums = IntegerField(default=0) #访问数
    original_nums = IntegerField(default=0) #原创数
    forward_nums = IntegerField(default=0)  # 转发数
    rate = IntegerField(default=-1)  # 排名
    answer_nums = IntegerField(default=0)  # 评论数
    parised_nums = IntegerField(default=0)  # 获赞数
    desc = TextField(null=True)
    industry = CharField(null=True)
    location = CharField(null=True)
    follower_nums = IntegerField(default=0)  # 粉丝数
    following_nums = IntegerField(default=0)  # 关注数


class history_url(BaseModel):
    id = AutoField()
    url = CharField()


if __name__ == "__main__":
    db.create_tables([history_url])