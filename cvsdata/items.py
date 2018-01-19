# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class CvsdataItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    site_name = Field()
    target_page = Field()
    category = Field()
    event_type = Field()
    goods_name = Field()
    price = Field()
    discount_price = Field()
    new_yn = Field()
    popular_yn = Field()
    distributer = Field()
    weight = Field()
    description = Field()
    img_url = Field()
    freebie_name = Field()
    freebie_price = Field()
    freebie_new_yn = Field()
    freebie_popular_yn = Field()
    freebie_distributer = Field()
    freebie_weight = Field()
    freebie_description = Field()
    freebie_img_url = Field()
