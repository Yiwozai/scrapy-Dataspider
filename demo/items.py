# -*- coding: utf-8 -*-

# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader


class FirstFilter(object):
    """处理input_processor传递来的迭代器，选取第一个并清洗
    """
    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return value.strip()
        return ''


class StripLink(object):
    """用于清洗空格符并连接，返回string divided by '_'
    """
    def __call__(self, values):
        string = ''
        for value in values:
            if value.strip():
                string += value.strip() + '_'
        return string[:-1]


class AuthorFilter(object):
    """处理author、author_en字段，连接作者等级并返回string divided by '_'
    """
    def __call__(self, values):
        string = ''
        for value in values:
            string += value
            if value.isdigit():
                string += '_'
        return string[:-1]


class IDFilter(object):
    """处理URL_ID字段
    """
    def __call__(self, values):
        return values[0].split('_')[1][:-5]


class DemoLoader(ItemLoader):
    """这是搜集数据所用的Item Loader

    更多请查看官方文档：https://docs.scrapy.org/en/latest/topics/loaders.html

    """
    default_output_processor = FirstFilter()


class DemoItem(Item):

    # 文章名
    dissertation = Field()
    dissertation_en = Field()

    # chinadoi网址
    doi = Field()

    # 摘要
    abstract = Field()
    abstract_en = Field(output_processor=lambda x: x[1].strip() if len(x) > 1 else x[0].strip())

    # 作者
    author = Field(output_processor=AuthorFilter())
    author_en = Field(output_processor=AuthorFilter())
    author_unit = Field(input_processor=StripLink())

    # 期刊
    journal = Field()
    journal_en = Field()
    journal_date = Field(input_processor=lambda x: ''.join(x[0].split('\xa0')))

    # 分类号
    classification = Field()

    # 关键词
    keywords = Field(input_processor=StripLink())
    keywords_en = Field(input_processor=StripLink())

    # 基金项目
    fund_project = Field()

    # 来源URL
    source_url = Field(output_processor=IDFilter())
