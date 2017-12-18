# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import pymysql


def db_connent():
    conn = pymysql.connect(
        host='47.94.139.196',
        user='root',
        passwd='Changtia0',
        db='academic_headline',
        charset='utf8',
        use_unicode=True
    )
    return conn


class DemoPipeline(object):

    def __init__(self):
        """该类将爬取的item信息写入本地json文件
        """
        self.file = codecs.open('data.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
