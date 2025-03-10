import random
from datetime import datetime

import scrapy


class RossiyaspiderSpider(scrapy.Spider):
    name = "rossiyaspider"
    allowed_domains = ["www.rossiya-airlines.ru"]
    start_urls = ["https://www.rossiya-airlines.ru/onlineboard/onlineboard/departures_board/",
                  "https://www.rossiya-airlines.ru/onlineboard/onlineboard/arrivals_board/"]

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
        routes = response.css('div.searcher-drop').css('ul.searcher-drop-list.shdrop').css(
            'li::attr(onclick)').extract()
        for route in routes:
            relative_url = route.split("'")[1]
            route_url = 'https://www.rossiya-airlines.ru' + relative_url
            yield scrapy.Request(route_url, callback=self.parse_route, headers={
                "User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1)]})

    def parse_route(self, response):
        route_items = response.css('div.schedule-list-item')

        for route_item in route_items:
            departure_point = route_item.xpath('./div[2]/text()').get().strip()
            arrival_point = route_item.xpath('./div[4]/text()').get()

            if not arrival_point or len(arrival_point) < 2:
                arrival_point = route_item.xpath('./div[3]/text()').get()

            route_number = route_item.xpath('./div[1]/text()').get().strip()
            flight = {
                'route': route_number,
                'airline': 'Rossiya',
                'departure_point': departure_point,
                'arrival_point': arrival_point.strip()
            }
            departure_time = self.get_date(route_item.xpath(
                "./div[@class='schedule-list-more']/ul[2]/li[1]/span[2]/text()").get().strip())
            arrival_time = self.get_date(route_item.xpath(
                "./div[@class='schedule-list-more']/ul[3]/li[1]/span[2]/text()").get().strip())

            flight['aircraft_model'] = route_item.xpath(
                "./div[@class='schedule-list-more']/ul/li[1]/span[2]/text()").get().strip()
            flight['business_seats'] = route_item.xpath(
                "./div[@class='schedule-list-more']/ul/li[2]/span[2]/text()").get().strip()
            flight['economy_seats'] = route_item.xpath(
                "./div[@class='schedule-list-more']/ul/li[3]/span[2]/text()").get().strip()
            flight['departure_time'] = departure_time
            flight['arrival_time'] = arrival_time
            yield flight

    def get_date(self, datetime_str):
        date_obj = datetime.strptime(datetime_str, "%d.%m.%y (%H:%M)")
        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
        return formatted_date
