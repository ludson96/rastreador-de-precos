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
            "telerio": StoreConfig(
                name="Telerio",
                url="https://www.telerio.com.br/ar-condicionado-janela-consul-7500-btus-frio-eletronico-design-moderno-ccn07fb/p?idsku=1145",
                selector="[class*='spotPriceValue'], [class*='sellingPriceValue']",
                enabled=True,
                product_identifier="CCN07FB",
                scraper_type="generic"
            ),
            "mercadolivre": StoreConfig(
                name="Mercadolivre",
                url="https://www.mercadolivre.com.br/ar-condicionado-janela-manual-consul-ccb07fb-7500-btus-frio-monofasico-110-v/p/MLB27175065",
                selector=".ui-pdp-price__second-line .andes-money-amount",
                enabled=False,
                product_identifier="CCB07FB",
                scraper_type="generic"
            ),
        }
    )
]
