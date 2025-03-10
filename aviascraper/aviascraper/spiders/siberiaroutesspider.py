import scrapy
import random

class SiberiaRoutesSpider(scrapy.Spider):
    name = "siberiaroutesspider"
    allowed_domains = ["s7.ru"]
    start_urls = ["https://www.s7.ru/ru/flights/"]

    def parse(self, response):
        routes = response.css('p.leading-6.text-regular-16.mb-2')
        route_numbers = []

        for route in routes:
            route_numbers.append(route.css('p::text').get().split()[1])

        with open("s7Routes.txt", "w") as file:
            for route_number in route_numbers:
                file.write(route_number + "\n")
