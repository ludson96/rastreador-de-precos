"""
Unit tests for Brazilian Real (BRL) price string parser.
"""

import pytest
from src.utils.price_parser import parse_brl_price, format_brl_price


def test_parse_brl_price_with_currency_symbol():
    assert parse_brl_price("R$ 1.582,27") == 1582.27
    assert parse_brl_price("R$ 899,90") == 899.90
    assert parse_brl_price("R$1.500,00") == 1500.00
    assert parse_brl_price("R$ 1499,90") == 1499.90


def test_parse_brl_price_without_currency_symbol():
    assert parse_brl_price("1.582,27") == 1582.27
    assert parse_brl_price("899,90") == 899.90
    assert parse_brl_price("1500,00") == 1500.00
    assert parse_brl_price("1582.27") == 1582.27


def test_parse_brl_price_with_whitespace_and_newlines():
    assert parse_brl_price("\n  R$ 1.582,27 \t") == 1582.27
    assert parse_brl_price("Por apenas R$\u00a01.499,90 à vista") == 1499.90
    assert parse_brl_price("R$\n1.609\n,\n91") == 1609.91


def test_parse_brl_price_invalid_inputs():
    assert parse_brl_price("") is None
    assert parse_brl_price(None) is None
    assert parse_brl_price("Produto sem estoque") is None
    assert parse_brl_price("Indisponível") is None


def test_format_brl_price():
    assert format_brl_price(1582.27) == "R$ 1.582,27"
    assert format_brl_price(899.9) == "R$ 899,90"
    assert format_brl_price(1500.0) == "R$ 1.500,00"
