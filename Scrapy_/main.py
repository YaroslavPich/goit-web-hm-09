import json
from typing import Any

import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.item import Item, Field


class QuoteItem(Item):
	quote = Field()
	author = Field()
	tags = Field()


class AuthorItem(Item):
	fullname = Field()
	born_date = Field()
	born_location = Field()
	description = Field()


class DataPipeline:
	quotes = []
	authors = []

	def process_item(self, item, spider):
		adapter = ItemAdapter(item)
		if 'fullname' in adapter.keys():
			self.authors.append(dict(adapter))
		if 'quote' in adapter.keys():
			self.quotes.append(dict(adapter))
		return item

	def close_spider(self, spider):
		with open('quotes.json', 'w', encoding='utf-8') as fd:
			json.dump(self.quotes, fd, ensure_ascii=False, indent=2)
		with open('authors.json', 'w', encoding='utf-8') as fd:
			json.dump(self.authors, fd, ensure_ascii=False, indent=2)


class QuoteSpider(scrapy.Spider):
	name = "get_quotes"
	allowed_domains = ["quotes.toscrape.com"]
	start_urls = ["https://quotes.toscrape.com/"]
	custom_settings = {"ITEM_PIPELINES": {DataPipeline: 300}}

	def parse(self, response: Response, **kwargs: Any):
		for q in response.xpath("/html//div[@class='quote']"):
			quote = q.xpath("span[@class='text']/text()").get().strip()
			author = q.xpath("span/small[@class='author']/text()").get().strip()
			tags = q.xpath("div[@class='tags']/a[@class='tag']/text()").extract()
			yield QuoteItem(tags=[tag.strip() for tag in tags], author=author, quote=quote)
			yield response.follow(url=self.start_urls[0] + q.xpath("span/a/@href").get(), callback=self.parse_author)
		next_link = response.xpath("/html//li[@class='next']/a/@href").get()
		if next_link:
			yield scrapy.Request(url=response.urljoin(next_link), callback=self.parse)

	@classmethod
	def parse_author(cls, response: Response, **kwargs: Any):
		content = response.xpath("/html//div[@class='author-details']")
		fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
		born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
		born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
		description = " ".join(content.xpath("div[@class='author-description']/text()").extract()).strip()
		yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)


if __name__ == '__main__':
	process = CrawlerProcess()
	process.crawl(QuoteSpider)
	process.start()
