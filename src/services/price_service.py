"""
Price Service orchestrates the monitoring of configured products across active store scrapers.
"""

from typing import List, Dict, Type, Optional
from src.models.product import ProductConfig, PriceResult
from src.scrapers.base import BaseScraper
from src.scrapers.generic_scraper import GenericScraper
from src.services.notification_service import NotificationService
from src.database.history import PriceHistoryDB


class PriceService:
    """
    Service responsible for coordinating product monitoring, executing scrapers per store,
    handling errors independently, persisting history to SQLite, and triggering notifications.
    """

    def __init__(
        self,
        products: List[ProductConfig],
        scrapers: Dict[str, BaseScraper] = None,
        notification_service: NotificationService = None,
        db_history: Optional[PriceHistoryDB] = None
    ):
        self.products = products
        self.scrapers = scrapers or {
            "generic": GenericScraper()
        }
        self.notification_service = notification_service or NotificationService()
        self.db_history = db_history or PriceHistoryDB()

    def run_check(self, send_daily_report: bool = False) -> List[PriceResult]:
        """
        Executes a single check across all active products and stores.
        Errors in one store do not break execution for other stores.
        Saves results to SQLite and triggers notifications.
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
            # 1. Save history to SQLite
            try:
                self.db_history.save_results(results)
            except Exception as e:
                print(f"[PriceService] Erro ao salvar histórico no SQLite: {e}")

            # 2. Handle notifications
            if send_daily_report:
                for notifier in self.notification_service.notifiers:
                    if hasattr(notifier, "send_daily_report"):
                        notifier.send_daily_report(results, db_history=self.db_history)
            else:
                self.notification_service.send_notifications(results)

        return results

