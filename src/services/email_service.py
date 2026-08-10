"""
Email Notifier Service.
Sends email alerts via SMTP when a product price reaches or drops below the target price.
"""

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import List
from src.services.notification_service import BaseNotifier
from src.models.product import PriceResult, ScrapingStatus
from src.utils.price_parser import format_brl_price


class EmailNotifier(BaseNotifier):
    """
    Notifier that sends email alerts via SMTP exclusively when a product price
    reaches or drops below the target price (is_target_reached == True).
    """

    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        username: str = None,
        password: str = None,
        email_to: str = None,
        enabled: bool = None
    ):
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USERNAME", "")
        self.password = password or os.getenv("SMTP_PASSWORD", "")
        self.email_to = email_to or os.getenv("EMAIL_TO", "")

        env_enabled = os.getenv("EMAIL_ENABLED", "false").lower() in ("true", "1", "yes")
        self.enabled = enabled if enabled is not None else env_enabled

    def notify(self, results: List[PriceResult]) -> None:
        if not self.enabled:
            return

        # Filter ONLY results where target price was reached (discount detected)
        matching_results = [res for res in results if res.is_target_reached]

        if not matching_results:
            return

        if not self.username or not self.password or not self.email_to:
            print("[EmailNotifier] Alerta de desconto detectado, mas credenciais SMTP não estão configuradas.")
            return

        for res in matching_results:
            self._send_email(res)

    def _send_email(self, result: PriceResult) -> None:
        msg = EmailMessage()
        subject = f"🚨 Alerta de Preço: {result.product_name} por {format_brl_price(result.current_price)}!"
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = self.email_to

        url_str = result.store_url or "#"

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
              <h2 style="color: #2e7d32;">🚨 Alerta de Desconto Encontrado!</h2>
              <p>O produto que você está monitorando atingiu o preço desejado:</p>
              
              <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr>
                  <td style="padding: 8px; font-weight: bold;">Produto:</td>
                  <td style="padding: 8px;">{result.product_name}</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                  <td style="padding: 8px; font-weight: bold;">Loja:</td>
                  <td style="padding: 8px;">{result.store_name}</td>
                </tr>
                <tr>
                  <td style="padding: 8px; font-weight: bold;">Preço Atual:</td>
                  <td style="padding: 8px; font-weight: bold; color: #2e7d32; font-size: 18px;">{format_brl_price(result.current_price)}</td>
                </tr>
                <tr style="background-color: #f9f9f9;">
                  <td style="padding: 8px; font-weight: bold;">Preço-Alvo:</td>
                  <td style="padding: 8px;">{format_brl_price(result.target_price)}</td>
                </tr>
              </table>

              <div style="margin-top: 25px; text-align: center;">
                <a href="{url_str}" style="background-color: #2e7d32; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                  Ver Produto na Loja
                </a>
              </div>
            </div>
          </body>
        </html>
        """

        msg.set_content(
            f"Alerta de Desconto!\n\n"
            f"Produto: {result.product_name}\n"
            f"Loja: {result.store_name}\n"
            f"Preço Atual: {format_brl_price(result.current_price)}\n"
            f"Preço-Alvo: {format_brl_price(result.target_price)}\n\n"
            f"Link: {url_str}"
        )
        msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"[EmailNotifier] E-mail de alerta enviado com sucesso para {self.email_to} ({result.store_name})!")
        except Exception as e:
            print(f"[EmailNotifier] Erro ao enviar e-mail de alerta: {e}")

    def send_daily_report(self, results: List[PriceResult], db_history=None) -> None:
        """
        Sends a comprehensive daily summary report via email containing:
        1. All checked products and stores with current prices and 24h lowest prices.
        2. A dedicated Health & Error Diagnostics section highlighting any selector failures, 404s, or timeouts.
        """
        if not self.enabled:
            return

        if not self.username or not self.password or not self.email_to:
            print("[EmailNotifier] Relatório diário solicitado, mas credenciais SMTP não estão configuradas.")
            return

        msg = EmailMessage()
        today_str = datetime.now().strftime("%d/%m/%Y")
        msg["Subject"] = f"📊 Relatório Diário de Preços e Saúde do Monitor ({today_str})"
        msg["From"] = self.username
        msg["To"] = self.email_to

        # Separate successful checks and errors
        error_results = [res for res in results if res.current_price is None or res.status not in (ScrapingStatus.SUCCESS, ScrapingStatus.TARGET_REACHED, ScrapingStatus.ABOVE_TARGET)]

        # Build Table Rows for Products
        table_rows_html = ""
        for res in results:
            lowest_24h = None
            if db_history:
                lowest_24h = db_history.get_lowest_price_24h(res.product_id, res.store_key)

            current_price_str = format_brl_price(res.current_price) if res.current_price is not None else "Indisponível / Erro"
            lowest_price_str = format_brl_price(lowest_24h) if lowest_24h is not None else current_price_str
            target_price_str = format_brl_price(res.target_price)

            status_badge = '<span style="color: #2e7d32; font-weight: bold;">🟢 No Preço!</span>' if res.is_target_reached else '<span style="color: #757575;">⚪ Acima do Alvo</span>'
            if res.current_price is None:
                status_badge = f'<span style="color: #c62828; font-weight: bold;">🔴 Erro: {res.status.value}</span>'

            table_rows_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
              <td style="padding: 10px;"><b>{res.product_name}</b><br><small style="color: #666;">{res.store_name}</small></td>
              <td style="padding: 10px; font-weight: bold;">{current_price_str}</td>
              <td style="padding: 10px; color: #1565c0;">{lowest_price_str}</td>
              <td style="padding: 10px;">{target_price_str}</td>
              <td style="padding: 10px;">{status_badge}</td>
            </tr>
            """

        # Build Error Section if any store failed
        error_section_html = ""
        if error_results:
            error_items_html = ""
            for err in error_results:
                url_display = err.store_url or "URL não informada"
                error_items_html += f"""
                <li style="margin-bottom: 12px;">
                  <b>Loja:</b> {err.store_name} ({err.product_name})<br>
                  <b>Tipo de Erro:</b> <code style="background-color: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 3px;">{err.status.value}</code><br>
                  <b>Mensagem:</b> {err.error_message or 'Sem detalhes'}<br>
                  <b>URL da Loja:</b> <a href="{url_display}">{url_display}</a>
                </li>
                """

            error_section_html = f"""
            <div style="margin-top: 25px; background-color: #fff3e0; border-left: 4px solid #ef6c00; padding: 15px; border-radius: 4px;">
              <h3 style="margin-top: 0; color: #e65100;">⚠️ Atenção: Diagnóstico de Erros & Seletores</h3>
              <p style="margin-bottom: 10px; color: #5d4037;">Algumas lojas apresentaram falha. Isso pode indicar que o site da loja alterou a estrutura/seletor CSS:</p>
              <ul style="padding-left: 20px; color: #3e2723;">
                {error_items_html}
              </ul>
              <p style="font-size: 12px; color: #6d4c41; margin-bottom: 0;"><i>Dica: Atualize os seletores CSS no arquivo <code>src/config/products.py</code> caso o layout da loja tenha mudado.</i></p>
            </div>
            """
        else:
            error_section_html = """
            <div style="margin-top: 25px; background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px; border-radius: 4px; color: #1b5e20;">
              <b>✅ Tudo em ordem!</b> Todas as lojas foram consultadas com sucesso sem erros de seletor.
            </div>
            """

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
            <div style="max-width: 700px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
              <h2 style="color: #1565c0; margin-bottom: 5px;">📊 Relatório Diário de Preços</h2>
              <p style="color: #666; margin-top: 0;">Resumo konsolidado de monitoramento do dia {today_str}</p>
              
              <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;">
                <thead>
                  <tr style="background-color: #f5f5f5; text-align: left;">
                    <th style="padding: 10px;">Produto / Loja</th>
                    <th style="padding: 10px;">Preço Atual</th>
                    <th style="padding: 10px;">Mínimo 24h</th>
                    <th style="padding: 10px;">Alvo</th>
                    <th style="padding: 10px;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {table_rows_html}
                </tbody>
              </table>

              {error_section_html}

              <div style="margin-top: 25px; text-align: center; font-size: 12px; color: #999;">
                Rastreador de Preços em Python • Relatório Diário Automático
              </div>
            </div>
          </body>
        </html>
        """

        msg.set_content(f"Relatório Diário de Preços - {today_str}\nConsulte a versão HTML em seu cliente de e-mail.")
        msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"[EmailNotifier] Relatório diário enviado com sucesso para {self.email_to}!")
        except Exception as e:
            print(f"[EmailNotifier] Erro ao enviar relatório diário por e-mail: {e}")

