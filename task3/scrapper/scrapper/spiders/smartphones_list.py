# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from lxml import html as html_parser


class SmartphonesListSpider(scrapy.Spider):
    name = 'smartphones_list'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.data = pd.DataFrame(
    #         columns=[
    #             'name', 'screen_size',
    #             'min_price', 'max_price',
    #             'thickness', 'nfc',
    #             'num_1', 'num_2', 'num_3', 'num_4'
    #         ]
    #     )

    def start_requests(self):
        for i in range(0, 51):
            #url = 'https://market.yandex.ru/catalog--mobilnye-telefony/54726/list?hid=91491&glfilter=16816515%3A16816517&onstock=1&local-offers-first=0&page={}'.format(i)
            url = 'https://www.e-katalog.ru/ek-list.php?katalog_=122&page_={}&presets_=1358'.format(i)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for model in response.xpath('//div[@class="model-short-div list-item--goods   "]'):
            opinions = []
            for t in model.xpath('.//td[@class="short-opinion-icons"]/*/sub/text()'):
                opinions.append(int(t.get()))

            if len(opinions) == 0:
                # no reviews - no sense to save
                continue

            tags = []
            for t in model.xpath('.//div[@class="m-s-f1 no-mobile"]/*/text()'):
                tags.append(t.get())
            has_nfc = ('NFC' in tags)

            descr = []
            for t in model.xpath('.//div[@class="m-s-f2 no-mobile"]/div/text()'):
                descr.append(t.get())

            thickness = 0
            for d in descr:
                splitted = d.split()
                if len(splitted) > 2 and splitted[-1] == 'мм':
                    thickness = int(splitted[-2])
            if thickness == 0:
                continue

            prices = []
            for t in model.xpath('.//div[@class="model-price-range"]/a/span/text()'):
                prices.append(int(''.join(t.get().split())))
            if len(prices) == 0:
                prices.append(int(''.join(model.xpath('.//div[@class="pr31 ib"]/span/text()').extract_first().split())))
            yield {
                'name': model.xpath('.//a[@class="model-short-title no-u"]/span[@class="u"]/text()').extract_first(),
                'num_1': opinions[0], 'num_2': opinions[1], 'num_3': opinions[2], 'num_4': opinions[3],
                'nfc': has_nfc,
                'screen_size': float(descr[0].split()[0]),
                'thickness': thickness,
                'min_price': prices[0], 'max_price': prices[-1]
            }

