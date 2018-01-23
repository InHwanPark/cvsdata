# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from cvsdata.items import CvsdataItem

# SEVEN_ELEVEN 1+1 2+1 증정 할인 PB상품 전체
# 상품 DETAIL PAGE 진입
class SevenElevenEventsSpider(Spider):
    name = 'seven_eleven_events'
    allowed_domains = ['7-eleven.co.kr']
    start_urls = [
        'http://www.7-eleven.co.kr/product/listMoreAjax.asp',
        'http://www.7-eleven.co.kr/product/bestdosirakList.asp?intPageSize=200&pTab=5'
    ]

    # global variables
    detail_page_url = 'http://www.7-eleven.co.kr/product/presentView.asp?pCd={}'
    detail_freebie_page_url = 'http://www.7-eleven.co.kr/product/presentView_pre.asp?pCd={}'
    product_cnt = 0
    prev_product_cnt = 0

    def parse(self, response):
        
        if 'dosirak' in response.url:
            print('dosirak')
            yield Request(url=response.url, callback=self.parse_dosirak)
        else:
            # seven eleven의 각 속성별 Tab parameter 번호
            for tab_idx in range(1, 9):
                # seven eleven의 페이지 번호는 0부터 시작
                if tab_idx in range(6, 8):
                    print('continue at {}'.format(tab_idx))
                    continue

                for pageNo in range(0, 100):
                    # 크롤링의 첫 페이지가 아니면서 수집 결과 총 수가 증가 하지 않았으면 목록 크롤링이 끝났으므로
                    # 크롤링을 중지한다.
                    if self.product_cnt != 0 and (self.product_cnt == self.prev_product_cnt):
                        break
                    else:
                        # 상품이 추가로 수집된 경우 현재 상품수를 보존하고 다음 페이지로 넘어간다.
                        self.prev_product_cnt = self.product_cnt
                        yield Request(url=response.urljoin('?intPageSize={}&intCurrPage={}&pTab={}'.format(10, pageNo, tab_idx)), meta={'tab_idx': tab_idx}, callback=self.parse_product)


    def parse_product(self, response):
        # 반환 HTML 중 class 속성을 가지지 않은 <li> Tag가 상품 하나를 나타낸다.
        product_list = response.xpath('//li[not(@class)]')

        for product in product_list:
            event_type = product.xpath('./ul[@class="tag_list_01"]/li/text()').extract_first()

            if event_type is None:
                if response.meta.get('tab_idx') == 8:
                    event_type = '신상품'
                else:
                    event_type = '증정'

            img_url = response.urljoin(product.xpath('.//*[@class="pic_product"]/img/@src').extract_first())
            goods_name = product.xpath('.//*[@class="infowrap"]/div[@class="name"]/text()').extract_first()

            if goods_name == '' or goods_name is None:
                goods_name = product.xpath('.//span[@class="tit_product"]/text()').extract_first()

            price = product.xpath('.//*[@class="infowrap"]/div[@class="price"]/span/text()').extract_first()

            freebie_img_url = ''
            freebie_name = ''
            freebie_price = ''
            freebie_p_cd = ''

            p_cd = product.xpath('.//a[@class="btn_product_01"]/@href').extract_first()
            p_cd = p_cd[p_cd.find("('") + 2: p_cd.find("')") ]

            if event_type == '증정':
                freebie_img_url = product.xpath('./a[@class="btn_product_02"]//img/@src').extract_first()
                freebie_name = product.xpath('./a[@class="btn_product_02"]//div[@class="name"]/text()').extract_first()
                freebie_price = product.xpath('./a[@class="btn_product_02"]//div[@class="price"]/span/text()').extract_first()

                freebie_p_cd = product.xpath('.//a[@class="btn_product_02"]/@href').extract_first()

                if freebie_p_cd is not None and len(freebie_p_cd) > 0:
                    freebie_p_cd = freebie_p_cd[freebie_p_cd.find("('") + 2: freebie_p_cd.find("')") ]
                    print('found freebie_p_cd : {}'.format(freebie_p_cd))

            self.product_cnt += 1

            item = CvsdataItem()
            item['site_name'] = 'seven eleven'
            item['target_page'] = 'PB' if event_type == 'PB' else '행사상품'
            item['category'] = event_type
            item['event_type'] = event_type
            item['img_url'] = img_url
            item['goods_name'] = goods_name
            item['price'] = price
            # item['new_yn'] = new
            # item['popular_yn'] = popular
            item['freebie_img_url'] = freebie_img_url
            item['freebie_name'] = freebie_name
            item['freebie_price'] = freebie_price
            # item['freebie_new_yn'] = 'N'
            # item['freebie_popular_yn'] = 'N'

            # yield {'event_type':event_type, 'img_url':img_url, 'name':goods_name, 'price':price, 'new': 'N', 'popular': 'N', 'freebie_img_url':freebie_img_url, 'freebie_name':freebie_name, 'freebie_price':freebie_price}
            # yield item
            yield Request(url=self.detail_page_url.format(p_cd),
                         meta={'item':item, 'p_cd':p_cd, 'freebie_p_cd': freebie_p_cd},
                         callback=self.parse_detail,
                         dont_filter=True)
                    
    # dosirak list parse
    def parse_dosirak(self, response):

        product_list = response.xpath('//*[@id="listDiv"]//div[contains(@class, "img_list")]/ul/li')
        print(len(product_list))

        for product in product_list:
            event_type = '도시락'

            img_url = response.urljoin(product.xpath('.//*[@class="pic_product"]/img/@src').extract_first())
            goods_name = product.xpath('.//*[@class="infowrap"]/div[@class="name"]/text()').extract_first()
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

            # 아이템 반환 - return item
            if goods_name is not None:
                item = CvsdataItem()
                item['site_name'] = 'seven eleven'
                item['target_page'] = '도시락'
                item['category'] = event_type
                item['event_type'] = event_type
                item['img_url'] = img_url
                item['goods_name'] = goods_name
                item['price'] = price
                item['new_yn'] = new
                item['popular_yn'] = popular
                item['freebie_img_url'] = freebie_img_url
                item['freebie_name'] = freebie_name
                item['freebie_price'] = freebie_price
                # item['freebie_new_yn'] = 'N'
                # item['freebie_popular_yn'] = 'N'

                # yield 대신 아이템 반환으로 변경 - 여기서 Request Call을 통해 Detail Page로 들어가야 함 - detail page 주소, freebie detail page 주소 있는지 검사 필요
                # 수집 된 주소를 통해 self.parse_detail로 이동
                yield item
                # yield {'event_type':event_type, 'img_url':img_url, 'goods_name':goods_name, 'price':price, 'new': new, 'popular' :popular, 'freebie_img_url':freebie_img_url, 'freebie_name':freebie_name, 'freebie_price':freebie_price}
            else:
                continue

    def parse_detail(self, response):
        # response.meta.get('item') 과 response.meta.get('detail_page_url') 과 response.meta.get('freebie_detail_page_url')이용
        # 'freebie_detail_page_url'이 있는지 확인하고 있을 경우 item과 함께 다시한번 이동하도록 meta = {'item':item} 다시 실행
        # 'freebie_detail_page_url'이 없을 경우 증정품이 없으므로 끝내고 바로 yield 혹은 return
        # 수집 된 주소를 통해 self.parse_detail로 이동
        # http://www.7-eleven.co.kr/product/presentView.asp?pCd=061298

        item = response.meta.get('item')
        p_cd = response.meta.get('p_cd')
        freebie_p_cd = response.meta.get('freebie_p_cd')

        new_yn = response.xpath('//li[@class="ico_tag_03"]').extract_first()
        popular_yn = response.xpath('//li[@class="ico_tag_01"]').extract_first()

        price = response.xpath('//span[@class="product_price"]/del/text()').extract_first()

        if price is not None and len(price) > 0:
            price = price[:-2]

        discount_price = response.xpath('//span[@class="product_price"]/strong/text()').extract_first()

        if price is None:
            price = discount_price
            discount_price = None

        if new_yn == 'New':
            new_yn = 'Y'
        else:
            new_yn = 'N'

        if popular_yn == '인기':
            popular_yn = 'Y'
        else:
            popular_yn = 'N'

        item['price'] = price
        item['discount_price'] = discount_price
        item['new_yn'] = new_yn
        item['popular_yn'] = popular_yn
        item['distributer'] = response.xpath('//span[@class="tit_3depth"]/text()').extract_first()
        description = response.xpath('//dd[@class="productView_content_dd_01"]/span[@class="txt"]/text()').extract_first().strip()
        description = description.replace('\t','').replace('\r','').replace('\n','')
        item['description'] = description
        item['weight'] = response.xpath('//ul[@class="productView_content_ul"]/li/span/text()').extract_first()
        item['detail_page_url'] = 'http://www.7-eleven.co.kr/product/presentView.asp?pCd=' + p_cd

        # 증정품의 상품이 있을 경우 2차 수집 진행
        if freebie_p_cd is not None and freebie_p_cd is not '':
            print('FREEBIE ITEM CONFIRMED : {}'.format(freebie_p_cd))
            yield Request(url=self.detail_freebie_page_url.format(freebie_p_cd),
                         meta={'item':item, 'p_cd':p_cd, 'freebie_p_cd': freebie_p_cd},
                         callback=self.parse_freebie_detail, dont_filter=True)
        else:
            # freebie_p_cd 가 없을 경우 기존 그대로 return
            yield item

    def parse_freebie_detail(self, response):
        # 여기서 증정품 화면 확인
        item = response.meta.get('item')

        freebie_new_yn = response.xpath('//li[@class="ico_tag_03"]').extract_first()
        freebie_popular_yn = response.xpath('//li[@class="ico_tag_01"]').extract_first()

        if freebie_new_yn == 'New':
            freebie_new_yn = 'Y'
        else:
            freebie_new_yn = 'N'

        if freebie_popular_yn == '인기':
            freebie_popular_yn = 'Y'
        else:
            freebie_popular_yn = 'N'
        
        freebie_price = response.xpath('//span[@class="product_price"]/strong/text()').extract_first()
        freebie_distributer = response.xpath('//span[@class="tit_3depth"]/text()').extract_first()
        freebie_weight = response.xpath('//ul[@class="productView_content_ul"]/li/span/text()').extract_first()
        freebie_description = response.xpath('//dd[@class="productView_content_dd_01"]/span[@class="txt"]/text()').extract_first().strip()
        freebie_description = freebie_description.replace('\t','').replace('\r','').replace('\n','')
        
        item['freebie_new_yn'] = freebie_new_yn
        item['freebie_popular_yn'] = freebie_popular_yn
        item['freebie_price'] = freebie_price
        item['freebie_distributer'] = freebie_distributer
        item['freebie_weight'] = freebie_weight
        item['freebie_description'] = freebie_description
        item['detail_page_url'] = 'http://www.7-eleven.co.kr/product/presentView_pre.asp?pCd=' + response.meta.get('freebie_p_cd')

        yield item
