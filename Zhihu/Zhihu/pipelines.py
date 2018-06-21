# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from scrapy.conf import settings


class Size16M_Pipeline(object):
    cur_filename = None
    cur_filehold = None

    def __init__(self):
        self.cur_generator_filename = self.generator_filename()
        self.cur_filename = self.cur_generator_filename.__next__()

    def __del__(self):
        self.cur_filehold.close()

    def generator_filename(self):
        i=0
        while True:
            yield '{d}.txt'.format(d=i)
            i =+ 1

    def process_item(self, item, spider):
        with open('{path}/{cfn}'.format(cfn=self.cur_filename,path=settings.get('STORE_PATH')),'a+') as self.cur_filehold:
            str = '《Root》《S0》{id}《/S0》《S1》{url}《/S1》《S2》{pf}《/S2》《S3a》{vt}《/S3a》《S3b》{sw}《S3b》《S4》{title}《/S4》《S5》{ct}《/S5》《S6》{pt}《/S6》《S9》{level}《/S9》《ID》{cid}《/ID》《S12》{cc}《/S12》《S13》{like}《/S13》《G1》{an}《/G1》《G0》{aid}《/G0》《Q1》{content}《/Q1》\n'.format(
                id=item['id'], url=item['url'], pf=item['platform'], vt=item['viewType'], sw=item['searchWord'],
                title=item['Title'], ct=item['crawlTime'], pt=item['publishTime'], level=item['level'],
                cid=item['commentID'], like=item['like'], an=item['authorName'],
                aid=item['authorID'], content=item['Content'])
            self.cur_filehold.write(str)

        if os.path.getsize('{path}/{cfn}'.format(path=settings.get('STORE_PATH',cfn=self.cur_filename))) > settings.get('FILE_SIZE'):
            self.cur_filename = self.cur_generator_filename.__next__()

        return item
