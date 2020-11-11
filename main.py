# -*- coding: utf-8 -*-
# @Time    : 2020/11/2 15:40
# @Author  : Deng Wenxing
# @Email   : dengwenxingae86@163.com
# @File    : main.py
# @Software: PyCharm

from scrapy.cmdline import execute


if __name__ == "__main__":
    execute(['scrapy','crawl','csdn'])