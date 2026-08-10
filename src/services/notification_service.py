"""
Notification Service module.
Handles output formatting for terminal display and establishes extensible interface for future alert channels (Telegram, Discord, Email).
"""

from abc import ABC, abstractmethod
from typing import List
from src.models.product import PriceResult, ScrapingStatus
from src.utils.price_parser import format_brl_price


class BaseNotifier(ABC):
    """Abstract interface for alert notifiers (Terminal, Telegram, Discord, Email)."""

    @abstractmethod
    def notify(self, results: List[PriceResult]) -> None:
        pass


class TerminalNotifier(BaseNotifier):
    """Outputs price scraping results clearly formatted to the terminal/console."""

    def notify(self, results: List[PriceResult]) -> None:
        print("\n" + "=" * 60)
        print("                PAINEL DE MONITORAMENTO DE PREÇOS             ")
        print("=" * 60 + "\n")

        for res in results:
            print(f"Produto: {res.product_name}")
            print(f"Loja: {res.store_name}")

            if res.current_price is not None:
                print(f"Preço atual: {format_brl_price(res.current_price)}")
                print(f"Preço-alvo: {format_brl_price(res.target_price)}")

                if res.is_target_reached:
                    print("Status: 🚀 PREÇO-ALVO ATINGIDO!")
                else:
                    print("Status: Acima do preço-alvo")
            else:
                print("Preço atual: N/A")
                print(f"Preço-alvo: {format_brl_price(res.target_price)}")
                print(f"Status: ERRO - {res.status.value}")
                if res.error_message:
                    print(f"Detalhes do erro: {res.error_message}")

            print("-" * 60)


class NotificationService:
    """Orchestrates all active notification channels."""

    def __init__(self, notifiers: List[BaseNotifier] = None):
        if notifiers is None:
            # Import here to prevent circular import issues
            from src.services.email_service import EmailNotifier
            self.notifiers = [TerminalNotifier(), EmailNotifier()]
        else:
            self.notifiers = notifiers

    def send_notifications(self, results: List[PriceResult]) -> None:
        for notifier in self.notifiers:
            notifier.notify(results)
