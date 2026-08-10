"""
Main application entry point.
Run using: python -m src.main
"""

import sys
from dotenv import load_dotenv
from src.config.products import PRODUCTS
from src.services.price_service import PriceService


def main():
    # Load environment variables if .env file exists
    load_dotenv()

    print("Iniciando verificação de preços...")
    service = PriceService(products=PRODUCTS)
    results = service.run_check()
    print(f"\nVerificação concluída. {len(results)} loja(s) consultada(s).")


if __name__ == "__main__":
    main()
