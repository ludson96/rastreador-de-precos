"""
Utility module for parsing and formatting Brazilian currency strings (BRL).
"""

import re
from typing import Optional


def parse_brl_price(raw_price_str: str) -> Optional[float]:
    """
    Parses a raw price string into a float, supporting Brazilian format (BRL).

    Examples:
        - "R$ 1.582,27" -> 1582.27
        - "1.582,27"    -> 1582.27
        - "R$ 899,90"   -> 899.90
        - "899,90"      -> 899.90
        - "1582.27"     -> 1582.27
        - "R$ 1.500"    -> 1500.00
    """
    if not raw_price_str:
        return None

    # Clean up currency symbols, spaces, line breaks, and text wrappers
    text = raw_price_str.replace("\n", "").replace("\r", "").replace("\xa0", " ").strip()

    # Find the numeric price substring
    match = re.search(r'(\d+(?:[\.,]\d+)*)', text)
    if not match:
        return None

    number_str = match.group(1)

    # Standardize BRL numbers (comma as decimal separator, dot as thousands separator)
    if "," in number_str and "." in number_str:
        if number_str.rfind(",") > number_str.rfind("."):
            # Format: 1.582,27 -> 1582.27
            number_str = number_str.replace(".", "").replace(",", ".")
        else:
            # Format: 1,582.27 -> 1582.27
            number_str = number_str.replace(",", "")
    elif "," in number_str:
        # Format: 1499,90 or 899,90 -> 1499.90
        number_str = number_str.replace(",", ".")
    elif "." in number_str:
        parts = number_str.split(".")
        # If dot is thousands separator e.g. 1.500 (3 trailing digits)
        if len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) <= 3:
            number_str = "".join(parts)

    try:
        val = float(number_str)
        return round(val, 2)
    except ValueError:
        return None


def format_brl_price(value: float) -> str:
    """
    Formats a float value to Brazilian Real string.
    Example: 1582.27 -> "R$ 1.582,27"
    """
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"
