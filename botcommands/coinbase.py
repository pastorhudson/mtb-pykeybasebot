import requests



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

    return f"{data['base'].upper()} ${float(data["amount"])}"

if __name__ == "__main__":
    # main(sys.argv[1:])
    price = get_spot_price()
    print(price)


