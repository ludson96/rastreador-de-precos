"""
Product Catalog Configuration.
Centralized product registry containing target prices, product models, voltage options, and store URLs/selectors.
"""

from typing import List
from src.models.product import ProductConfig, StoreConfig

PRODUCTS: List[ProductConfig] = [
    ProductConfig(
        id="consul_ccb07gb",
        name="Ar-condicionado de Janela Consul 7.500 BTUs Frio",
        model="CCB07GB",
        capacity="7500 BTU",
        voltage="110V / 220V",
        target_price=1500.00,
        enabled=True,
        stores={
            "consul_oficial": StoreConfig(
                name="Consul Oficial",
                url="https://www.consul.com.br/ar-condicionado-de-janela-consul-7500-btus-frio-ccb07gb/p",
                selector=".price-sales, .vtex-product-price-1-x-currencyInteger, .consul-product-price",
                enabled=True,
                product_identifier="CCB07GB",
                scraper_type="generic"
            ),
            "magalu": StoreConfig(
                name="Magazine Luiza",
                url="https://www.magazineluiza.com.br/ar-condicionado-de-janela-consul-7500-btus-frio-ccb07gb/p/237248100/ar/arja/",
                selector="[data-testid='price-value'], .price-template__text",
                enabled=True,
                product_identifier="237248100",
                scraper_type="generic"
            ),
            "casas_bahia": StoreConfig(
                name="Casas Bahia",
                url="https://www.casasbahia.com.br/ar-condicionado-janela-consul-7500-btus-frio-ccb07gb/p/55056708",
                selector="#product-price, .product-price-value",
                enabled=False,  # Disabled example
                product_identifier="55056708",
                scraper_type="generic"
            )
        }
    )
]
