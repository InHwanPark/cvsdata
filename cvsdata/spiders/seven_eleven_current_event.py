# -*- coding: utf-8 -*-
from scrapy import Spider


class SevenElevenCurrentEventSpider(Spider):
    name = 'seven_eleven_current_event'
    allowed_domains = ['7-eleven.co.kr']
    start_urls = ['http://www.7-eleven.co.kr/event/eventList.asp?intPageSize=14&state=Y']

    def parse(self, response):
        results = response.xpath('//ul[@id="listUl"]/li')

        for result in results:
            site_name = 'seven eleven'
            event_type = ''
            event_name = result.xpath('.//dl/dt/text()').extract_first()
            # 일단 전체 기간으로 받고 split으로 시작일 종료일 분리
            period = result.xpath('.//dl/dd[@class="date"]/text()').extract_first().split(' ~ ')

            period_start = period[0]
            period_end = period[1]
            announcement_date = ''
            event_link = result.xpath('.//a[@class="event_img"]/@href').extract_first()
            event_link = 'http://www.7-eleven.co.kr/event/eventView.asp?seqNo=' + event_link[event_link.find("('") + 2: event_link.find("',") ] + '&listNo=1&intPageSize=8'
            img_url = response.urljoin(result.xpath('.//a[@class="event_img"]/img/@src').extract_first().replace('\\\\', '/'))

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


            