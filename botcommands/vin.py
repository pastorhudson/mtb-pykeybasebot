import os
import random
import textwrap

import requests

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


def _money(value):
    return f"${value:,.0f}" if isinstance(value, (int, float)) else None


def _joined(*values, sep=" / "):
    parts = [str(v) for v in values if v not in (None, "")]
    return sep.join(parts) if parts else None


def _rows(pairs, label_width=15):
    """Turn (label, value) pairs into aligned lines, skipping empty values."""
    lines = []
    for label, value in pairs:
        if value in (None, ""):
            continue
        lines.append(f"{label + ':':<{label_width}}{value}")
    return lines


def build_message(data):
    b = data.get("build") or {}
    listing = data.get("latest_listing") or {}
    dealer = (listing.get("dealer") or {}) if listing else {}

    title = _joined(b.get("year"), b.get("make"), b.get("model"), b.get("trim"),
                    sep=" ") or "Unknown vehicle"

    lines = [title, f"-- VIN {data.get('vin')} ({data.get('status')}) --", ""]

    lines += _rows([
        ("Version", b.get("version")),
        ("Body", _joined(b.get("body_type"), b.get("drivetrain"))),
        ("Engine", b.get("engine")),
        ("Fuel", _joined(b.get("fuel_type"), b.get("powertrain_type"))),
        ("Trans", b.get("transmission")),
        ("Exterior", b.get("exterior_color")),
        ("Interior", b.get("interior_color")),
        ("Base MSRP", _money(b.get("base_msrp"))),
        ("Combined", _money(b.get("combined_msrp"))),
    ])

    if listing:
        miles = listing.get("miles")
        lines += ["", "-- Listing --"]
        lines += _rows([
            ("Price", _money(listing.get("price"))),
            ("Miles", f"{miles:,}" if isinstance(miles, (int, float)) else None),
            ("Type", listing.get("inventory_type")),
            ("Stock #", listing.get("stock_number")),
            ("Inv. date", listing.get("inventory_date")),
            ("Sold", listing.get("sold_date")),
            ("Dealer", dealer.get("name")),
            ("Location", _joined(dealer.get("city"), dealer.get("state"), sep=", ")),
            ("Phone", dealer.get("phone")),
            ("Listing", listing.get("vdp_url")),
        ])

    history = listing.get("price_history") or []
    if history:
        lines += ["", "-- Price History --"]
        for ev in history:
            when = (ev.get("changed_at") or "")[:10]
            change = _joined(_money(ev.get("price_before")), _money(ev.get("price_after")),
                             sep=" → ")
            miles = ev.get("miles")
            tail = f"  ({miles:,} mi)" if isinstance(miles, (int, float)) else ""
            lines.append(f"{when}  {change}{tail}")

    options = b.get("options") or []
    if options:
        lines += ["", "-- Options --"]
        for opt in options:
            name = textwrap.fill(opt.get("name") or "", width=40)
            price = _money(opt.get("msrp"))
            code = opt.get("code") or ""
            lines.append(f"{code:<4}{name}" + (f"  {price}" if price else ""))

    body = "\n".join(lines).rstrip()
    return f"```{body}```"


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

    msg = build_message(data)
    if observations:
        msg = f"{get_quip()}\n{msg}"
    return {"msg": msg}, True


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "4T1DAACKXTU765422"
    payload, found = get_vin_lookup(query, observations=False)
    print(payload["msg"])
    print(found)