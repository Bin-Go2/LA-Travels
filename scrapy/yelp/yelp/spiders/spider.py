from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import time

class moviespider(CrawlSpider):
    name = "yelp"

    allowed_domains = ['yelp.com']
    # seed url
    # type of comedy is limited to movie and show
    # genres is limited to comedy
    start_urls = ['https://www.yelp.com/search?find_desc=Restaurants&find_loc=Los+Angeles%2C+CA',]
    # limit the nuexit()mber of movie we
    custom_settings = {'CLOSESPIDER_ITEMCOUNT': 50}

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths=("//a[.//span[contains(@class, 'right')] and .//svg[@xmlns='http://www.w3.org/2000/svg']]")
        ), follow = True, callback="parse_listpage"),
    )
    def parse_listpage(self,response):
        # page that show the list of comedy movie
        # # links for each comedy movie
        queues = response.css('h4 span a[href*="/biz/"]::attr(href)').getall()
        time.sleep(.5)
        for queue in queues:
            yield response.follow(queue,callback=self.parse_detail)

    def parse_detail(self, response):
        time.sleep(.3)
        data = {}
        data["url"] = response.url
        data["name"] = response.css("h1::text").get()
        data["rate"] = response.xpath("//div[contains(@role, 'img') and contains(@aria-label, 'star')]//@aria-label").getall()[0]
        # use the food type find the all text file
        title_text = response.xpath("//div[./span/span/a[contains(@href,'/c/la')]]//span/text()").getall()

        data["location"] = response.xpath("//address//text()").getall()
        
        if title_text:
            for item in title_text:
                if "$" in item:
                    data["price"] = item
                elif "AM" in item or "PM" in item:
                    data["open_time"] = item
        data["food_type"] = response.css("a[href *= '/c/la']::text").getall()
        review = response.xpath("//ul/li//span/text()").getall()
        data["review"] = response.xpath("//ul/li//span/text()").getall() 
        yield data