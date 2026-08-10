"""
Abstract Base Scraper establishing the contract for all scraping engines.
Future scrapers (e.g. PlaywrightScraper, AmazonScraper, API Scraper) will inherit from BaseScraper.
"""

from abc import ABC, abstractmethod
from src.models.product import PriceResult, StoreConfig, ProductConfig


class BaseScraper(ABC):
    """
    Abstract Base Class for product price scrapers.
    """

    @abstractmethod
    def fetch_price(self, product: ProductConfig, store_key: str, store: StoreConfig) -> PriceResult:
        """
        Fetches and extracts price for a specified product from a store.

        :param product: ProductConfig containing product metadata & target price
        :param store_key: Unique identifier key for store in config
        :param store: StoreConfig containing URL and CSS selector
        :return: PriceResult object
        """
        pass
