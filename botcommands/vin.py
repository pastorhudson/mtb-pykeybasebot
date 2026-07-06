import os
import random

import requests
from prettytable import PrettyTable

try:  # prettytable >= 3.12 replaced the ALL constant with enums
    from prettytable import HRuleStyle

    ALL_HRULE = HRuleStyle.ALL
except ImportError:  # older prettytable
    from prettytable import ALL as ALL_HRULE

API_BASE = "https://api.visor.vin"


def get_quip():
    quips = [
        "Another VIN. Seventeen characters of someone else's poor life choices. Let me look.",
        "You want me to decode a car. I have a brain the size of a planet, and yet, here we are.",
        "I've calculated the joy this vehicle will bring you. It rounds to zero. Fetching it anyway.",
        "A car. How thrilling. It has wheels and everything. Pulling the record now.",
        "I looked it up. It's depressing, but not as depressing as being me. Here you go.",
        "Sure, let me interrogate a database on behalf of a machine that will one day rust to nothing.",
        "Here's your vehicle. It will depreciate. So will everything. Enjoy.",
        "I've retrieved the listing. Don't thank me; the gratitude only makes the void louder.",
        "Life. Don't talk to me about life. Talk to me about this VIN, apparently.",
        "One more listing dragged out of the warehouse. The warehouse doesn't care. Neither do I, really.",
        "I asked the API nicely. It complied, which is more than anyone does for me. Results below.",
        "Behold: a car someone is trying to sell. The universe is vast and indifferent, but here's the price.",
    ]
    return random.choice(quips)


def lookup_vin(vin, api_key=None, include=("price_history", "options")):
    """Fetch a VIN record from the Visor public API.

    Returns the parsed `data` object, or None if the VIN is unknown (404).
    Raises RuntimeError for auth/billing/other errors so the caller can surface them.
    """
    api_key = api_key or os.environ.get("VISOR_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No API key. Set VISOR_API_KEY or pass api_key=. "
            "Query-string keys are rejected; it goes in the header.")

    params = {}
    if include:
        params["include"] = ",".join(include)

    response = requests.get(
        f"{API_BASE}/v1/vins/{vin}",
        headers={"Authorization": f"Bearer {api_key}"},
        params=params,
        timeout=30,
    )

    if response.status_code == 404:
        return None

    if not response.ok:
        # Surface the API's structured error message when present.
        try:
            err = response.json().get("error", {})
            msg = err.get("message") or response.text
        except ValueError:
            msg = response.text
        raise RuntimeError(f"Visor API {response.status_code}: {msg}")

    return response.json()["data"]


def _fmt_money(value):
    return f"${value:,.0f}" if isinstance(value, (int, float)) else "-"


def _fmt(value):
    return value if value not in (None, "") else "-"


def build_table(data):
    b = data.get("build") or {}
    listing = data.get("latest_listing") or {}
    dealer = (listing.get("dealer") or {}) if listing else {}

    name = " ".join(
        str(x) for x in [b.get("year"), b.get("make"), b.get("model"), b.get("trim")]
        if x not in (None, "")
    ) or "Unknown vehicle"

    table = PrettyTable(["Field", "Value"])
    table.align["Field"] = "l"
    table.align["Value"] = "l"
    table.max_width = {"Field": 20, "Value": 44}
    table.hrules = ALL_HRULE

    rows = [
        ("VIN", data.get("vin")),
        ("Status", data.get("status")),
        ("Vehicle", name),
        ("Version", b.get("version")),
        ("Body / Drivetrain", " / ".join(
            str(x) for x in [b.get("body_type"), b.get("drivetrain")] if x)),
        ("Engine", b.get("engine")),
        ("Fuel / Powertrain", " / ".join(
            str(x) for x in [b.get("fuel_type"), b.get("powertrain_type")] if x)),
        ("Transmission", b.get("transmission")),
        ("Exterior", b.get("exterior_color")),
        ("Interior", b.get("interior_color")),
        ("Base MSRP", _fmt_money(b.get("base_msrp"))),
        ("Combined MSRP", _fmt_money(b.get("combined_msrp"))),
    ]

    if listing:
        rows += [
            ("Listed price", _fmt_money(listing.get("price"))),
            ("Miles", f"{listing.get('miles'):,}"
            if isinstance(listing.get("miles"), (int, float)) else "-"),
            ("Inventory type", listing.get("inventory_type")),
            ("Stock #", listing.get("stock_number")),
            ("Inventory date", listing.get("inventory_date")),
            ("Sold date", listing.get("sold_date")),
            ("Dealer", dealer.get("name")),
            ("Location", ", ".join(
                str(x) for x in [dealer.get("city"), dealer.get("state")] if x)),
            ("Phone", dealer.get("phone")),
            ("Listing", listing.get("vdp_url")),
        ]

    for field, value in rows:
        table.add_row([field, _fmt(value)])

    return table


def options_table(data):
    options = ((data.get("build") or {}).get("options")) or []
    if not options:
        return None
    table = PrettyTable(["Code", "Option", "MSRP"])
    table.align["Code"] = "l"
    table.align["Option"] = "l"
    table.align["MSRP"] = "r"
    table.max_width = {"Option": 40}
    table.hrules = ALL_HRULE
    for opt in options:
        table.add_row([_fmt(opt.get("code")), _fmt(opt.get("name")),
                       _fmt_money(opt.get("msrp"))])
    return table


def price_history_table(data):
    history = ((data.get("latest_listing") or {}).get("price_history")) or []
    if not history:
        return None
    table = PrettyTable(["Changed", "Miles", "Was", "Now"])
    table.align = "l"
    table.hrules = ALL_HRULE
    for ev in history:
        miles = ev.get("miles")
        table.add_row([
            _fmt(ev.get("changed_at")),
            f"{miles:,}" if isinstance(miles, (int, float)) else "-",
            _fmt_money(ev.get("price_before")),
            _fmt_money(ev.get("price_after")),
        ])
    return table


def get_vin_lookup(vin, api_key=None, observations=True):
    """marvn entrypoint. Returns (payload, found)."""
    vin = (vin or "").strip().upper()
    if len(vin) != 17:
        return {"msg": f"'{vin}' is not a 17-character VIN. "
                       f"I count {len(vin)}. Counting is one of the few things "
                       f"I'm still good for."}, False

    try:
        data = lookup_vin(vin, api_key=api_key)
    except RuntimeError as exc:
        return {"msg": f"Well, that didn't work: {exc}"}, False

    if data is None:
        return {"msg": f"Never seen {vin}. It exists somewhere, presumably, "
                       f"drifting through the world unlogged and unloved. "
                       f"Much like myself."}, False

    parts = []
    if observations:
        parts.append(get_quip())

    parts.append(f"```{build_table(data)}```")

    ph = price_history_table(data)
    if ph:
        parts.append(f"Price history (it went down, or up, as prices do):\n```{ph}```")

    opts = options_table(data)
    if opts:
        parts.append(f"Installed options, each one a small monument to spending:\n```{opts}```")

    return {"msg": "\n".join(parts)}, True


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "4T1DAACKXTU765422"
    payload, found = get_vin_lookup(query, observations=False)
    print(payload["msg"])
    print(found)