import logging
import random
from datetime import datetime

import pandas as pd
import scrapy
from httpcore import TimeoutException
from scrapy_playwright.page import PageMethod

class AeroflotspiderSpider(scrapy.Spider):
    name = "aeroflotspider"
    allowed_domains = ["flights.aeroflot.ru"]
    start_urls = ["https://flights.aeroflot.ru/ru-ru/onlineboard/"]

    date = '20250310'

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
        routes_list = self.get_routes()
        print(routes_list)
        for route in routes_list[:1]:
            for dest, arr in route.items():
                route_url = 'https://flights.aeroflot.ru/ru-ru/onlineboard/route/' + dest + "-" + arr + "-" + self.date
                yield scrapy.Request(route_url, meta=dict(playwright=True, playwright_include_page=True),
                             callback=self.parse_route, headers={
                "User-Agent": self.user_agent_list[random.randint(0, len(self.user_agent_list) - 1)]})

    async def parse_route(self, response):

        page = response.meta['playwright'].get('playwright_page')
        await page.wait_for_selector(xpath="//div[contains(@class, 'flight-list-item')]")

        route_items = response.xpath("//div[contains(@class, 'flight-list-item')]")

        logging.info(route_items)

        for route_item in route_items:

            if "selected" not in route_item.attrib['class']:
                route_item.click()
                await page.wait_for_selector(xpath='./board-flight-header/div/operator-logo-and-model/text/span')

            route_item = response.xpath("./")

            departure_point = (
                    route_item.xpath('./board-flight-header/div/station/div/text/span/text()').get().strip() + ' ' +
                    route_item.xpath(
                        './board-flight-header/div/station/div/terminal-link/span/*[1]/text()').get().strip())

            arrival_point = (route_item.xpath(
                './board-flight-header/div/station[2]/div/text/span/text()').get().strip() + ' ' +
                             route_item.xpath(
                                 './board-flight-header/div/station[2]/div/terminal-link/span/*[1]/text()').get().strip())

            route_number = route_item.xpath("./board-flight-header/div/div/div/text()").get().strip()

            flight = {
                'route': route_number,
                'airline': 'Aeroflot',
                'departure_point': departure_point,
                'arrival_point': arrival_point
            }

            departure_time = self.get_date(
                route_item.xpath(
                    "./board-flight-header/div/time-group[1]/div/div/div/text/span/text()").get().strip())
            arrival_time = self.get_date(
                route_item.xpath(
                    "./board-flight-header/div/time-group[2]/div/div/div/text/span/text()").get().strip())

            flight['aircraft_model'] = route_item.xpath(
                "./board-flight-header/div/operator-logo-and-model/text/span/text()").get().strip()
            flight['departure_time'] = departure_time
            flight['arrival_time'] = arrival_time

            yield flight

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()


    def get_date(self, time_str):
        date_obj = datetime.strptime(self.date, "%Y%m%d")
        time_obj = datetime.strptime(time_str, "%H:%M")
        date_obj = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute)
        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
        return formatted_date

    def get_routes(self):
        df = pd.read_excel(
            "C:\\Users\\Daniyal\\PycharmProjects\\aviaParser\\aviascraper\\aviascraper\\routes_table.xlsx",
            engine='openpyxl', usecols=(1, 3))

        routes_list = []

        for index, row in df.iterrows():
            routes_list.append({row['Код отправления']: row['Код прибытия']})

        return routes_list
