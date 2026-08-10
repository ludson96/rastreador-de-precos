"""
Unit tests for Product model and target price logic.
"""

from src.models.product import PriceResult, ScrapingStatus


def test_target_reached_when_lower():
    res = PriceResult(
        product_id="test",
        product_name="Test Product",
        store_key="store1",
        store_name="Store 1",
        target_price=1500.00,
        current_price=1499.90,
        status=ScrapingStatus.TARGET_REACHED
    )
    assert res.is_target_reached is True


def test_target_reached_when_equal():
    res = PriceResult(
        product_id="test",
        product_name="Test Product",
        store_key="store1",
        store_name="Store 1",
        target_price=1500.00,
        current_price=1500.00,
        status=ScrapingStatus.TARGET_REACHED
    )
    assert res.is_target_reached is True


def test_target_not_reached_when_higher():
    res = PriceResult(
        product_id="test",
        product_name="Test Product",
        store_key="store1",
        store_name="Store 1",
        target_price=1500.00,
        current_price=1582.27,
        status=ScrapingStatus.ABOVE_TARGET
    )
    assert res.is_target_reached is False


def test_target_not_reached_when_price_none():
    res = PriceResult(
        product_id="test",
        product_name="Test Product",
        store_key="store1",
        store_name="Store 1",
        target_price=1500.00,
        current_price=None,
        status=ScrapingStatus.HTTP_ERROR
    )
    assert res.is_target_reached is False
