from scrapy.crawler import CrawlerProcess

from surplex_spider import SurplexSpider


def run_spider_via_python_script():
    process = CrawlerProcess()
    process.crawl(SurplexSpider)
    process.start()


if __name__ == "__main__":
    run_spider_via_python_script()
