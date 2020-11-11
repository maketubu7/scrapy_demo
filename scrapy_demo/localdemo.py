# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from datetime import datetime
from scrapy_demo.models import *
import requests,re
from scrapy import Selector
from scrapy_demo.items import *
from scrapy import Selector

def parse_author(response):
    author_id = response.url.split("/")[-1]
    # 获取用户的详情
    author = Author()
    all_li_strs = response.xpath("//div[@class='my_tab_page_con']/dl")
    click_nums = 0
    for article in all_li_strs:
        num = int(article.xpath("//div[@class='my_tab_page_con']/dl[1]/dd[2]/div/label/em/text()").extract()[0])
        click_nums += num
    original_nums = int(response.xpath("//ul[@class='me_chanel_list clearfix']/li[1]/a/label/span[2]/text()").extract()[0].strip())
    following_nums = int(response.xpath("//div[@class='me_wrap_r']/div[1]/div[2]/a/span/text()").extract()[0])
    follower_nums = int(response.xpath("//div[@class='me_wrap_r']/div[1]/div[1]/a/span/text()").extract()[0])
    rate_str = response.xpath("//div[@class='me_chanel_det_item level']//*[name()='svg' and @class='icon']").extract()[0]
    rate = int(re.match(r'(.*)csdnc-bloglevel-(\d*)',rate_str.split('use')[1]).group(2))
    desc = response.xpath("//div[@class='description clearfix']/p/text()").extract()[0].strip()
    name = response.xpath("//div[@class='lt_title']/text()").extract()[2].strip()

    author.id = author_id
    author.click_nums = click_nums
    author.original_nums = original_nums
    author.following_nums = following_nums
    author.follower_nums = follower_nums
    author.rate = rate
    author.answer_nums = original_nums
    author.parised_nums = 0
    author.desc = desc
    author.name = name

def parse_(response):
    all_page = int(response.xpath('//div[@class="forums_table_c"]/table/tfoot/tr[2]/td/div/div/a/text()').extract()[-2])
    next_page = int(response.xpath('//a[@class="pageliststy cur_page"]/text()').extract()[0]) + 1
    print(all_page,next_page)

def format_data(content):
    return content.replace('\t', '').replace('\n', '').strip()
def parse_topic(response):
    # 获取帖子的详情以及回复
    all_divs = response.xpath("//div[starts-with(@id, 'post-')]")
    res = []
    content = format_data(response.xpath("//dd[@class='topic_r post_info floorOwner']/div/div/text()").extract()[0])
    print(content)
    for answer_item in all_divs[1:]:
        content = format_data(answer_item.xpath(".//div[@class='post_body post_body_min_h']/text()").extract()[0])

        if not content:
            continue
        answeritem = AnswerItem()
        author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]
        author_id = author_info.split("/")[-1]
        create_time = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
        create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        answeritem['author'] = author_id
        answeritem['create_time'] = create_time
        praised_nums = answer_item.xpath(".//label[@class='red_praise digg d_hide']//em/text()").extract()[0].split(' ')[-1]
        answeritem['parised_nums'] = int(praised_nums) if praised_nums else 0
        answeritem['content'] = content
        res.append(answeritem)
    return res


if __name__ == '__main__':
    response = requests.get('https://bbs.csdn.net/topics/396639854')
    sel =Selector(response)
    res = parse_topic(sel)
    print(res)
