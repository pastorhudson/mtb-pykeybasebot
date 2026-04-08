# !/usr/bin/env python3
"""
discordia.py - fetch sections from the Principia Discordia (HTML edition)

Can read from a local file path or a URL.
Requires: requests, beautifulsoup4
"""
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString

DEFAULT_FILE = Path('./storage/discordia.htm')

DEFAULT_URL = "https://www.cs.cmu.edu/~tilt/principia/body.html"


# ---------------------------------------------------------------------------
# HTML -> structured sections
# ---------------------------------------------------------------------------

def _node_to_text(node) -> str:
    """Convert a single BS4 node to plain text."""
    if isinstance(node, NavigableString):
        return str(node)
    if node.name == "pre":
        for img in node.find_all("img"):
            img.decompose()
        return "\n" + node.get_text() + "\n"
    if node.name in ("h1", "h2", "h3", "h4"):
        return "\n\n" + node.get_text(strip=True).upper() + "\n"
    if node.name == "p":
        # Preserve <br> as newlines within paragraphs (important for dialogue)
        parts = []
        for child in node.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif child.name == "br":
                parts.append("\n")
            else:
                parts.append(child.get_text())
        text = "".join(parts).strip()
        return ("\n" + text + "\n") if text else ""
    if node.name in ("div",):
        return "\n" + node.get_text(separator=" ", strip=True) + "\n"
    if node.name == "li":
        return "\n  - " + node.get_text(separator=" ", strip=True)
    if node.name == "blockquote":
        lines = node.get_text(separator="\n", strip=True).splitlines()
        return "\n" + "\n".join("  > " + l for l in lines) + "\n"
    if node.name == "br":
        return "\n"
    return node.get_text(separator=" ")


def _first_heading(nodes) -> str | None:
    """Return the text of the first heading node in a list, or None."""
    for n in nodes:
        if not isinstance(n, NavigableString) and n.name in ("h1", "h2", "h3", "h4"):
            return n.get_text(strip=True)
    return None


def _extract_sections(html: str) -> list[dict]:
    """
    Parse the HTML body and split into sections at every <hr> tag.
    Each section dict has {"title": str, "body": str}.
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body") or soup

    # Collect all top-level children
    nodes = list(body.children)

    sections = []
    current_title = "Introduction"
    current_nodes = []

    def flush():
        parts = [_node_to_text(n) for n in current_nodes]
        text = re.sub(r"\n{3,}", "\n\n", "".join(parts)).strip()
        if text:
            # If title is still a placeholder, grab first heading from body
            title = current_title
            if title == "—":
                title = _first_heading(current_nodes) or "—"
            sections.append({"title": title, "body": text})
        current_nodes.clear()

    for node in nodes:
        if isinstance(node, NavigableString):
            if node.strip():
                current_nodes.append(node)
            continue

        if node.name == "hr":
            flush()
            current_title = "—"
            continue

        current_nodes.append(node)

    flush()
    return sections


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------

def _load_html(filepath=None, url=None, timeout=20, user_agent="Mozilla/5.0") -> str:
    if filepath:
        with open(filepath, "r", encoding="windows-1252", errors="replace") as f:
            return f.read()
    headers = {"User-Agent": user_agent, "Accept-Language": "en-US,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_discordia_text(
        ref="all",
        *,
        filepath=DEFAULT_FILE,
        url=DEFAULT_URL,
        timeout=20,
        max_chars=6000,
        user_agent="Mozilla/5.0",
) -> str:
    """
    Return text from the Principia Discordia.

    Reads from `filepath` if set (default: local HTM file).
    Falls back to fetching `url` if filepath is None.

    ref:
      - "all"          => full text of every section
      - search string  => section(s) whose text contains ref (case-insensitive)
    """
    try:
        html = _load_html(
            filepath=filepath,
            url=url if not filepath else None,
            timeout=timeout,
            user_agent=user_agent,
        )
    except (OSError, requests.RequestException) as e:
        return f"Error loading Discordia text: {e}"

    sections = _extract_sections(html)

    if not ref or ref.lower() == "all":
        full = "\n\n---\n\n".join(f"{s['title']}\n\n{s['body']}" for s in sections)
        body = re.sub(r"\n{3,}", "\n\n", full).strip()
        title = "Principia Discordia (full)"
    else:
        needle = ref.strip().lower()
        matches = [
            s for s in sections
            if needle in s["title"].lower() or needle in s["body"].lower()
        ]
        if not matches:
            return (
                f'Error: no section found for "{ref}". '
                'Try a phrase from the text, or "all".'
            )
        body = re.sub(
            r"\n{3,}", "\n\n",
            "\n\n---\n\n".join(f"{s['title']}\n\n{s['body']}" for s in matches),
        ).strip()
        title = (
            f'Principia Discordia (match: "{ref}")'
            if len(matches) == 1
            else f'Principia Discordia ({len(matches)} sections matching "{ref}")'
        )

    if max_chars and len(body) > max_chars:
        body = body[:max_chars].rstrip() + "\n\n...[cut]..."

    return f"{title}\n```\n{body}\n```"


if __name__ == "__main__":
    print(get_discordia_text("Is Eris True?"))
