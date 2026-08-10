"""
Unit tests for GenericScraper with mocked HTTP responses.
"""

from unittest.mock import patch, MagicMock
import requests
from src.scrapers.generic_scraper import GenericScraper
from src.models.product import ProductConfig, StoreConfig, ScrapingStatus


def create_sample_product():
    return ProductConfig(
        id="p1",
        name="Ar-condicionado Consul",
        model="CCB07GB",
        target_price=1500.00,
        stores={
            "s1": StoreConfig(
                name="Loja Teste",
                url="https://lojateste.com/p1",
                selector=".price",
                enabled=True
            )
        }
    )


@patch("requests.get")
def test_scraper_successful_extraction(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '<html><body><div class="price">R$ 1.450,00</div></body></html>'
    mock_get.return_value = mock_resp

    product = create_sample_product()
    scraper = GenericScraper()
    result = scraper.fetch_price(product, "s1", product.stores["s1"])

    assert result.current_price == 1450.00
    assert result.status == ScrapingStatus.TARGET_REACHED
    assert result.is_target_reached is True


@patch("requests.get")
def test_scraper_selector_not_found(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '<html><body><div class="other">R$ 1.450,00</div></body></html>'
    mock_get.return_value = mock_resp

    product = create_sample_product()
    scraper = GenericScraper()
    result = scraper.fetch_price(product, "s1", product.stores["s1"])

    assert result.current_price is None
    assert result.status == ScrapingStatus.SELECTOR_NOT_FOUND


@patch("requests.get")
def test_scraper_http_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_resp

    product = create_sample_product()
    scraper = GenericScraper()
    result = scraper.fetch_price(product, "s1", product.stores["s1"])

    assert result.current_price is None
    assert result.status == ScrapingStatus.HTTP_ERROR


@patch("requests.get")
def test_scraper_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection Refused")

    product = create_sample_product()
    scraper = GenericScraper()
    result = scraper.fetch_price(product, "s1", product.stores["s1"])

    assert result.current_price is None
    assert result.status == ScrapingStatus.CONNECTION_ERROR
