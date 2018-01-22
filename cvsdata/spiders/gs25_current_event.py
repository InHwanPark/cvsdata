# -*- coding: utf-8 -*-
import json
import datetime
from scrapy import Spider, Request


class Gs25CurrentEventSpider(Spider):
    name = 'gs25_current_event'
    allowed_domains = ['gs25.gsretail.com']
    start_urls = ['http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/current-events']
    json_url = 'http://gs25.gsretail.com/board/boardList?CSRFToken='

    # global variables
    current_page = 1

    def parse(self, response):
        csrf_token = response.xpath('//input[@name="CSRFToken"]/@value').extract_first()
        print(csrf_token)

        self.json_url += csrf_token

        # http://gs25.gsretail.com/board/boardList?CSRFToken=345c21e9-6a7b-40c5-9b9a-1acb767a7f42
        absolute_url = self.json_url + '&modelName=event&pageNum={}&pageSize={}&parameterList={}'
        
        # 여기서 그냥 디테일 페이지 이동
        # Token값 옮기기
        yield Request(url=absolute_url.format(1, 10, 'brandCode:GS25@!@eventFlag:CURRENT'), method='POST',
                      headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate'
                      },
                      callback=self.parse_page_json,
                      dont_filter=True)

    def parse_page_json(self, response):
        jsonresponse = json.loads(response.body)
        jsonresponse = json.loads(jsonresponse)

        pagination = jsonresponse['pagination']

        total_number_of_results = pagination['totalNumberOfResults']
        number_of_pages = pagination['numberOfPages']
        page_size = pagination['pageSize']

        absolute_url = self.json_url + '&modelName=event&pageNum={}&pageSize={}&parameterList={}'

        for i in range(1, number_of_pages + 1):
            yield Request(url=absolute_url.format(i, 10, 'brandCode:GS25@!@eventFlag:CURRENT'), method='POST',
                      headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate'
                      },
                      callback=self.parse_json,
                      dont_filter=True)

    def parse_json(self, response):
        jsonresponse = json.loads(response.body)
        jsonresponse = json.loads(jsonresponse)

        results = jsonresponse['results']

        for result in results:
            
            site_name = 'GS25'
            exposure_type = ''
            

            if 'exposureType' in result:
                exposure_type = result['exposureType']
                exposure_type = exposure_type['code']
            else:
                exposure_type = 'ONLINE'

            event_name = result['title']
            period_start = result['startDateString']
            period_end = result['endDateString']
            announcement_date = ''
            event_link = ''
            img_url = result['portraitThumbnail']['url']

            # event_type은 STAMP / PUBLISHING / SOCIALVOTE
            # http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/detail/stamp?eventCode=8814312082976
            # http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/detail/publishing?eventCode=8814082706976
            # http://www.gsretail.com/gsretail/ko/customer-engagement/event/detail/social-vote?eventCode=8814017170976
            event_type = result['eventType']
            event_code = result['eventCode']
            # event_type /  event_code 를 조합하여 이동페이지 링크 작성
            if event_type == 'STAMP':
                event_link = 'http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/detail/stamp?eventCode={}'.format(event_code)
            elif event_type == 'PUBLISHING':
                event_link = 'http://gs25.gsretail.com/gscvs/ko/customer-engagement/event/detail/publishing?eventCode={}'.format(event_code)
            elif event_type == 'SOCIALVOTE':
                event_link = 'http://www.gsretail.com/gsretail/ko/customer-engagement/event/detail/social-vote?eventCode={}'.format(event_code)

            # no_winner 값이 false 일 경우 -> 당첨자 발표가 필요한 이벤트 : announcementDate가 필요
            no_winner = result['noWinner']

            if no_winner is False:
                announcement_date = result['winnerAnnouncementDate']

            yield {
                'site_name': site_name, 
                'event_type': event_type, 
                'event_name': event_name, 
                'period_start':period_start, 
                'period_end':period_end, 
                'announcement_date': announcement_date, 
                'event_link': event_link, 
                'img_url': img_url
            }