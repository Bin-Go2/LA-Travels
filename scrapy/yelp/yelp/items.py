# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StoreItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    url = scrapy.Field()
    name = scrapy.Field()
    rating = scrapy.Field()
    # title_text = scrapy.Field() # 
    location = scrapy.Field()
    price = scrapy.Field()
    food_type = scrapy.Field()
    review = scrapy.Field()
       
    
