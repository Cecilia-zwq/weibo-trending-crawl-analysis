# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DetailData(scrapy.Item):
    views = scrapy.Field()
    discussions = scrapy.Field()
    interactions = scrapy.Field()
    originals = scrapy.Field()
    highest_rank = scrapy.Field()
    duration = scrapy.Field()
    link = scrapy.Field()


class RankData(scrapy.Item):
    time = scrapy.Field()
    rank = scrapy.Field()
    heat = scrapy.Field()


class WeiboItem(scrapy.Item):
    topic = scrapy.Field()
    rank_data = scrapy.Field(serializer=RankData)
    detail_data = scrapy.Field(serializer=DetailData)
    summary = scrapy.Field()
    host = scrapy.Field()
    genre = scrapy.Field()
