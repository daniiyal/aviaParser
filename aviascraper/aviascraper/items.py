# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AviascraperItem(scrapy.Item):
    flight_number = scrapy.Field()  # Номер рейса
    airline = scrapy.Field()  # Авиакомпания
    aircraft_model = scrapy.Field()  # Модель самолета
    departure_point = scrapy.Field()  # Пункт вылета
    arrival_point = scrapy.Field()  # Пункт прилета
    departure_time = scrapy.Field()  # Время вылета
    arrival_time = scrapy.Field()  # Время прилета
