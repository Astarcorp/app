# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

def remove_whitespace(value):
	return value.strip()

class JokeItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	joke_text = scrapy.Field(
		input_processor = MapCompose(remove_tags, remove_whitespace), #removing HTML tags and whitespace
		output_processor = TakeFirst()
	)

class QuoteItem(scrapy.Item):
	title = scrapy.Field()
	author = scrapy.Field()
	tag = scrapy.Field()

class HRPolicyRelationItem(scrapy.Item):
	relationship = scrapy.Field()
	name = scrapy.Field()
	policyname = scrapy.Field()

class DocumentItem(scrapy.Item):
	document = scrapy.Field()
	policyname = scrapy.Field()