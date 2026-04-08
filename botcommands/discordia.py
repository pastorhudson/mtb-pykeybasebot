# !/usr/bin/env python3
import re
import requests

DEFAULT_URL = "https://archive.org/stream/PrincipiaDiscordia_201806/Principia%20Discordia_djvu.txt"


def _clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # nuke extra spaces but keep newlines kinda
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _find_section(text: str, ref: str):
    """
    ref rules (simple, caveman-safe):
      - "all" => whole book
      - "L200-L260" => line range (1-based, inclusive)
      - any other text => find first line that contain ref (case-insensitive),
                         then return ~N lines after it.
    """
    if not ref or ref.lower() == "all":
        return ("Principia Discordia (full)", text)

    m = re.match(r"^\s*[Ll](\d+)\s*-\s*[Ll](\d+)\s*$", ref)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        if a <= 0 or b <= 0 or b < a:
            return ("Error", "Error: bad line range. Use like L200-L260.")
        lines = text.splitlines()
        # 1-based to 0-based
        a0 = max(0, a - 1)
        b0 = min(len(lines), b)
        chunk = "\n".join(lines[a0:b0]).strip()
        return (f"Principia Discordia lines {a}-{b}", chunk)

    # string search mode
    lines = text.splitlines()
    needle = ref.strip().lower()
    for i, line in enumerate(lines):
        if needle in line.lower():
            start = max(0, i - 2)
            end = min(len(lines), i + 140)  # ~140 lines after hit
            chunk = "\n".join(lines[start:end]).strip()
            return (f'Principia Discordia (match: "{ref}")', chunk)

    return ("Error", f'Error: no find for "{ref}". Try line range like L200-L260, or "all".')


def get_discordia_text(
        ref="all",
        *,
        url=DEFAULT_URL,
        plain_txt=False,
        timeout=20,
        max_chars=6000,
        user_agent="Mozilla/5.0",
):
    """
    Like get_bg_text(), but for Principia Discordia raw txt on archive.org.

    ref:
      - "all"
      - "L200-L260"
      - or search string like "Hail Eris" (grab block near first hit)

    max_chars: keep bot from spew too much.
    """
    headers = {"User-Agent": user_agent, "Accept-Language": "en-US,en;q=0.9"}

    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching Discordia text: {e}"

    text = _clean_text(r.text)
    title, body = _find_section(text, ref)

    if title == "Error":
        return body

    if not body:
        return "Error: empty chunk."

    if max_chars and len(body) > max_chars:
        body = body[:max_chars].rstrip() + "\n\n...[cut]..."

    out = f"{title}\n```{body}```"
    if plain_txt:
        return out
    return f"{out}"

if __name__ == "__main__":
    print(get_discordia_text("Hail Eris"))