# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from TripadvisorScrapy import settings

class TripadvisorscrapyPipeline:
    def process_item(self, item, spider):
        return item


class RestPipeline:
    
    def __init__(self):
        # connect db
        self.client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
        self.db = self.client[settings.MONGO_DB]  # connect db
        self.coll = self.db[settings.MONGO_COLL_REST]  # connect collections
    
    def process_item(self, item, spider):
        postItem = dict(item)  

        self.coll.insert(postItem)  
        # upsert data
        # self.coll.update_one(postItem, {'$set': postItem}, upsert=True)

        return item 


class HotelPipeline:

    def __init__(self):
        # connect db
        self.client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)
        self.db = self.client[settings.MONGO_DB]  # connect db
        self.coll = self.db[settings.MONGO_COLL_HOTEL]  # connect collections
    
    def process_item(self, item, spider):
        postItem = dict(item)  

        self.coll.insert(postItem)  
        # upsert data
        # self.coll.update_one(postItem, {'$set': postItem}, upsert=True)

        return item 