import scrapy
from TripadvisorScrapy import items

class FoodSpider(scrapy.Spider):
    name = 'Food'

    custom_settings = {
    	'ITEM_PIPELINES':{'TripadvisorScrapy.pipelines.RestPipeline': 300}}
    
    allowed_domains = ['www.tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/Restaurants-g32655-Los_Angeles_California.html']

    def parse(self, response):
        rest_urls = response.xpath("//div[@data-test]/span/div/div[1]/span/a/@href").getall()

        for rest_url in rest_urls:
            yield response.follow(rest_url, callback=self.detail_parse)

        next_page = response.xpath("//a[contains(text(),'Next')]/@href").get()
        if next_page:
            print(next_page,'***====***'*10)
            yield response.follow(next_page, callback=self.parse)

   
    def detail_parse(self,response):
        try:
            reviews = response.meta['reviews']
        except:
            reviews = []

        reviews_selector = len(response.xpath("//div[@class='review-container']"))
        for i in range(1,reviews_selector+1):
            review_txt = response.xpath(f"string((//div[@class='review-container'])[{i}]//div[@class='entry'])").get()
            reviews.append(review_txt)

        next_page = response.xpath("//a[contains(text(),'Next')]/@href").get()

        if next_page:
            yield response.follow(next_page, callback=self.detail_parse,meta={'reviews':reviews})

        else:
            restaurant = items.RestItem()
            
            name = response.xpath("//div[@class='react-container']/div/div[1]/h1/text()").get()
            stars = response.xpath("//div[@class='react-container']/div/div[2]/\
            span/a/span[@aria-label]/@aria-label").get(default='not-found')

            rating = response.xpath("//div[@class='react-container']/div/div[2]/span[2]//b//text()").get(default='not-list')
            price_and_cusine = response.xpath("//div[@class='react-container']/div/div[2]/span[3]/a/text()").getall()
            try:
                price = price_and_cusine[0] if '$' in price_and_cusine[0] else ''
                cusine_type = price_and_cusine[1:] if price else price_and_cusine[0:]
            except:
                price = 'not-list'
                cusine_type = 'not-list'

            location = response.xpath("//div[@class='react-container']/div/div[3]/span[1]//text()").get(default='not-list')

            near_hotels_selector = response.xpath("//div[span[contains(text(),'Best nearby hotels')]]/div/div")
            hotels = []
            for hotel in near_hotels_selector:
                hotel_name = hotel.xpath("div/div[1]/div[2]/div[1]/text()").get()
                try:
                    hotel_distance = float(hotel.xpath("div/div[1]/div[2]/div[4]/text()").get().split(' ')[0])
                    hotels.append(  (hotel_name,hotel_distance) )
                except:
                    hotels.append(  (hotel_name,'not-list') )

            near_rests_selector = response.xpath("//div[span[contains(text(),'Best nearby restaurants')]]/div/div")
            rests = []
            for rest in near_rests_selector:
                rest_name = rest.xpath("div/div[1]/div[2]/div[1]/text()").get()
                try:
                    rest_distance = float(rest.xpath("div/div[1]/div[2]/div[4]/text()").get().split(' ')[0])
                    rests.append((rest_name,rest_distance))
                except: 
                    rests.append((rest_name,'not-list'))

            near_attrcs_selector = response.xpath("//div[span[contains(text(),'Best nearby attractions')]]/div/div")
            attrcs = []
            for attrc in near_attrcs_selector:
                attrc_name = attrc.xpath("div/div[1]/div[2]/div[1]/text()").get()
                try:
                    attrc_distance = float(attrc.xpath("div/div[1]/div[2]/div[4]/text()").get().split(' ')[0])
                    attrcs.append((attrc_name,attrc_distance))
                except:
                    attrcs.append((attrc_name,'not-list'))

            special_foods = response.xpath("//span[@class='ui_tagcloud ']/text()").getall()

            
            restaurant['name'] = name
            restaurant['stars'] = stars
            restaurant['rating'] = rating
            restaurant['price'] = price
            restaurant['cusine_type'] = cusine_type
            restaurant['location'] = location
            restaurant['hotels'] = hotels
            restaurant['rests'] = rests
            restaurant['attrcs'] = attrcs
            restaurant['special_foods'] = special_foods
            restaurant['review_txt'] = reviews

            restaurant['url'] = response.request.url

            yield restaurant


