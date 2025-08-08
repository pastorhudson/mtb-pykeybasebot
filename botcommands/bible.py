#!/usr/bin/env python

import sys
import requests
from bs4 import BeautifulSoup
import re


def _clean_text(html_fragment, keep_verse_numbers=True):
    """Normalize whitespace and optionally keep verse numbers."""
    # Remove footnotes, crossrefs, headings, and verse anchors
    for sel in [
        '.footnotes', '.footnote', '.crossrefs', '.publisher-info-bottom',
        '.passage-other-trans', '.passage-display-bcv',
        '.footnote-refs', '.inline-crossrefs', '.bcv',
        '.versenum + sup'  # stray footnote markers next to versenum
    ]:
        for el in html_fragment.select(sel):
            el.decompose()

    # Verse numbers on BG are in <sup class="versenum">#
    if not keep_verse_numbers:
        for el in html_fragment.select('sup.versenum'):
            el.decompose()
    else:
        # add a thin space after verse numbers so "16For" doesn't jam
        for el in html_fragment.select('sup.versenum'):
            el.string = (el.get_text(strip=True) + ' ')

    text = html_fragment.get_text(separator=' ', strip=True)
    # Collapse excessive spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_bg_text(passage, version='ESV', plain_txt=False, keep_verse_numbers=True, timeout=15):
    """
    Fetch a Bible passage from Bible Gateway.

    Args:
        passage (str): e.g., "John 3:16-18"
        version (str): e.g., "ESV", "NIV", "KJV", "CSB", "NET", "VOICE", etc.
        plain_txt (bool): if True, no code fences / version suffix.
        keep_verse_numbers (bool): keep verse numbers in the output.
        timeout (int): request timeout in seconds.

    Returns:
        str: formatted passage text or an error string.
    """
    # BibleGateway renders passages at this endpoint:
    url = "https://www.biblegateway.com/passage/"

    headers = {
        # BG is picky; a normal UA avoids edge cases
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    params = {
        "search": passage,
        "version": version,
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching passage from Bible Gateway: {e}"

    soup = BeautifulSoup(r.text, "html.parser")

    # Primary container(s) for passage text on BG:
    # - div.passage-content / div.passage-text
    # backup selectors included for markup variations
    containers = soup.select("div.passage-content div.passage-text")
    if not containers:
        containers = soup.select("div.passage-text") or soup.select("div.result-text-style-normal")
    if not containers:
        # Try to extract any error hint BibleGateway shows
        err = soup.select_one("div.alert, p.warning, p.notice")
        hint = err.get_text(" ", strip=True) if err else "Passage not found."
        return f"\"{passage}\" not found for version '{version}'. {hint}"

    # Multiple containers happen when the passage spans chapters
    parts = []
    # Grab the reference/title that BG shows (nice to include as header)
    ref_el = soup.select_one("div.passage-content h1, h1.passage-display")
    ref_title = ref_el.get_text(" ", strip=True) if ref_el else passage

    for c in containers:
        # Each container may have <div class="publisher-info-bottom"> with copyright; remove above
        text = _clean_text(c, keep_verse_numbers=keep_verse_numbers)
        if text:
            parts.append(text)

    body = "\n\n".join(parts).strip()
    if not body:
        return f"\"{passage}\" returned empty content in version '{version}'."

    if plain_txt:
        return f"{ref_title}\n{body}"
    else:
        return f"```{ref_title}\n{body}```\n\n({version})"


if __name__ == "__main__":
    # Example usage
    print(get_bg_text("Proverbs 23", version="VOICE"))
    print(get_bg_text("John 3:16-18", version="ESV"))
