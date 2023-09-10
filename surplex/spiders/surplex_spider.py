# -*- coding: utf-8 -*-
import base64

from scrapy import Request
from scrapy import Spider

from update_database import UpdateDatabase
from utils import *


class SurplexSpider(Spider):
    name = "surplex_spider"
    base_url = 'https://www.surplex.com/'
    file_path = '../output/surplex_auctions.csv'
    auction_categories_url = 'https://www.surplex.com/es/a.html'

    start_urls = [
        auction_categories_url,
    ]

    handle_httpstatus_list = [
        400, 401, 402, 403, 404, 405, 406, 407, 409,
        500, 501, 502, 503, 504, 505, 506, 507, 509,
    ]

    csv_headers = [
        "auction_id", "name", "denomination", "article_number", "maker", "model", "production_year",
        "availability", "commission_percentage", "disassembly_loading_costs", "total_price",
        "transportation_expenses", "delivery_conditions", "payment_conditions", "dimensions",
        "weight_approx", "batch_name", "batch_link", "lot_no", "document_links", "inspection",
        "pickup", "category", "type", "start_date", "end_date", "followers", "total_bids",
        "current_bid", "bid_up", "bid_option_1", "bid_option_2", "bid_option_3", "sku", "city",
        "state", "country", "location", "description", "item_details", "technical_details",
        "expense_benefits", "auction_details", "image_links", "agent_name", "agent_role",
        "agent_phone", "agent_mobile", "agent_email", "url",
    ]

    feeds = {
        file_path: {
            'format': 'csv',
            'encoding': 'utf8',
            'store_empty': False,
            'fields': csv_headers,
            'indent': 4,
            'overwrite': True,
        }
    }

    custom_settings = {
        'FEEDS': feeds,
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 3,
    }

    headers = {
        'authority': 'www.surplex.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }

    cookies = {}

    meta = {
        'handle_httpstatus_list': handle_httpstatus_list,
    }

    seen_urls = []

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.db = UpdateDatabase()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_categories, headers=self.headers)

    def parse_categories(self, response, **kwargs):
        return response.follow_all(css='h5.cardAuction__title a',
                                   callback=self.parse_listings,
                                   headers=self.headers,
                                   meta=self.meta,
                                   )

    def parse_listings(self, response):
        yield from [response.follow(url=url_s, callback=self.parse_details, meta=self.meta, headers=self.headers)
                    for url_s in response.css('.cardProduct__title a') if url_s]

        yield from [response.follow(url=self.get_decoded_url(encoded_url),
                                    callback=self.parse_details,
                                    headers=self.headers,
                                    meta=self.meta)
                    for encoded_url in response.css('span.item-url::attr(data-redirect)').getall()]

        yield from response.follow_all(css='link[rel="next"]',
                                       callback=self.parse_listings,
                                       dont_filter=True,
                                       headers=self.headers,
                                       meta=response.meta)

    def parse_details(self, response):
        item = {}
        item['auction_id'] = self.get_meta_value(response, "bc:auction-id")
        item['name'] = self.get_meta_value(response, "bc:title")
        item['denomination'] = self.get_key_value(response, "Denominación")
        item['article_number'] = self.get_key_value(response, "Número de artículo")
        item['maker'] = self.get_meta_value(response, "bc:brand")
        item['model'] = self.get_meta_value(response, "bc:model")
        item['production_year'] = self.get_key_value(response, "Año de fabricación")
        item['availability'] = self.get_key_value(response, "Disponibilidad")
        item['location'] = clean(self.get_key_value(response, "Lugar").split('Mostrar en el mapa')[0]).rstrip(',')
        item['commission_percentage'] = self.get_key_value(response, "de comisión")
        item['disassembly_loading_costs'] = self.get_key_value(response, "Gastos de desmontaje y carga (obligatorio)")
        item['total_price'] = self.get_key_value(response, "Precio total")
        item['transportation_expenses'] = self.get_key_value(response, "Gastos de transporte")
        item['delivery_conditions'] = self.get_key_value(response, "Condiciones de entrega")
        item['payment_conditions'] = self.get_key_value(response, "Condiciones de pago")
        item['dimensions'] = self.get_key_value(response, "Dimensiones ")
        item['weight_approx'] = self.get_key_value(response, "Peso aprox")
        item['batch_name'] = self.get_key_value(response, "Subasta")
        item['batch_link'] = self.get_batch_link(response, "Subasta")
        item['lot_no'] = self.get_key_value(response, "lote núm.")
        item['document_links'] = self.get_document_links(response)
        item['inspection'] = self.get_key_value(response, "Inspección")
        item['pickup'] = self.get_key_value(response, "Recogida")
        item['category'] = self.get_meta_value(response, "bc:category")
        item['type'] = self.get_meta_value(response, "bc:type")
        item['start_date'] = clean_date(self.get_meta_value(response, "bc:start"))
        item['end_date'] = clean_date(self.get_meta_value(response, "bc:end"))
        item['followers'] = self.get_meta_value(response, "bc:watchlist")
        item['total_bids'] = self.get_meta_value(response, "bc:bidamount")
        item['current_bid'] = self.get_meta_value(response, "bc:price")
        item['bid_up'] = self.get_bid_up(response)
        item['sku'] = self.get_meta_value(response, "bc:sku")
        item['city'] = self.get_meta_value(response, "bc:city")
        item['state'] = self.get_meta_value(response, "bc:countryiso2")
        item['country'] = self.get_meta_value(response, "bc:country")
        item['description'] = self.get_description_html(response)
        item['image_links'] = self.get_image_urls(response)
        item['item_details'] = self.get_item_details(response)
        item['technical_details'] = self.get_technical_details(response)
        item['expense_benefits'] = self.get_expenses_benefits(response)
        item['auction_details'] = self.get_auction_details(response)
        item['bid_option_1'] = self.get_bid_option_1(response)
        item['bid_option_2'] = self.get_bid_option_2(response)
        item['bid_option_3'] = self.get_bid_option_3(response)
        item['agent_name'] = self.get_agent_name(response)
        item['agent_role'] = self.get_agent_role(response)
        item['agent_phone'] = self.get_agent_phone(response)
        item['agent_mobile'] = self.get_agent_mobile(response)
        item['agent_email'] = self.get_agent_email(response)
        item['url'] = response.url

        self.db.insert_auction_db(item)
        return item

    def get_description_html(self, response):
        desc = response.css('#collapseDescription').get('')
        return f'{desc}\n{self.get_document_links(response)}'.strip() or self.get_meta_description(response)

    def get_meta_description(self, response):
        return response.css('[property="og:description"]::attr(content)').get('')

    def get_description(self, response):
        return join_seq(response.css('#collapseDescription::text').getall())

    def get_image_urls(self, response):
        return ";\n".join(url.lstrip('//') for url in response.css('#gallery-main ::attr(data-src)').getall()
                          if url and '/images/' in url)

    def get_start_price(self, response):
        return clean_price(response.css('.lot-detail.lot-detail--starting-price .lot-detail__value::text').get())

    def get_document_links(self, response):
        encoded_strings = response.css('.table--docLink .link::attr(data-redirect)').getall()
        return ",\n".join([response.urljoin(base64.b64decode(e).decode('utf-8')) for e in encoded_strings if e])

    def get_key_value(self, response, key):
        return join_seq(response.css(f'dt:contains("{key}") + dd ::text').getall())

    def get_meta_value(self, response, key):
        return response.css(f'[name="{key}"]::attr(content)').get()

    def get_batch_link(self, response, key):
        return response.css(f'dt:contains("{key}") + dd a.acc-auction-link::attr(href)').get()

    def get_bid_up(self, response):
        return response.css('input[name="search"]::attr(value)').get()

    def get_item_details(self, response):
        return clean(response.css('#collapseOffer').get())

    def get_technical_details(self, response):
        return clean(response.css('#collapseTechnical').get())

    def get_expenses_benefits(self, response):
        return clean(response.css('#collapseCosts').get())

    def get_auction_details(self, response):
        return clean(response.css('#collapseAuction').get())

    def get_agent_name(self, response):
        return clean(response.css('.contact__dataName::Text').get())

    def get_agent_role(self, response):
        return clean(response.css('.contact__dataRole::text').get())

    def get_agent_phone(self, response):
        return response.css('[data-track-label="phone"]::attr(href)').get('')[4:]

    def get_agent_mobile(self, response):
        return response.css('[data-track-label="mobile"]::attr(href)').get('')[4:]

    def get_agent_email(self, response):
        return response.css('.contact__dataInfoBarItem--mail a::attr(href)').get('')[7:].split('?')[0].strip()

    def get_bid_option_1(self, response):
        return "".join(response.css('.bidBox__agentItem ::attr(data-track-value)').getall()[:1])

    def get_bid_option_2(self, response):
        return "".join(response.css('.bidBox__agentItem ::attr(data-track-value)').getall()[1:2])

    def get_bid_option_3(self, response):
        return "".join(response.css('.bidBox__agentItem ::attr(data-track-value)').getall()[-1:])

    def get_decoded_url(self, encoded_url):
        return str(base64.b64decode(encoded_url), 'utf-8')
