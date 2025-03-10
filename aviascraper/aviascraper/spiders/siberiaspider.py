import random
from datetime import datetime

import scrapy


class SiberiaspiderSpider(scrapy.Spider):
    name = "siberiaspider"
    allowed_domains = ["s7.ru"]
    start_urls = ["https://www.s7.ru/ru/flights/"]

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    ]

    def parse(self, response):
        routes = response.xpath("//div[@class='flight-gridContainer']/a")
        for route in routes:
            relative_url = route.css('a').attrib['href']
            route_url = 'https://www.s7.ru' + relative_url
            yield scrapy.Request(route_url, callback=self.parse_route, headers={
                "User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1)]})

    def parse_route(self, response):
        route = response.css('div.hero_text').css('h1::text').get().split()

        route_items = response.css('div.itemInnerAirway')
        for route_item in route_items:
            departure_point = route_item.xpath('./div[2]/div[2]/div[1]/b/text()').get() + route_item.xpath(
                './div[2]/div[2]/div[1]/text()').get()
            arrival_point = route_item.xpath('./div[2]/div[2]/div[3]/b/text()').get() + route_item.xpath(
                './div[2]/div[2]/div[3]/text()').get()
            flight = {
                'route': route[1] + " " + route[2],
                'airline': 'S7',
                'departure_point': departure_point,
                'arrival_point': arrival_point
            }
            route_date = route_item.xpath('./div/div/text()').get()
            departure_time = self.get_date(route_date, route_item.xpath('./div/div[1]/div[1]/text()').get())
            arrival_time = self.get_date(route_date, route_item.xpath('./div/div[1]/div[3]/text()').get())
            flight['aircraft_model'] = route_item.xpath('./div[3]/p/text()').get() + ' ' + route_item.xpath(
                './div[3]/div/text()').get()
            flight['departure_time'] = departure_time
            flight['arrival_time'] = arrival_time
            yield flight

    def get_date(self, date_str, time_str):
        months = {
            'января': 'january',
            'ферваля': 'february',
            'марта': 'march',
            'апреля': 'april',
            'мая': 'may',
            'июня': 'june',
            'июля': 'july',
            'августа': 'august',
            'сентября': 'september',
            'октября': 'october',
            'ноября': 'november',
            'декабря': 'december'
        }
        new_date = date_str.split()[0] + ' ' + months.get(date_str.split()[1])
        date_obj = datetime.strptime(new_date, "%d %B")
        time_obj = datetime.strptime(time_str, "%H:%M")
        date_obj = date_obj.replace(year=datetime.now().year)
        date_obj = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute)
        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
        return formatted_date
