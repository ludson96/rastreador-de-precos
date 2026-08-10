"""
Domain models for products, store configurations, and price scraping results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ScrapingStatus(str, Enum):
    SUCCESS = "SUCCESS"
    TARGET_REACHED = "TARGET_REACHED"
    ABOVE_TARGET = "ABOVE_TARGET"
    HTTP_ERROR = "HTTP_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT = "TIMEOUT"
    SELECTOR_NOT_FOUND = "SELECTOR_NOT_FOUND"
    INVALID_PRICE = "INVALID_PRICE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class StoreConfig:
    """Configuration for a specific store selling a product."""
    name: str
    url: str
    selector: str
    enabled: bool = True
    product_identifier: Optional[str] = None
    scraper_type: str = "generic"  # Allows extending to custom scrapers or Playwright


@dataclass
class ProductConfig:
    """Configuration for a product to monitor across multiple stores."""
    id: str
    name: str
    model: str
    target_price: float
    capacity: Optional[str] = None
    voltage: Optional[str] = None
    enabled: bool = True
    stores: Dict[str, StoreConfig] = field(default_factory=dict)


@dataclass
class PriceResult:
    """Scraping execution result for a single store check."""
    product_id: str
    product_name: str
    store_key: str
    store_name: str
    target_price: float
    store_url: Optional[str] = None
    current_price: Optional[float] = None
    status: ScrapingStatus = ScrapingStatus.UNKNOWN_ERROR
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_target_reached(self) -> bool:
        """Returns True if the current price is less than or equal to the target price."""
        if self.current_price is not None and self.target_price is not None:
            return self.current_price <= self.target_price
        return False

