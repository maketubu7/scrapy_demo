# -*- coding: utf-8 -*-
# @Time    : 2020/11/4 17:13
# @Author  : Deng Wenxing
# @Email   : dengwenxingae86@163.com
# @File    : mysqlServer.py
# @Software: PyCharm

from scrapy_demo.common.libs.PropertiesUtil import Properties
from scrapy_demo.servers.mysqlPool import POOL

class mysqlService:

    @classmethod
    def get_conn(cls):
        conn = POOL.connection()
        cur = conn.cursor()
        return conn, cur
    @classmethod
    def colse_conn(cls,conn,cur):
        conn.close()
        cur.close()

    @classmethod
    def insert_url(cls,url):
        conn,cur = cls.get_conn()
        print(conn,cur)
        try:
            sql = 'insert into history_url (url) values ("%s")'%url
            cur.execute(sql)
        except:
            conn.rollback()
            cls.colse_conn(conn,cur)



if __name__ == '__main__':
    mysqlService.insert_url('asdas')
