import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankgantrisch.items import Article


class gantSpider(scrapy.Spider):
    name = 'gant'
    start_urls = ['https://www.bankgantrisch.ch/service/news/news-list.html']

    def parse(self, response):
        links = response.xpath('//div[@class="news-list-view"]//h4/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="last next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="header"]/h2/text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//span[@class="news-date news-list-date"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="news-text"]//text()').getall()
        content = [text.strip() for text in content if text.strip()]
        content = "\n".join(content[:-2]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
