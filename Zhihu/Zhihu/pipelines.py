# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sys
from scrapy.conf import settings


class Size16M_Pipeline(object):
    buffer_list = None
    filename = None

    def __init__(self):
        self.buffer_list = []
        self.filename = 0

    def close_spider(self, spider):
        if self.buffer_list:
            with open('{path}/{cfn}'.format(cfn='{}.txt'.format(self.filename), path=settings.get('STORE_PATH')),'a+',encoding='utf-8') as f:
                f.writelines(self.buffer_list)
                self.buffer_list.clear()

    def process_item(self, item, spider):
        str = '《Root》《S0》{id}《/S0》《S1》{url}《/S1》《S2》{pf}《/S2》《S3a》{vt}《/S3a》《S3b》{sw}《S3b》《S4》{title}《/S4》《S5》{ct}《/S5》《S6》{pt}《/S6》《S9》{level}《/S9》《ID》{cid}《/ID》《S12》{cc}《/S12》《S13》{like}《/S13》《G1》{an}《/G1》《G0》{aid}《/G0》《Q1》{content}《/Q1》《/Root》\n'.format(
            id=item.setdefault('id', ''), url=item.setdefault('url', ''), pf=item.setdefault('platform', ''), vt=item.setdefault('viewType', ''), sw=item.setdefault('searchWord', ''),
            title=item.setdefault('Title', ''), ct=item.setdefault('crawlTime', ''), pt=item.setdefault('publishTime', ''), level=item.setdefault('level', ''),
            cid=item.setdefault('commentID', ''), like=item.setdefault('like', ''), an=item.setdefault('authorName', ''),
            aid=item.setdefault('authorID', ''), content=item.setdefault('Content', ''), cc=item.setdefault('comment_count', ''))

        if not sys.getsizeof(self.buffer_list) > settings.get('FILE_SIZE'):
            self.buffer_list.append(str)
        else:
            self.filename = self.filename + 1
            with open(r'{path}/{cfn}'.format(cfn=r'{}.txt'.format(self.filename), path=settings.get('STORE_PATH')),'a+',encoding='utf-8') as f:
                f.writelines(self.buffer_list)
                self.buffer_list.clear()

        return item
