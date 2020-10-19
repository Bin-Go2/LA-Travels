# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TripadvisorscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class RestItem(scrapy.Item):

    name = scrapy.Field()
    stars = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    cusine_type = scrapy.Field()
    location = scrapy.Field()
    hotels = scrapy.Field()
    rests = scrapy.Field()
    attrcs = scrapy.Field()
    special_foods = scrapy.Field()
    review_txt = scrapy.Field()
    url = scrapy.Field()



class HotelItem(scrapy.Item):

    name = scrapy.Field()
    price_info = scrapy.Field()
    room_num = scrapy.Field()
    stars = scrapy.Field()
    amentites = scrapy.Field()
    features = scrapy.Field()
    room_types = scrapy.Field()
    hotel_class = scrapy.Field()
    hotel_style = scrapy.Field()
    location = scrapy.Field()
    near_rests = scrapy.Field()
    near_attrcs = scrapy.Field()
    popular_mentions= scrapy.Field()
    review_txt = scrapy.Field()
    url = scrapy.Field()
    
     