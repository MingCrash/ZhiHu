# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.conf import settings
from Zhihu.items import ZhihuItem
import scrapy
import urllib
import time
import json
import re

class CommentspSpider(scrapy.Spider):
    name = 'commentSP'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    question_params = {
        't':'general',
        'q': None,
        'correction': 1,
        'offset': None,
        'limit': 20,  #跨度
    }
    anserws_params = {
        'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics',
        'offset': None,
        'limit': 20,  #跨度
        'sort_by': 'created'
    }
    comment_parmas = {
        'include': 'data[*].author,collapsed,reply_to_author,disliked,content,voting,vote_count,is_parent_author,is_author',
        'order': 'normal',
        'offset': None,
        'limit': 20,  #跨度
        'status': 'open'
    }
    question_meet_end = None
    anserws_meet_end = None
    comment_meet_end = None

    def get_localtime(self):
        return time.strftime("%Y-%m-%d", time.localtime())

    def get_createtime(self,secs):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs))

    def start_requests(self):
        for i in settings.get('SEARCHWORD'):
            for j in range(0, settings.get('QUESTION_OFFSET')):
                if not self.question_meet_end:
                    self.question_params['q'] = i
                    self.question_params['offset'] = j * self.question_params['limit']
                    paramters = urllib.parse.urlencode(self.question_params)
                    api_link = 'https://www.zhihu.com/api/v4/search_v3?{paramtes}'.format(paramtes=paramters)
                    print('<————————————关键字',i,'首页链接————————————>\n',api_link,'\n<——————————————————————————————————>')
                    yield Request(url=api_link, callback=self.question_parse, meta={'kw': i})
                else:
                    break

    def question_parse(self, response):
        jsonBody = json.loads(response.body)
        self.question_meet_end = jsonBody['paging']['is_end']
        if not self.question_meet_end:
            for item in jsonBody['data']:
                if item['type'] == 'search_result':
                    itemType = item['object']['type']
                    itemCommentCount = item['object']['comment_count']

                    if itemType == 'article':
                        # tmparticleTitle = item['object']['title']
                        # articleTitle = re.sub('<em>(.*)</em>',response.meta['kw'],tmparticleTitle,1)
                        articleURL = 'https://zhuanlan.zhihu.com/p/{id}'.format(id=item['object']['id'])
                        # print(articleTitle,articleURL,itemCommentCount,'article')
                        yield Request(url=articleURL,callback=self.artical_parse,meta={'kw':response.meta['kw'],'id':item['object']['id']})

                    elif itemType == 'answer' and itemCommentCount>0:
                        tmpquestionTitle = item['object']['question']['name']
                        questionTitle = re.sub('<em>(.*)</em>',response.meta['kw'],tmpquestionTitle,1)
                        # questionURL = 'https://www.zhihu.com/question/{id}/answers/created'.format(id=item['object']['question']['id'])
                        # print(questionTitle,questionURL,itemCommentCount,'question')
                        # print('问题：',questionTitle)

                        self.anserws_meet_end = False
                        self.anserws_params['offset'] = 0
                        while not self.anserws_meet_end:
                            paramters = urllib.parse.urlencode(self.anserws_params)
                            questionURL = 'https://www.zhihu.com/api/v4/questions/{id}/answers?{paramtes}'.format(id=item['object']['question']['id'],paramtes=paramters)
                            yield Request(url=questionURL, callback=self.answer_parse, meta={'kw': response.meta['kw']})
                            self.anserws_params['offset'] += self.anserws_params['limit']
                            time.sleep(5)                       #--*-- 这个数值必须大于download delay值 --*--
                    else:
                        tmpquestionTitle = item['object']['question']['name']
                        questionTitless = re.sub('<em>(.*)</em>', response.meta['kw'], tmpquestionTitle, 1)
                        print('标题>>>>>',questionTitless,'<<<<<属于无回答问题，跳过\n')
                        continue
        else:
            return

    def answer_parse(self, response):
        jsonBody = json.loads(response.body)
        self.anserws_meet_end = jsonBody['paging']['is_end']
        if not self.anserws_meet_end:
            for item in jsonBody['data']:
                pipleitem = ZhihuItem()
                pipleitem['id'] = item['id']
                pipleitem['url'] = 'https://www.zhihu.com/question/{q_id}/answer/{a_id}'.format(q_id=item['question']['id'],a_id=item['id'])
                pipleitem['platform'] = '知乎'
                pipleitem['viewType'] = '问答'
                pipleitem['searchWord'] = response.meta['kw']
                pipleitem['Title'] = item['question']['title']
                pipleitem['crawlTime'] = self.get_localtime()
                pipleitem['publishTime'] = self.get_createtime(item['created_time'])
                pipleitem['level'] = 1
                pipleitem['commentID'] = 1
                pipleitem['comment_count'] = item['comment_count']
                pipleitem['like'] = item['voteup_count']
                pipleitem['authorName'] = item['author']['name']
                pipleitem['authorID'] = item['author']['id']
                pipleitem['Content'] = item['excerpt']
                yield pipleitem
                if item['comment_count'] > 0:
                    self.comment_meet_end = False
                    self.comment_parmas['offset'] = 0
                    while not self.comment_meet_end:
                        paramas = urllib.parse.urlencode(self.comment_parmas)
                        url = 'https://www.zhihu.com/api/v4/answers/{id}/comments?{paramters}'.format(id=item['id'],paramters=paramas)
                        yield Request(url=url, callback=self.comment_parse, meta={'answerid':item['id'], 'kw':response.meta['kw'], 'title':item['question']['title']})
                        self.comment_parmas['offset'] += self.comment_parmas['limit']
                        time.sleep(5)                       #--*-- 这个数值必须大于download delay值 --*--
                # print('--------------------ANSWER--------------------\n',response.url,'\n',pipleitem,'\n--------------------ANSWER--------------------\n')
        else:
            return

    def comment_parse(self, response):
        jsonBody = json.loads(response.body)
        self.comment_meet_end = jsonBody['paging']['is_end']
        if not self.comment_meet_end:
            for item in jsonBody['data']:
                pipleitem = ZhihuItem()
                pipleitem['id'] = response.meta['answerid']
                pipleitem['commentID'] = item['id']
                pipleitem['url'] = item['url']
                pipleitem['platform'] = '知乎'
                pipleitem['viewType'] = '问答'
                pipleitem['searchWord'] = response.meta['kw']
                pipleitem['Title'] = response.meta['title']
                pipleitem['crawlTime'] = self.get_localtime()
                pipleitem['publishTime'] = self.get_createtime(item['created_time'])
                pipleitem['level'] = 2
                pipleitem['like'] = item['vote_count']
                pipleitem['authorName'] = item['author']['member']['name']
                pipleitem['authorID'] = item['author']['member']['id']
                pipleitem['Content'] = item['content']
                # print('--------------------COMMENT--------------------\n',response.url,'\n',pipleitem,'\n--------------------COMMENT--------------------\n')
                yield pipleitem
        return

    def artical_parse(self, response):
        pipleitem = ZhihuItem()
        pipleitem['viewType'] = '文章'
        pipleitem['id'] = response.meta['id']
        pipleitem['url'] = response.url
        pipleitem['platform'] = '知乎'
        pipleitem['searchWord'] = response.meta['kw']
        pipleitem['Title'] = response.css('.Post-Header .Post-Title').xpath('string(.)').extract_first()
        pipleitem['crawlTime'] = self.get_localtime()
        created_secs = int(re.findall('&quot;created&quot;:(\d*)',response.body.decode())[0])
        pipleitem['publishTime'] = self.get_createtime(secs=created_secs)
        pipleitem['level'] = 1
        pipleitem['authorName'] = response.css('.AuthorInfo-name .UserLink-link').xpath('text()').extract_first()
        pipleitem['authorID'] = response.css('.AuthorInfo-name .UserLink-link').xpath('@href').extract_first()
        pipleitem['commentID'] = 1
        pipleitem['Content'] = response.css('#root .Post-RichText').xpath('string(.)').extract_first()
        # print('--------------------ARTICLE--------------------\n', response.url, '\n', pipleitem,'\n--------------------ARTICLE--------------------\n')
        return pipleitem




