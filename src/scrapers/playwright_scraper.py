"""
Playwright Scraper implementation using headless Firefox browser.
Extracts product prices from pages requiring JavaScript execution (e.g. Mercado Livre).
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from src.scrapers.base import BaseScraper
from src.models.product import ProductConfig, StoreConfig, PriceResult, ScrapingStatus
from src.utils.price_parser import parse_brl_price


class PlaywrightScraper(BaseScraper):
    """
    Scraper utilizing Playwright sync API with Firefox browser engine for dynamic client-rendered web pages.
    """

    def __init__(self, timeout: int = 15000, headless: bool = True):
        self.timeout = timeout
        self.headless = headless

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
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) "
                        "Gecko/20100101 Firefox/128.0"
                    ),
                    viewport={"width": 1366, "height": 768},
                    locale="pt-BR"
                )
                page = context.new_page()

                try:
                    page.goto(store.url, wait_until="load", timeout=self.timeout)
                    
                    # Aguarda o elemento de preço aparecer na página
                    element = page.wait_for_selector(store.selector, timeout=self.timeout)
                    
                    if not element:
                        result.status = ScrapingStatus.SELECTOR_NOT_FOUND
                        result.error_message = f"Seletor CSS '{store.selector}' não encontrado após aguardar o carregamento."
                        browser.close()
                        return result

                    raw_text = element.inner_text()
                    price = parse_brl_price(raw_text)

                    if price is None:
                        result.status = ScrapingStatus.INVALID_PRICE
                        result.error_message = f"Não foi possível converter o texto '{raw_text.strip()}' em preço válido"
                        browser.close()
                        return result

                    result.current_price = price
                    if price <= product.target_price:
                        result.status = ScrapingStatus.TARGET_REACHED
                    else:
                        result.status = ScrapingStatus.ABOVE_TARGET

                    browser.close()
                    return result

                except PlaywrightTimeoutError:
                    result.status = ScrapingStatus.TIMEOUT
                    result.error_message = f"Timeout ({self.timeout}ms) aguardando pelo elemento '{store.selector}'"
                    browser.close()
                    return result

        except Exception as err:
            result.status = ScrapingStatus.UNKNOWN_ERROR
            result.error_message = f"Erro ao executar Playwright: {err}"
            return result
