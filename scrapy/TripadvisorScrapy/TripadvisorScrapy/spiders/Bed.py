import scrapy
from TripadvisorScrapy import items
import json

class BedSpider(scrapy.Spider):

    custom_settings = {
    	'ITEM_PIPELINES':{'TripadvisorScrapy.pipelines.HotelPipeline': 400}}


    name = 'Bed'
    allowed_domains = ['www.tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/Hotels-g32655-Los_Angeles_California-Hotels.html']

    def parse(self, response):
        
        hotel_urls = response.xpath("//a[contains(@href,'html') and contains(@href,'/Hotel_Review-g') \
        and not(contains(@href,'REVIEW'))]/@href").getall()
        for hotel_url in hotel_urls:
            yield response.follow(hotel_url, callback=self.detail_parse)

        next_page = response.xpath("//a[contains(text(),'Next')]/@href").get()
        if next_page:
            print(next_page,'**=**'*10)
            yield response.follow(next_page, callback=self.parse)

    def detail_parse(self,response):

        try:
            reviews = response.meta['reviews']
        except:
            reviews = []

        reviews_selector = len(response.xpath("//div[@data-reviewid]/div[3]/div[1]/div/q"))

        for i in range(1,reviews_selector+1):
            review_txt = response.xpath(f"string((//div[@data-reviewid]/div[3]/div[1]/div/q)[{i}])").get()
            reviews.append(review_txt)

        next_page = response.xpath("//a[contains(text(),'Next')]/@href").get()
        
        
        if next_page:
            yield response.follow(next_page, callback=self.detail_parse,meta={'reviews':reviews})

        else:

            hotel = items.HotelItem()
            name = response.xpath("//h1[@id]/text()").get()
            price_info = response.xpath("string((//div[@id='ABOUT_TAB'])[2]/div/div[2])").get(default='not list')
            room_num = response.xpath("(//div[@id='ABOUT_TAB'])[2]/div/div[last()]/text()").get(default='not list')
            stars = response.xpath("(//div[@id='ABOUT_TAB'])[1]/div[2]/div[1]/div[1]/span/text()").get(default='not list')

            desc = response.xpath("(//div[@id='ABOUT_TAB'])[1]/div[2]/div[2]/div[1]/@data-ssrev-handlers").get(default='not list')
            amentites,features,room_types = [],[],[]
            if desc != 'not list':
                desc = json.loads(desc)
                try:
                    for i in desc['load'][-1]['amenities']['highlightedAmenities']['propertyAmenities']:
                        amentites.append(i['amenityNameLocalized'])
                    for i in desc['load'][-1]['amenities']['nonHighlightedAmenities']['propertyAmenities']:
                        amentites.append(i['amenityNameLocalized'])
                except:
                    pass

                try:
                    for i in desc['load'][-1]['amenities']['highlightedAmenities']['roomFeatures']:
                        features.append(i['amenityNameLocalized'])
                    for i in desc['load'][-1]['amenities']['nonHighlightedAmenities']['roomFeatures']:
                        features.append(i['amenityNameLocalized'])
                except:
                    pass
                
                try:
                    for i in desc['load'][-1]['amenities']['highlightedAmenities']['roomTypes']:
                        room_types.append(i['amenityNameLocalized'])
                    for i in desc['load'][-1]['amenities']['nonHighlightedAmenities']['roomTypes']:
                        room_types.append(i['amenityNameLocalized'])
                except:
                    pass

            hotel_class = response.xpath("(//div[@id='ABOUT_TAB'])[1]/div[2]/div[2]/div[3]/div/div[2]/span/span/@title").get(default='not list')

            hotel_style = []
            hotel_style = response.xpath("(//div[@id='ABOUT_TAB'])[1]/div[2]/div[2]/div[3]/div/div/text()").getall()
            hotel_style = list(filter(lambda x:x!='HOTEL STYLE',hotel_style))

            location = response.xpath("//div[@id='LOCATION']/div[4]/div[1]/div[2]/span/span/text()").get(default='not list')

            near_rests = []
            near_rests_selector = response.xpath("//div[@id='LOCATION']/div[4]/div[2]/a")

            for i in near_rests_selector:
                try:
                    rest_name = i.xpath("div[1]/text()").get()
                    distance = i.xpath("string(div[2]/span[2])").get()
                    near_rests.append((rest_name,distance))
                except:
                    continue

            near_attrcs = []
            near_atts_selector = response.xpath("//div[@id='LOCATION']/div[4]/div[3]/a")
            
            for i in near_atts_selector:
                try:
                    attr_name = i.xpath("div[1]/text()").get()
                    distance = i.xpath("string(div[2]/span[2])").get()
                    near_attrcs.append((attr_name,distance))
                except:
                    continue
        
            popular_mentions = response.xpath("//button[@class='ui_button secondary small H5_EAgqY']/text()").getall()

            hotel['name'] = name
            hotel['price_info'] = price_info
            hotel['room_num'] = room_num
            hotel['stars'] = stars
            hotel['amentites'] = amentites
            hotel['features'] = features
            hotel['room_types'] = room_types
            hotel['hotel_class'] = hotel_class
            hotel['hotel_style'] = hotel_style
            hotel['location'] = location
            hotel['near_rests'] = near_rests
            hotel['near_attrcs'] = near_attrcs
            hotel['review_txt'] = reviews
            hotel['popular_mentions'] = popular_mentions

            hotel['url'] = response.request.url

            yield hotel


