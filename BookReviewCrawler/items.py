# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Book(scrapy.Item):
    BookID = scrapy.Field()
    Link = scrapy.Field()
    Title = scrapy.Field()
    Author = scrapy.Field()
    Rate = scrapy.Field()
    Description = scrapy.Field()
    Review = scrapy.Field()
