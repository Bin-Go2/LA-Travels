import scrapy
import time
from yelp.items import StoreItem

class YelpSpiderSpider(scrapy.Spider):
    name = 'yelp_spider'
    allowed_domains = ['www.yelp.com/']
    # start_urls = ['https://www.yelp.com/search?find_desc=&find_loc=Los+Angeles%2C+CA&ns=1']

    def start_requests(self):
        place_list = ['USC, Los Angeles','Hollywood, Los Angeles'] # POI 
        for place  in place_list:
            start_url = f"https://www.yelp.com/search?find_desc=&find_loc={place}"
            yield scrapy.Request(start_url,callback=self.depth1_parse)

    def depth1_parse(self, response):
        # crawl one page's restaurants' basic information for one specific place
        rest_urls = response.xpath("//h4//span/a/@href").getall()
        candidate_urls = list(filter(lambda x: x[:4]=='/biz', rest_urls))
        for url in candidate_urls:
            restaruarnt_url = "https://www.yelp.com"+url
            yield scrapy.Request(restaruarnt_url,callback=self.depth2_parse,dont_filter=True)
            break 
               
        # next_page = response.xpath("//a[contains(@href,'start=')]//@href").getall()[-1]
        page_option = response.xpath("//a[span]/@href").getall()
        next_page = page_option[-3]  
        last_page = page_option[-4]
        if 'start' in last_page and 'start' in next_page: # 爬中间页面
            yield scrapy.Request("https://www.yelp.com"+next_page,callback=self.depth1_parse,dont_filter=True)
        if "start" in next_page and next_page[-2:] == '10': #爬取第一页
            yield scrapy.Request("https://www.yelp.com"+next_page,callback=self.depth1_parse,dont_filter=True)


    def depth2_parse(self, response):
        # crawl one restaurant's detail information
    
        store_item = StoreItem()
        name = response.xpath("//h1/text()").get()
        url = response.request.url
        rating = response.xpath("//div[@aria-label]/@aria-label").get()
        location = response.xpath("//address//text()").getall()
        price = response.xpath("//div//span//span[contains(text(),'$')]/text()").get()
        food_type = response.css("a[href *= '/c/la']::text").getall()
        reviews = response.xpath("//span[@lang]")
        store_item['review']  = []
        for review in reviews:
            store_item['review'].append(review.xpath("text()").get())
            
        review_pages = int(response.xpath('//span[contains(text(),"1 of ")]/text()').get().split()[-1])
        store_item['name'] = name
        store_item['url'] = url
        store_item['rating'] = rating
        store_item['location'] = location
        store_item['food_type'] = food_type
        yield store_item

        ## restrict review pages?
        for i in range(review_pages):
            next_page_url = url+"?"+f"start={i*20}"
            # .... scrapy.Request(next_page_url,callback=self.parse_next_page)
            # 关于item yield的问题
            yield scrapy.Request(next_page_url,callback=self.depth1_parse,dont_filter=True)

            


        


       
        
