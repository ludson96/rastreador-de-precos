"""
Unit tests for EmailNotifier.
Verifies that emails are dispatched ONLY when price drops below or reaches target price.
"""

from unittest.mock import patch, MagicMock
from src.services.email_service import EmailNotifier
from src.models.product import PriceResult, ScrapingStatus


def create_result(price: float, target: float = 1500.00, status: ScrapingStatus = ScrapingStatus.SUCCESS):
    return PriceResult(
        product_id="p1",
        product_name="Ar-condicionado Consul",
        store_key="consul",
        store_name="Consul Oficial",
        store_url="https://consul.com.br/p1",
        target_price=target,
        current_price=price,
        status=status
    )


@patch("smtplib.SMTP")
def test_email_sent_when_target_reached(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    notifier = EmailNotifier(
        smtp_server="smtp.example.com",
        smtp_port=587,
        username="user@example.com",
        password="secretpassword",
        email_to="alert@example.com",
        enabled=True
    )

    results = [create_result(price=1450.00, target=1500.00)]
    notifier.notify(results)

    assert mock_server.starttls.called
    mock_server.login.assert_called_with("user@example.com", "secretpassword")
    assert mock_server.send_message.called


@patch("smtplib.SMTP")
def test_email_not_sent_when_price_above_target(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    notifier = EmailNotifier(
        smtp_server="smtp.example.com",
        smtp_port=587,
        username="user@example.com",
        password="secretpassword",
        email_to="alert@example.com",
        enabled=True
    )

    results = [create_result(price=1582.27, target=1500.00)]
    notifier.notify(results)

    assert not mock_server.send_message.called


@patch("smtplib.SMTP")
def test_email_not_sent_on_scraping_error(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    notifier = EmailNotifier(
        smtp_server="smtp.example.com",
        smtp_port=587,
        username="user@example.com",
        password="secretpassword",
        email_to="alert@example.com",
        enabled=True
    )

    result_error = PriceResult(
        product_id="p1",
        product_name="Ar-condicionado Consul",
        store_key="consul",
        store_name="Consul Oficial",
        target_price=1500.00,
        current_price=None,
        status=ScrapingStatus.HTTP_ERROR
    )

    notifier.notify([result_error])
    assert not mock_server.send_message.called


@patch("smtplib.SMTP")
def test_email_not_sent_when_disabled(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    notifier = EmailNotifier(
        smtp_server="smtp.example.com",
        smtp_port=587,
        username="user@example.com",
        password="secretpassword",
        email_to="alert@example.com",
        enabled=False
    )

    results = [create_result(price=1400.00, target=1500.00)]
    notifier.notify(results)

    assert not mock_server.send_message.called
