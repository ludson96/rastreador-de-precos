"""
Main application entry point.
Run regular check: python -m src.main
Run daily report: python -m src.main --daily-report
"""

import sys
import argparse
from dotenv import load_dotenv
from src.config.products import PRODUCTS
from src.services.price_service import PriceService


def main():
    parser = argparse.ArgumentParser(description="Rastreador de Preços de Produtos")
    parser.add_argument("--daily-report", action="store_true", help="Executa a verificação e envia o relatório diário por e-mail")
    args = parser.parse_args()

    # Load environment variables if .env file exists
    load_dotenv()

    mode_text = "com envio de Relatório Diário" if args.daily_report else "em modo monitoramento comum"
    print(f"Iniciando verificação de preços ({mode_text})...")

    service = PriceService(products=PRODUCTS)
    results = service.run_check(send_daily_report=args.daily_report)
    print(f"\nVerificação concluída. {len(results)} loja(s) consultada(s).")


if __name__ == "__main__":
    main()

