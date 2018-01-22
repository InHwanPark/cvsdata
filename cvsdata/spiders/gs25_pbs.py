# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from cvsdata.items import CvsdataItem

# GS25 PB 상품 리스트
class Gs25PbsSpider(Spider):
    name = 'gs25_pbs'
    allowed_domains = ['gs25.gsretail.com']
    start_urls = ['http://gs25.gsretail.com/gscvs/ko/products/youus-freshfood',
                  'http://gs25.gsretail.com/gscvs/ko/products/youus-different-service'
    ]

    json_url = 'http://gs25.gsretail.com/products/youus-freshfoodDetail-search?CSRFToken='
    bestYouUsProductDetailViewList = []
    def parse(self, response):
        self.json_url += response.xpath('//input[@name="CSRFToken"]/@value').extract_first()

        absolute_url = self.json_url + '&pageNum={}&pageSize={}&searchSrvFoodCK={}&searchSort={}&searchProduct={}'

        # FreshFoodKey
        # DifferentServiceKey
        category = 'FreshFoodKey'

        if 'different' in response.url:
            category = 'DifferentServiceKey'

        yield Request(url=absolute_url.format(1, 16, category, 'searchAllSort', 'productAll'),
                    headers={
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate'
                    },
                    meta={'category':category},
                    callback=self.parse_page_json,
                    dont_filter=True)


    def parse_page_json(self, response):
        jsonresponse = json.loads(response.body, encoding='utf-8')
        jsonresponse = json.loads(jsonresponse, encoding='utf-8')

        # json result 에서 페이징 정보 가져온다
        
        total_page = jsonresponse['SubPageListPagination']['numberOfPages']
        page_size = jsonresponse['SubPageListPagination']['pageSize']

        self.bestYouUsProductDetailViewList = [best_pd['code'] for best_pd in jsonresponse['bestYouUsProductDetailViewList']]

        print('test best len : {}'.format(len(self.bestYouUsProductDetailViewList)))

        absolute_url = self.json_url + '&pageNum={}&pageSize={}&searchSrvFoodCK={}&searchSort={}&searchProduct={}'

        for i in range(1, total_page + 1):
            yield Request(url=absolute_url.format(i, 16, response.meta.get('category'), 'searchAllSort', 'productAll'),
                        headers={
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate'
                        },
                        meta={'category':response.meta.get('category')},
                        callback=self.parse_json,
                        dont_filter=True)


    def parse_json(self, response):
        jsonobject = json.loads(response.body, encoding='utf-8')
        jsonobject = json.loads(jsonobject, encoding='utf-8')

        items = []
        for product in jsonobject['SubPageListData']:
            
            event_type = '차별화 상품' if response.meta.get('category') == 'DifferentServiceKey' else 'Fresh Food'
            img_url = product['attFileNmOld']
            goods_name = product['goodsNm']
            price = product['price']

            new_yn = product['isNew']

            if new_yn == 'T':
                new_yn = 'Y'
            else:
                new_yn = 'N'

            best_yn = 'Y' if product['code'] in self.bestYouUsProductDetailViewList else 'N'

            freebie_img_url = ''
            freebie_name = ''
            freebie_price = ''

            item = CvsdataItem()
            item['site_name'] = 'gs25'
            item['target_page'] = 'PB'
            item['category'] = event_type
            item['event_type'] = event_type
            item['detail_page_url'] = response.url
            item['img_url'] = img_url
            item['goods_name'] = goods_name
            item['price'] = price
            item['new_yn'] = new_yn
            item['popular_yn'] = best_yn
            item['freebie_img_url'] = freebie_img_url
            item['freebie_name'] = freebie_name
            item['freebie_price'] = freebie_price
            item['freebie_new_yn'] = 'N'
            item['freebie_popular_yn'] = 'N'

            items.append(item)
        
        return items
