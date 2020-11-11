# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_demo.models import *


class ScrapyDemoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TopicItem(scrapy.Item):
    topic_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    create_time = scrapy.Field()
    last_pub_time = scrapy.Field()
    answer_nums = scrapy.Field()
    click_nums = scrapy.Field()
    praised_nums = scrapy.Field()
    jtl = scrapy.Field()
    score = scrapy.Field()
    status = scrapy.Field()

    def save(self):
        topic =Topic()
        topic.topic_id = self['topic_id']
        topic.title = self['title']
        topic.content = self['content']
        topic.author = self['author']
        topic.create_time = self['create_time']
        topic.last_pub_time = self['last_pub_time']
        topic.answer_nums = self['answer_nums']
        topic.click_nums = self['click_nums']
        topic.praised_nums = self['praised_nums']
        topic.jtl = self['jtl']
        topic.score = self['score']
        topic.status = self['status']

        exists_topic = topic.select().where(Topic.topic_id == topic.topic_id)

        if exists_topic:
            topic.save()
        else:
            topic.save(force_insert=True)


class AuthorItem(scrapy.Item):
    id = scrapy.Field()
    click_nums = scrapy.Field()
    original_nums = scrapy.Field()
    forward_nums = scrapy.Field()
    rate = scrapy.Field()
    answer_nums = scrapy.Field()
    parised_nums = scrapy.Field()
    desc = scrapy.Field()
    location = scrapy.Field()
    industry = scrapy.Field()
    name = scrapy.Field()
    following_nums = scrapy.Field()
    follower_nums = scrapy.Field()

    def save(self):
        author = Author()
        author.id = self['id']
        author.click_nums = self['click_nums']
        author.original_nums = self['original_nums']
        author.forward_nums = self.get('forward_nums',0)
        author.rate = self['rate']
        author.answer_nums = self['answer_nums']
        author.parised_nums = self['parised_nums']
        author.desc = self['desc']
        author.location = self.get('location','')
        author.industry = self.get('industry','')
        author.name = self['name']
        author.follower_nums = self['follower_nums']
        author.following_nums = self['following_nums']
        existed_author = Author.select().where(Author.id == author.id)
        if existed_author:
            author.save()
        else:
            author.save(force_insert=True)

class AnswerItem(scrapy.Item):
    topic_id = scrapy.Field()
    author = scrapy.Field()
    create_time = scrapy.Field()
    parised_nums = scrapy.Field()
    content = scrapy.Field()

    def save(self):
        answer = Answer()
        answer.topic_id = self['topic_id']
        answer.author = self['author']
        answer.create_time = self['create_time']
        answer.parised_nums = self['parised_nums']
        answer.content = self['content']
        answer.save()
