# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from datetime import datetime
from scrapy_demo.models import *
import requests,re
from scrapy import Selector
from scrapy_demo.items import *
from scrapy_demo.servers.mysqlServer import mysqlService


class CsdnSpider(scrapy.Spider):
    name = 'csdn'
    allowed_domains = ['csdn.net','me.csdn.net']
    start_urls = ['https://bbs.csdn.net/forums/ios?page=7']
    domain = "https://bbs.csdn.net"

    def parse(self, response):
        all_trs = response.xpath('//div[@class="forums_table_c"]/table/tbody/tr')
        content = response.xpath("//div[@class='fl']/a[3]/text()").extract()[0]
        page_info = response.xpath("//div[@class='page_nav']/em[1]/text()").extract()[0]
        for tr in all_trs:
            res = {}
            res["status"] = tr.xpath('./td[@class="forums_topic_flag"]/span/text()').extract()[0]
            res["score"] = tr.xpath('./td[@class="forums_score"]/em/text()').extract()[0]
            topic_urls = tr.xpath('./td[@class="forums_topic"]/a/@href').extract()
            if len(topic_urls) > 1:
                topic_url = parse.urljoin(self.domain, topic_urls[1])
            else:
                topic_url = parse.urljoin(self.domain, topic_urls[0])
            detail_page_info = self.get_detail_page_info(topic_url)
            res["content"] = detail_page_info[0]
            res["praised_nums"] = detail_page_info[1]
            res["jtl"] = detail_page_info[2]
            res['topic_url'] = topic_url
            res['topic_id'] = int(topic_url.split('/')[-1])
            res['topic_title'] = tr.xpath('./td[@class="forums_topic"]/a/text()').extract()[0].replace('【', '').replace(
                '】', '')
            author_url = parse.urljoin(self.domain, tr.xpath('./td[@class="forums_author"]/a/@href').extract()[0])
            res['author_url'] = author_url
            res['author_id'] = author_url.split('/')[-1]
            res['auth_name'] = tr.xpath('./td[@class="forums_author"]/a/text()').extract()[0]
            view_num = tr.xpath('./td[@class="forums_reply"]/span/text()').extract()[0]
            create_date = tr.xpath('./td[@class="forums_author"]/em/text()').extract()[0]
            answer_last_date = tr.xpath('./td[@class="forums_last_pub"]/em/text()').extract()[0]
            res['create_date'] = datetime.strptime(create_date, "%Y-%m-%d %H:%M")
            res['last_pub_time'] = datetime.strptime(answer_last_date, "%Y-%m-%d %H:%M")
            res['answer_nums'] = int(view_num.split('/')[0])
            res['click_nums'] = int(view_num.split('/')[1])

            topicitem = TopicItem()
            topicitem["status"] = res.get("status")
            topicitem["title"] = res.get("topic_title")
            topicitem["topic_id"] = res.get("topic_id")
            topicitem["author"] = res.get("author_id")
            topicitem["click_nums"] = res.get("click_nums")
            topicitem["answer_nums"] = res.get("answer_nums")
            topicitem["create_time"] = res.get("create_date")
            topicitem["last_pub_time"] = res.get("last_pub_time")
            topicitem["score"] = res.get("score")
            topicitem["content"] = res.get("content","")
            topicitem["praised_nums"] = res.get("praised_nums",0)
            topicitem["jtl"] = res.get("jtl")

            yield topicitem
            yield scrapy.http.Request(url=topic_url,callback=self.parse_topic)
            yield scrapy.http.Request(url=author_url,callback=self.parse_author)
        all_page = int(response.xpath('//div[@class="forums_table_c"]/table/tfoot/tr[2]/td/div/div/a/text()').extract()[-2])
        next_page = int(response.xpath('//a[@class="pageliststy cur_page"]/text()').extract()[0]) + 1
        if next_page <= all_page and next_page:
            next_url = self.start_urls[0]+'?page=%s'%str(next_page)
            print('next_url:%s'%next_url)
            mysqlService.insert_url(next_url)
            yield scrapy.http.Request(url=next_url,callback=self.parse)


    def format_data(self,content):
        return content.replace('\t', '').replace('\n', '').strip()

    def get_detail_page_info(self,url):
        res_text = requests.get(url).text
        sel = Selector(text=res_text)
        all_divs = sel.xpath("//div[starts-with(@id, 'post-')]")
        topic_item = all_divs[0]
        ##标题
        content = self.format_data(sel.xpath("//dd[@class='topic_r post_info floorOwner']/div/div/text()").extract()[0])
        ##点赞数
        praised_nums = topic_item.xpath(".//label[@class='red_praise digg d_hide']//em/text()").extract()[0].split(' ')[-1]
        ##结贴率
        jtl_str = topic_item.xpath(".//div[@class='close_topic']/text()").extract()[0]
        jtl = 0
        jtl_match = re.search("(\d+)%", jtl_str)
        if jtl_match:
            jtl = int(jtl_match.group(1))
        return (content, praised_nums, jtl)

    def parse_topic(self,response):
        # 获取帖子的详情以及回复
        topic_id = response.url.split("/")[-1]
        all_divs = response.xpath("//div[starts-with(@id, 'post-')]")

        for answer_item in all_divs[1:]:
            content = self.format_data(answer_item.xpath(".//div[@class='post_body post_body_min_h']/text()").extract()[0])
            if not content:
                continue
            answeritem = AnswerItem()
            answeritem['topic_id'] = topic_id
            author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]
            author_id = author_info.split("/")[-1]
            create_time = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
            create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            answeritem['author'] = author_id
            answeritem['create_time'] = create_time
            praised_nums = answer_item.xpath(".//label[@class='red_praise digg d_hide']//em/text()").extract()[0].split(' ')[-1]
            answeritem['parised_nums'] = int(praised_nums) if praised_nums else 0
            answeritem['content'] = content

            yield answeritem

    def parse_author(selef,response):
        author_id = response.url.split("/")[-1]
        # 获取用户的详情
        authoritem = AuthorItem()
        all_li_strs = response.xpath("//div[@class='my_tab_page_con']/dl")
        click_nums = 0
        for article in all_li_strs:
            num = int(article.xpath("//div[@class='my_tab_page_con']/dl[1]/dd[2]/div/label/em/text()").extract()[0])
            click_nums += num
        original_nums_res = response.xpath("//ul[@class='me_chanel_list clearfix']/li[1]/a/label/span[2]/text()").extract()
        original_nums = 0
        if original_nums_res:
            original_nums = int(original_nums_res[0].strip())
        following_nums_res = response.xpath("//div[@class='me_wrap_r']/div[1]/div[2]/a/span/text()").extract()
        following_nums = 0
        follower_nums = 0
        if following_nums_res:
            following_nums = int(following_nums_res[0].strip())
        follower_nums_res = response.xpath("//div[@class='me_wrap_r']/div[1]/div[1]/a/span/text()").extract()
        if follower_nums_res:
            follower_nums = int(follower_nums_res[0].strip())
        rate_str = \
        response.xpath("//div[@class='me_chanel_det_item level']//*[name()='svg' and @class='icon']").extract()[0]
        rate = int(re.match(r'(.*)csdnc-bloglevel-(\d*)', rate_str.split('use')[1]).group(2))
        desc = response.xpath("//div[@class='description clearfix']/p/text()").extract()[0].strip()
        name = response.xpath("//div[@class='lt_title']/text()").extract()[2].strip()

        authoritem['id'] = author_id
        authoritem['click_nums'] = click_nums
        authoritem['original_nums'] = original_nums
        authoritem['following_nums'] = following_nums
        authoritem['follower_nums'] = follower_nums
        authoritem['rate'] = rate
        authoritem['answer_nums'] = original_nums
        authoritem['parised_nums'] = 0
        authoritem['desc'] = desc
        authoritem['name'] = name

        yield authoritem
