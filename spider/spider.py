# coding=utf-8
import os
import logging
import re
import requests

import pandas as pd

import scrapy
from selenium import webdriver

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.html import remove_tags, replace_tags

import coloredlogs
import json

coloredlogs.install(level='DEBUG')

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'scrapy': {
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)



# %%
class Spider(CrawlSpider):
    name = "kaggle-kernels"

    # allowed_domains = ['www.site.com']
    
#     rules = (
#         Rule(LinkExtractor(allow=(r'links/.*$'), deny=('')), callback='parse_item'),
#         Rule(LinkExtractor(allow=(r'links/[a-z]/\d+'))),
#     )
    custom_settings = {
        'LOGSTATS_INTERVAL': 15,
        'EXTENSIONS': {
            'scrapy.extensions.logstats.LogStats': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        }
    }
    
    # start_urls = ['http://www.site.com/links']
    # kernels_df = pd.read_pickle('../data/kernels10000.pkl.gz')
    # start_urls = ['https://www.kaggle.com/kernels/all/{}'.format(i) for i in range(4000, 20000, 20)]
    # start_urls = ['https://www.kaggle.com/kernels/sourceurl/{}'.format(id) for id in kernels_df['scriptVersionId'].values] 

#     def __init__(self):
#         self.browser = webdriver.Chrome()
#         self.browser.implicitly_wait(60)
    
    def old_parse_item(self, response):
        item = {}
        item['url'] = response.url
        # logging.debug('yo!')
        
        
#         self.browser.get(response.url)  # load response to the browser
#         button = self.browser.find_element_by_xpath("script-code-pane__download") # find 
#         url = re.search(response.text, 'http://www.kaggle.io/(.*))')
#         print(url)
#         button.press()
        RE = 'Kaggle\.State\.push\((\{".*"\})\);performance'
        match = re.search(RE, response.text)
        res = json.loads(match.group(1))

        # xpath = '//*[@id="{}"]/*'.format(attr)
        
        # lst = response.xpath(xpath).extract()
        # item['list'] = list(filter(None, (map(lambda x: replace_tags(x, '\n'), lst))))
        
        # elems = response.xpath('//*').extract()
        # item['text'] = ' '.join((map(remove_tags, elems))

        yield res

    def parse_item(self, response):
        item = {}
        item['url'] = response.url
        
        url = response.url
        BASE_URL = 'https://www.kaggle.com/kernels/sourceurl/{}'
        author, kernel  = url.split('/')[3], url.split('/')[3]
        RE = '"scriptVersionId":(\d+)'
        match = re.search(RE, response.text)
        id = match.group(1)

        yield scrapy.Request(BASE_URL.format(id), callback=self.parse_sourceurl, meta={'author': author, 'kernel': kernel})

        
    def parse_sourceurl(self, response):
        meta = response.meta
        
        kernel_source_url = response.text
        print(kernel_source_url)

        RE = '/([\w\.]+)\?sv='
        meta['fn'] = re.search(RE, kernel_source_url).group(1)
        yield scrapy.Request(kernel_source_url, callback=self.parse_source, meta=meta)



    def parse_source(self, response):
        meta = response.meta
        item = meta
        item['url'] = response.url
        kind = item['fn'].split('.')[-1]
        if not os.path.exists('../results/{}'.format(kind)):
            os.makedirs('../results/{}'.format(kind))
        
        fn = '../results/{}/{}_{}_{}'.format(kind, meta['author'], meta['kernel'], meta['fn'])
        with open(fn, 'w') as f:
            print(response.text, file=f)

    def old_parse_start_url(self, response):
        for kernel in json.loads(response.body.decode()):
            url = '{}{}/'.format('https://www.kaggle.com', kernel['scriptUrl'])
            print(url)
            yield scrapy.Request(url, callback=self.parse_item)

    def start_requests(self):
        kernels_df = pd.read_pickle('../data/kernels10000.pkl.gz')
        # start_urls = ['https://www.kaggle.com/kernels/all/{}'.format(i) for i in range(4000, 20000, 20)]
        for url, id in kernels_df[['scriptUrl', 'scriptVersionId']].values:
            print(url)
            author, kernel = url.split('/')[1:]
            meta = {'author': author, 'kernel': kernel}
            yield scrapy.Request('https://www.kaggle.com/kernels/sourceurl/{}'.format(id), 
                           callback=self.parse_sourceurl, meta=meta)


    def _parse_start_url(self, response):
    
        meta = {'url': response.url}
        
        kernel_source_url = response.text

        RE = '/([\w\.]+)\?sv='
        meta['fn'] = re.search(RE, kernel_source_url).group(1)
        yield scrapy.Request(kernel_source_url, callback=self.parse_source, meta=meta)