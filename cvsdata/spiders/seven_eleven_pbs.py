# -*- coding: utf-8 -*-
from scrapy import Spider, Request



class SevenElevenPbsSpider(Spider):
    name = 'seven_eleven_pbs'
    allowed_domains = ['7-eleven.co.kr']
    start_urls = ['http://www.7-eleven.co.kr/product/bestdosirakList.asp?intPageSize=100&pTab=5']

    # global variables
    product_cnt = 0
    prev_product_cnt = 0

    def parse(self, response):
        
        intPageSize = 100
        pTab = 5

        product_list = response.xpath('//*[@id="listDiv"]//div[contains(@class, "img_list")]/ul/li')
        print(len(product_list))

        for product in product_list:
            event_type = '도시락'

            img_url = response.urljoin(product.xpath('.//*[@class="pic_product"]/img/@src').extract_first())
            name = product.xpath('.//*[@class="infowrap"]/div[@class="name"]/text()').extract_first()
            price = product.xpath('.//*[@class="infowrap"]/div[@class="price"]/span/text()').extract_first()

            product_tag = product.xpath('./ul[@class="tag_list_01"]/li/text()').extract_first()

            new = 'N'
            popular = 'N'

            if product_tag == '인기':
                popular = 'Y'
            elif product_tag == '신상품':
                new = 'Y'

            freebie_img_url = ''
            freebie_name = ''
            freebie_price = ''

            if name is not None:
                yield {'event_type':event_type, 'img_url':img_url, 'name':name, 'price':price, 'new': new, 'popular' :popular, 'freebie_img_url':freebie_img_url, 'freebie_name':freebie_name, 'freebie_price':freebie_price}
            else:
                continue

    def parse_detail(self, response):
        pass
        
