"""
Unit tests for PriceHistoryDB (SQLite).
"""

import os
import pytest
from datetime import datetime, timedelta
from src.database.history import PriceHistoryDB
from src.models.product import PriceResult, ScrapingStatus

@pytest.fixture
def db(tmp_path):
    db_file = tmp_path / "test_price_history.db"
    history_db = PriceHistoryDB(db_path=str(db_file))
    return history_db


def test_save_and_retrieve_lowest_price_24h(db):
    res1 = PriceResult(
        product_id="p1",
        product_name="Ar-condicionado",
        store_key="loja1",
        store_name="Loja 1",
        target_price=1500.0,
        current_price=1450.0,
        status=ScrapingStatus.TARGET_REACHED,
        timestamp=datetime.now() - timedelta(hours=2)
    )
    res2 = PriceResult(
        product_id="p1",
        product_name="Ar-condicionado",
        store_key="loja1",
        store_name="Loja 1",
        target_price=1500.0,
        current_price=1380.0,
        status=ScrapingStatus.TARGET_REACHED,
        timestamp=datetime.now() - timedelta(hours=1)
    )

    db.save_results([res1, res2])
    lowest = db.get_lowest_price_24h("p1", "loja1")
    assert lowest == 1380.0


def test_lowest_price_ignores_older_than_24h(db):
    res_old = PriceResult(
        product_id="p1",
        product_name="Ar-condicionado",
        store_key="loja1",
        store_name="Loja 1",
        target_price=1500.0,
        current_price=1200.0,
        status=ScrapingStatus.TARGET_REACHED,
        timestamp=datetime.now() - timedelta(hours=26)
    )
    res_recent = PriceResult(
        product_id="p1",
        product_name="Ar-condicionado",
        store_key="loja1",
        store_name="Loja 1",
        target_price=1500.0,
        current_price=1400.0,
        status=ScrapingStatus.TARGET_REACHED,
        timestamp=datetime.now() - timedelta(hours=5)
    )

    db.save_results([res_old, res_recent])
    lowest = db.get_lowest_price_24h("p1", "loja1")
    assert lowest == 1400.0
