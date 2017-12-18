# -*- coding: utf-8 -*-

"""
“万方数据”爬虫 —— 期刊部分

期刊数据获取

用于：Linux等POSIX兼容系统，或者有Python环境的Windows系统的爬虫客户端
"""

import re
from ..items import DemoItem, DemoLoader
from scrapy import Spider, Request


regex = re.compile(r'<t>共</t>&nbsp;(\d+)&nbsp;<t>页</t>')


class DemoSpider(Spider):

    """
    这个爬虫经历以下过程：

    单个期刊页面 ===》 解析出各文章页面
    各文章页面   ===》 爬取数据
    """

    name = 'dataget'
    allowed_domains = ['wanfangdata.com.cn']
    start_urls = ['http://c.g.wanfangdata.com.cn/Periodical-lxxb.aspx']

    def parse(self, response, chance=True):
        """解析杂志主页面，位于：“单个杂志”页面
        """
        # yield Request 每一期
        journals = response.css('div[class=new_ul] li a::attr(href)').extract()
        for journal in journals:
            yield Request(
                url=response.urljoin(journal),
                callback=self.parse
            )

        # yield Request 首页这一期的每篇论文
        articles = response.css('a[class="qkcontent_name"]::attr(href)').extract()
        for article in articles:
            yield Request(
                url=article,
                callback=self.parse_article
            )

    def parse_article(self, response):
        """采集文章信息，位于：“文章” 页面
        """
        # 实例化item loader
        item = DemoLoader(item=DemoItem(), response=response)

        # 论文
        # item['dissertation']: string  —— 这个字符串可能是中文名字，也可能是英文
        #                       —— 当是中文时，可能还有name_en
        #                       —— 当是英文时，一定没有name_en
        # item['dissertation_en']: string
        item.add_css('dissertation', 'div[class=btn_list] h1::text')
        item.add_css('dissertation_en', 'div[class=btn_list] h2::text')

        # URL
        # item['source_url']: string
        item.add_value('source_url', response.url)

        # chinadoi
        # item['doi']: string
        item.add_css('doi', 'dl[id=doi_dl] a::text')

        # 摘要
        # item['abstract']: string
        # item['abstract_en']: string
        abstracts = response.css('dl[class=abstract_dl] dt t::text').extract()
        if len(abstracts) == 1:
            if abstracts[0] == '摘要：':
                item.add_css('abstract', 'dl[class=abstract_dl] dd::text')
                item.add_value('abstract_en', '')
            else:
                assert abstracts[0] == 'Abstract：', '不为中文摘要，就一定是英文摘要'
                item.add_value('abstract', '')
                item.add_css('abstract_en', 'dl[class=abstract_dl] dd::text')
        elif len(abstracts) == 2:
            item.add_css('abstract', 'dl[class=abstract_dl] dd::text')
            item.add_css('abstract_en', 'dl[class=abstract_dl] dd::text')

        # ======================|
        #                       |
        # 下面所有筛选借助 lables |
        #                       |
        # ======================|
        lables = response.css('tr')

        # 作者
        # item['author']： string divided by '_'   eg: AAA_BBB_CCC
        # item['author_en']: string divided by '_'   eg: AAA_BBB_CCC
        # item['author_unit']: string divided by '_'   eg: AAA_BBB_CCC
        item.add_css('author_en', 'td', re=r'([A-Z]\w+ [A-Z][\w-]+?)<sup>\[(\d)\]</sup>')

        for lable in lables:
            # 更换Item Loader选择器
            item.selector = lable
            tag_name = lable.css('th t::text').extract_first()

            if tag_name == '作者':
                item.add_css('author', 'td', re=r'(\w+)(?:</a>)?<sup>\[(\d)\]</sup>')
            elif tag_name == '作者单位':
                item.add_css('author_unit', 'td ol li::text')

            # 期刊
            # item['journal']: string
            # item['journal_en']: string
            # item['journal_date']: string
            elif tag_name == '刊  名：':
                item.add_css('journal', 'td a::text')
            elif tag_name == 'Journal：':
                item.add_css('journal_en', 'td a::text')
            elif tag_name == '年，卷(期)':
                item.add_css('journal_date', 'td a::text')

            # 分类号
            # item['classification']： string
            elif tag_name == '分类号':
                item.add_css('classification', 'td::text')

            # 关键词
            # item['keywords']： string divided by '_'   eg: AAA_BBB_CCC
            # item['keywords_en']： string divided by '_'   eg: AAA_BBB_CCC
            elif tag_name == '关键词：':
                item.add_css('keywords', 'td a::text')
            elif tag_name == 'Keywords：':
                item.add_css('keywords_en', 'td a::text')

            # 基金项目
            # item['fund_project']: string
            elif tag_name == '基金项目':
                item.add_css('fund_project', 'td::text')

        return item.load_item()
