import scrapy
from scrapy.loader import ItemLoader
import json
import sys
import os
from datetime import date
from scrapy.crawler import CrawlerProcess
from scrapy import signals

# --- DATA STRUCTURE DEFINITION ---
class OtomotoField(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    phone_number = scrapy.Field()
    version = scrapy.Field()
    generation = scrapy.Field()
    mileage = scrapy.Field()
    price_currency = scrapy.Field() 
    engine_capacity = scrapy.Field()
    fuel_type = scrapy.Field()
    engine_power = scrapy.Field()
    gearbox = scrapy.Field()
    transmission = scrapy.Field()
    extra_urban_consumption = scrapy.Field()
    urban_consumption = scrapy.Field()
    body_type = scrapy.Field()
    co2_emissions = scrapy.Field()
    door_count = scrapy.Field()
    nr_seats = scrapy.Field()
    color = scrapy.Field()
    new_used = scrapy.Field()
    price = scrapy.Field()
    country_origin = scrapy.Field()
    no_accident = scrapy.Field()
    subregion = scrapy.Field()
    city = scrapy.Field()
    user_id = scrapy.Field()
    ad_id = scrapy.Field()
    title = scrapy.Field() 
    region = scrapy.Field() 
    lon = scrapy.Field()
    lat = scrapy.Field()
    seller_since = scrapy.Field()
    seller_since2 = scrapy.Field()
    current_date = scrapy.Field()
    page_number = scrapy.Field()    
    seller_type = scrapy.Field()    
    seller_name = scrapy.Field()    
    createdAt = scrapy.Field()
    has_vin = scrapy.Field()
    is_imported_car = scrapy.Field()
    has_registration = scrapy.Field()
    service_record = scrapy.Field()
    damaged = scrapy.Field()

# --- CUSTOM MIDDLEWARE TO CATCH 429 ERRORS ---
class TooManyRequestsStopper:
    """
    Intercepts responses. If a 429 status is detected, it stops the spider immediately.
    """
    def process_response(self, request, response, spider):
        if response.status == 429:
            spider.logger.critical(">>> [CRITICAL] 429 Too Many Requests detected! Stopping spider...")
            spider.crawler.engine.close_spider(spider, 'http_429_ban')
            return response
        return response

class OtomotoSpider(scrapy.Spider):
    name = 'otomoto_batch'
    
    # --- SPIDER SETTINGS ---
    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,             
        'CONCURRENT_REQUESTS': 40,        
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0, 
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [403, 500, 502, 503, 504],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            f'{__name__}.TooManyRequestsStopper': 600,
        },
        'FAKEUSERAGENT_PROVIDERS': [
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',
            'scrapy_fake_useragent.providers.FakerProvider',
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',
        ],
        'COOKIES_ENABLED': False,
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, urls=None, *args, **kwargs):
        super(OtomotoSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls if urls else []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(OtomotoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        car_pages = response.css('a[href*="otomoto.pl/osobowe/oferta"]::attr(href)').getall()
        
        try:
            page_num = response.url.split('page=')[-1]
        except:
            page_num = "?"

        if not car_pages:
            self.logger.warning(f"[EMPTY PAGE] No ads found on page {page_num}. Possible Soft Ban.")
            return

        self.logger.info(f"[PAGE {page_num}] Found {len(car_pages)} ads.")

        for car_page in car_pages:
            yield response.follow(car_page, self.parse_car_page, cb_kwargs={'page_num': page_num})

    def parse_car_page(self, response, page_num):
        loader = ItemLoader(OtomotoField(), response=response)     
        
        query = 'script:contains("pageProps")::text'
        js_code = response.css(query).get()
        if not js_code: return 

        js_code = js_code.replace('data = (', '').replace(');', '')
        
        try:
            json_data = json.loads(js_code)
            if "props" in json_data:
                advert = json_data.get("props", {}).get("pageProps", {}).get("advert", {})
            else:
                advert = json_data.get("pageProps", {}).get("advert", {})
            params = advert.get("parametersDict", {})
        except Exception:
            return

        today = date.today().strftime("%d/%m/%Y")
        loader.add_value('current_date', today)
        loader.add_value('page_number', page_num)
        loader.add_value('ad_id', str(advert.get("id", "")))
        loader.add_value('url', advert.get("url", response.url))
        loader.add_value('title', advert.get("title", ""))
        loader.add_value('createdAt', advert.get("createdAt", ""))
        
        price_obj = advert.get("price", {})
        loader.add_value('price', str(price_obj.get("value", "")))
        loader.add_value('price_currency', price_obj.get("currency", ""))

        seller = advert.get("seller", {})
        loader.add_value('seller_type', seller.get("type", ""))
        loader.add_value('user_id', str(seller.get("id", "")))
        loader.add_value('seller_name', seller.get("name", ""))
        
        loc = seller.get("location", {})
        loader.add_value('city', loc.get("city", ""))
        loader.add_value('region', loc.get("region", ""))
        map_loc = loc.get("map", {})
        loader.add_value('lon', str(map_loc.get("longitude", "")))
        loader.add_value('lat', str(map_loc.get("latitude", "")))

        badges = seller.get("featuresBadges", [])
        if len(badges) > 1: loader.add_value('seller_since', badges[1])
        if len(badges) > 2: loader.add_value('seller_since2', badges[2])

        def get_param(key, field="value"):
            p_data = params.get(key, {})
            values_list = p_data.get("values", [])
            if values_list and isinstance(values_list, list):
                return values_list[0].get(field, "")
            return ""

        loader.add_value('year', get_param("year"))
        loader.add_value('mileage', get_param("mileage"))
        loader.add_value('engine_capacity', get_param("engine_capacity"))
        loader.add_value('engine_power', get_param("engine_power"))
        loader.add_value('door_count', get_param("door_count"))
        loader.add_value('nr_seats', get_param("nr_seats"))
        loader.add_value('has_vin', get_param("has_vin"))
        loader.add_value('is_imported_car', get_param("is_imported_car"))
        loader.add_value('has_registration', get_param("has_registration"))
        loader.add_value('no_accident', get_param("no_accident"))
        loader.add_value('service_record', get_param("service_record"))
        loader.add_value('damaged', get_param("damaged"))
        loader.add_value('co2_emissions', get_param("co2_emissions"))
        loader.add_value('extra_urban_consumption', get_param("extra_urban_consumption"))
        loader.add_value('urban_consumption', get_param("urban_consumption"))

        loader.add_value('brand', get_param("make", "label"))
        loader.add_value('model', get_param("model", "label"))
        loader.add_value('version', get_param("version", "label"))
        loader.add_value('generation', get_param("generation", "label"))
        loader.add_value('fuel_type', get_param("fuel_type", "label"))
        loader.add_value('gearbox', get_param("gearbox", "label"))
        loader.add_value('transmission', get_param("transmission", "label"))
        loader.add_value('body_type', get_param("body_type", "label"))
        loader.add_value('color', get_param("color", "label"))
        loader.add_value('country_origin', get_param("country_origin", "label"))
        loader.add_value('new_used', get_param("new_used", "label"))

        ad_id = str(advert.get("id", ""))
        if ad_id:
            phone_url = f"https://www.otomoto.pl/ajax/misc/contact/multi_phone/{ad_id}/0/"
            yield scrapy.Request(phone_url, callback=self.phone_parse, meta={'loader': loader})
        else:
            yield loader.load_item()

    def phone_parse(self, response):
        loader = response.meta['loader']
        try:
            data = json.loads(response.text)
            phone_val = data.get("value", "no_phone")
            if isinstance(phone_val, str):
                phone_val = phone_val.replace("<p>", "").replace("</p>", "").strip()
            loader.add_value('phone_number', phone_val)
        except:
            loader.add_value('phone_number', "no_phone")
        yield loader.load_item()

    def spider_closed(self, spider, reason):
        if reason == 'http_429_ban':
            print(f">>> [WORKER] Stopped due to 429 Too Many Requests.")
            sys.exit(429)

        stats = self.crawler.stats
        item_count = stats.get_value('item_scraped_count', 0)
        
        if item_count == 0:
            print(f">>> [WORKER] Spider finished but found 0 ads (Soft Ban detected).")
            sys.exit(5) 
        else:
            print(f">>> [WORKER SUCCESS] Items downloaded: {item_count}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        # We now require 3 arguments: start, end, output_filename
        print("Usage: python otomoto_spider_batch_v1.py <start_page> <end_page> <output_file>")
        sys.exit(1)
        
    start_p = int(sys.argv[1])
    end_p = int(sys.argv[2])
    output_filename = sys.argv[3]
    
    # Generate URLs for the current batch
    batch_urls = [f'https://www.otomoto.pl/osobowe?page={i}' for i in range(start_p, end_p + 1)]
    
    process = CrawlerProcess({
        'FEEDS': {
            output_filename: {  # Dynamic filename from argument
                'format': 'csv',
                'overwrite': True,
                'encoding': 'utf8',
            }
        }
    })
    
    process.crawl(OtomotoSpider, urls=batch_urls)
    process.start()