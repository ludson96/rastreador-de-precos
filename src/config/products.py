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
            "fastshop": StoreConfig(
                name="Fast Shop",
                url="https://site.fastshop.com.br/ar-condicionado-janela-7500-btus-consul-frio-com-design-moderno---ccb07gb-170153-180363/p",
                selector="[class*='OfferList_PriceFormat'], .price",
                enabled=True,
                product_identifier="CCB07GB",
                scraper_type="generic"
            ),
        }
    )
]
