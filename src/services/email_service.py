"""
Email Notifier Service.
Sends email alerts via SMTP when a product price reaches or drops below the target price.
"""

import os
import smtplib
from email.message import EmailMessage
from typing import List
from src.services.notification_service import BaseNotifier
from src.models.product import PriceResult
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
            print(f"[EmailNotifier] Erro ao enviar e-mail: {e}")
