"""
Generic Scraper implementation using requests and BeautifulSoup.
Extracts product prices based on configured URL and CSS selector.
"""

import requests
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper
from src.models.product import ProductConfig, StoreConfig, PriceResult, ScrapingStatus
from src.utils.price_parser import parse_brl_price

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)


class GenericScraper(BaseScraper):
    """
    Generic scraper leveraging HTTP GET (requests) and CSS selectors (BeautifulSoup).
    """

    def __init__(self, timeout: int = 10, user_agent: str = DEFAULT_USER_AGENT):
        self.timeout = timeout
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def fetch_price(self, product: ProductConfig, store_key: str, store: StoreConfig) -> PriceResult:
        result = PriceResult(
            product_id=product.id,
            product_name=product.name,
            store_key=store_key,
            store_name=store.name,
            store_url=store.url,
            target_price=product.target_price,
        )

        try:
            response = requests.get(store.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            result.status = ScrapingStatus.TIMEOUT
            result.error_message = f"Timeout ({self.timeout}s) ao acessar {store.url}"
            return result
        except requests.exceptions.ConnectionError:
            result.status = ScrapingStatus.CONNECTION_ERROR
            result.error_message = f"Falha de conexão com a loja em {store.url}"
            return result
        except requests.exceptions.HTTPError as err:
            result.status = ScrapingStatus.HTTP_ERROR
            result.error_message = f"Erro HTTP ({response.status_code}) em {store.url}: {err}"
            return result
        except requests.exceptions.RequestException as err:
            result.status = ScrapingStatus.UNKNOWN_ERROR
            result.error_message = f"Erro na requisição: {err}"
            return result

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            element = soup.select_one(store.selector)

            if not element:
                result.status = ScrapingStatus.SELECTOR_NOT_FOUND
                result.error_message = f"Seletor CSS '{store.selector}' não encontrado na página"
                return result

            raw_text = element.get_text()
            price = parse_brl_price(raw_text)

            if price is None:
                result.status = ScrapingStatus.INVALID_PRICE
                result.error_message = f"Não foi possível converter o texto '{raw_text.strip()}' em preço válido"
                return result

            result.current_price = price
            if price <= product.target_price:
                result.status = ScrapingStatus.TARGET_REACHED
            else:
                result.status = ScrapingStatus.ABOVE_TARGET

            return result

        except Exception as err:
            result.status = ScrapingStatus.UNKNOWN_ERROR
            result.error_message = f"Erro ao processar HTML: {err}"
            return result
