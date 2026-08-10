"""
Price Service orchestrates the monitoring of configured products across active store scrapers.
"""

from typing import List, Dict, Type
from src.models.product import ProductConfig, PriceResult
from src.scrapers.base import BaseScraper
from src.scrapers.generic_scraper import GenericScraper
from src.services.notification_service import NotificationService


class PriceService:
    """
    Service responsible for coordinating product monitoring, executing scrapers per store,
    handling errors independently, and triggering notifications.
    """

    def __init__(
        self,
        products: List[ProductConfig],
        scrapers: Dict[str, BaseScraper] = None,
        notification_service: NotificationService = None
    ):
        self.products = products
        self.scrapers = scrapers or {
            "generic": GenericScraper()
        }
        self.notification_service = notification_service or NotificationService()

    def run_check(self) -> List[PriceResult]:
        """
        Executes a single check across all active products and stores.
        Errors in one store do not break execution for other stores.
        """
        results: List[PriceResult] = []

        for product in self.products:
            if not product.enabled:
                continue

            for store_key, store in product.stores.items():
                if not store.enabled:
                    continue

                scraper = self.scrapers.get(store.scraper_type, self.scrapers["generic"])
                result = scraper.fetch_price(product, store_key, store)
                results.append(result)

        if results:
            self.notification_service.send_notifications(results)

        return results
