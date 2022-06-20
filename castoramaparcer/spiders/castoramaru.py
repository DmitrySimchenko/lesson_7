import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from castoramaparcer.items import CastoramaparcerItem


class CastoramaruSpider(scrapy.Spider):
    name = 'castoramaru'
    allowed_domains = ['castorama.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.castorama.ru/catalogsearch/result/?q={kwargs.get("query")}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("(//a[@class='next i-next']/@href)[1]").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains(@class, "product-card")][2]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=CastoramaparcerItem(), response=response)
        loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        loader.add_xpath('price', '//span[@class="price"]/span/span/text()')
        loader.add_xpath('photos', '//img[contains(@class, "top-slide__img")]/@data-src')
        loader.add_value('url', response.url)
        yield loader.load_item()
