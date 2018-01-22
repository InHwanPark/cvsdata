# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
# from scrapy.loader import ItemLoader
from cvsdata.items import CvsdataItem

# GS25 1+1 2+1 증정 상품 목록
class Gs25EventsSpider(Spider):
    name = 'gs25_events'
    allowed_domains = ['gs25.gsretail.com']
    start_urls = ['http://gs25.gsretail.com/gscvs/ko/products/event-goods']
    json_url = 'http://gs25.gsretail.com/gscvs/ko/products/event-goods-search?CSRFToken='
    
    # global variables
    current_page = 1

    def parse(self, response):
        self.json_url += response.xpath('//input[@name="CSRFToken"]/@value').extract_first()

        absolute_url = self.json_url + "&pageNum={}&pageSize={}&parameterList={}".format(1, 8, 'TOTAL')

        yield Request(url=absolute_url, method='POST',
                      headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate'
                      },
                      callback=self.parse_page_json,
                      dont_filter=True)

    def parse_page_json(self, response):
        jsonresponse = json.loads(response.body)
        jsonresponse = json.loads(jsonresponse)

        # json result 에서 페이징 정보 가져온다
        total_page = jsonresponse['pagination']['numberOfPages']
        page_size = jsonresponse['pagination']['pageSize']

        absolute_url = self.json_url + "&pageNum={}&pageSize={}&parameterList={}"

        for i in range(1, total_page+1):
            yield Request(url=absolute_url.format(i, 8, 'TOTAL'), method='POST',
                      headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate'
                      },
                      callback=self.parse_json,
                      dont_filter=True)

        #   각 페이징 요소 완료시까지 이동


    def parse_json(self, response):
        # l = ItemLoader(item=CvsdataItem(), response=response)

        jsonresponse = json.loads(response.body)
        jsonresponse = json.loads(jsonresponse)

        items = []
        for product in jsonresponse['results']:
            event_type = product['eventTypeNm']
            pic_url = product['attFileNm']
            goods_name = product['goodsNm']
            price = product['price']

            freebie_img_url = ''
            freebie_name = ''
            freebie_price = ''

            if event_type == '증정(기타)':
                freebie_img_url = product['giftAttFileNm']
                freebie_name = product['giftGoodsNm']
                freebie_price = product['giftPrice']

            item = CvsdataItem()
            item['site_name'] = 'gs25'
            item['target_page'] = '행사상품'
            item['category'] = event_type
            item['event_type'] = event_type
            item['detail_page_url'] = response.url
            item['img_url'] = pic_url
            item['goods_name'] = goods_name
            item['price'] = price
            item['new_yn'] = 'N'
            item['popular_yn'] = 'N'
            item['freebie_img_url'] = freebie_img_url
            item['freebie_name'] = freebie_name
            item['freebie_price'] = freebie_price
            item['freebie_new_yn'] = 'N'
            item['freebie_popular_yn'] = 'N'

            items.append(item)
        
        return items
