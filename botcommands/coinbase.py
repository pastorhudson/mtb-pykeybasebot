from pprint import pprint

import requests

CURRENCY_CODES = {
    # Major global currencies
    "USD": {"name": "US Dollar", "symbol": "$", "numeric": "840"},
    "EUR": {"name": "Euro", "symbol": "€", "numeric": "978"},
    "GBP": {"name": "British Pound", "symbol": "£", "numeric": "826"},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "numeric": "392"},
    "CHF": {"name": "Swiss Franc", "symbol": "Fr", "numeric": "756"},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "numeric": "036"},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "numeric": "124"},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "numeric": "156"},
    "INR": {"name": "Indian Rupee", "symbol": "₹", "numeric": "356"},
    "BRL": {"name": "Brazilian Real", "symbol": "R$", "numeric": "986"},
    "RUB": {"name": "Russian Ruble", "symbol": "₽", "numeric": "643"},
    "KRW": {"name": "South Korean Won", "symbol": "₩", "numeric": "410"},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$", "numeric": "702"},
    "NZD": {"name": "New Zealand Dollar", "symbol": "NZ$", "numeric": "554"},
    "MXN": {"name": "Mexican Peso", "symbol": "$", "numeric": "484"},
    "HKD": {"name": "Hong Kong Dollar", "symbol": "HK$", "numeric": "344"},
    "TRY": {"name": "Turkish Lira", "symbol": "₺", "numeric": "949"},
    "ZAR": {"name": "South African Rand", "symbol": "R", "numeric": "710"},
    "SEK": {"name": "Swedish Krona", "symbol": "kr", "numeric": "752"},
    "NOK": {"name": "Norwegian Krone", "symbol": "kr", "numeric": "578"},
    "DKK": {"name": "Danish Krone", "symbol": "kr", "numeric": "208"},
    "PLN": {"name": "Polish Złoty", "symbol": "zł", "numeric": "985"},

    # Cryptocurrency codes (not official ISO 4217 but commonly used)
    "BTC": {"name": "Bitcoin", "symbol": "₿", "numeric": ""},
    "ETH": {"name": "Ethereum", "symbol": "Ξ", "numeric": ""},
    "XLM": {"name": "Stellar Lumen", "symbol": "*", "numeric": ""},

    # Precious metals
    "XAU": {"name": "Gold (troy ounce)", "symbol": "", "numeric": "959"},
    "XAG": {"name": "Silver (troy ounce)", "symbol": "", "numeric": "961"},
    "XPT": {"name": "Platinum (troy ounce)", "symbol": "", "numeric": "962"},
    "XPD": {"name": "Palladium (troy ounce)", "symbol": "", "numeric": "964"},

    # Additional common currencies
    "AED": {"name": "UAE Dirham", "symbol": "د.إ", "numeric": "784"},
    "THB": {"name": "Thai Baht", "symbol": "฿", "numeric": "764"},
    "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp", "numeric": "360"},
    "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "numeric": "458"},
    "PHP": {"name": "Philippine Peso", "symbol": "₱", "numeric": "608"},
    "TWD": {"name": "New Taiwan Dollar", "symbol": "NT$", "numeric": "901"},
    "ILS": {"name": "Israeli New Shekel", "symbol": "₪", "numeric": "376"},
    "SAR": {"name": "Saudi Riyal", "symbol": "﷼", "numeric": "682"},
    "ARS": {"name": "Argentine Peso", "symbol": "$", "numeric": "032"},
    "CLP": {"name": "Chilean Peso", "symbol": "$", "numeric": "152"},
    "COP": {"name": "Colombian Peso", "symbol": "$", "numeric": "170"},
    "PEN": {"name": "Peruvian Sol", "symbol": "S/", "numeric": "604"},
    "EGP": {"name": "Egyptian Pound", "symbol": "E£", "numeric": "818"},
    "NGN": {"name": "Nigerian Naira", "symbol": "₦", "numeric": "566"},
    "VND": {"name": "Vietnamese Dong", "symbol": "₫", "numeric": "704"},
}



def get_spot_price(pair: str = 'XLM-USD') -> float:
    """
    Return the spot price for the requested trading pair from Coinbase.

    Parameters
    ----------
    pair : str
        Trading pair in the form BASE-CURRENCY, e.g. 'BTC-USD'.
        If the dash is omitted, '-USD' is assumed.
    """
    if "-" not in pair:
        pair = f"{pair}-USD"

    url = f"https://api.coinbase.com/v2/prices/{pair.upper()}/spot"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()['data']
    pprint(data)
    curency_symbol = CURRENCY_CODES[data['currency']]['symbol']
    return f"{data['base'].upper()} {curency_symbol}{float(data["amount"])}"

if __name__ == "__main__":
    # main(sys.argv[1:])
    price = get_spot_price()
    print(price)


