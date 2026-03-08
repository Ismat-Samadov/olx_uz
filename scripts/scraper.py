"""
OLX.uz real estate scraper.
Uses curl_cffi (Chrome TLS fingerprint) for HTTP and asyncio for concurrency.
Parses listing cards from HTML using BeautifulSoup.
Output: data/data.csv
"""

import asyncio
import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession

BASE_URL = "https://www.olx.uz/nedvizhimost/"
TOTAL_PAGES = 25
BATCH_SIZE = 5  # concurrent requests per batch
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "data.csv"
OLX_ORIGIN = "https://www.olx.uz"

HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
}

CSV_FIELDS = ["id", "title", "price", "currency", "location", "date", "url", "image"]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_price(raw: str) -> tuple[str, str]:
    """Return (price_digits, currency)."""
    raw = _clean(raw)
    # Strip HTML tags
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = _clean(raw)
    # Currency symbols
    for sym, code in [("сум", "UZS"), ("$", "USD"), ("€", "EUR")]:
        if sym in raw:
            digits = re.sub(r"[^\d]", "", raw.split(sym)[0])
            return digits, code
    # Fallback: everything that isn't a digit → currency suffix
    digits = re.sub(r"[^\d]", "", raw)
    return digits, "UZS"


def extract_listings(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all(attrs={"data-cy": "l-card"})
    results = []
    seen_ids: set[str] = set()

    for card in cards:
        card_id = card.get("id", "")
        if card_id in seen_ids:
            continue
        seen_ids.add(card_id)

        # --- URL ---
        link_tag = card.find("a", href=True)
        href = link_tag["href"] if link_tag else ""
        # Strip query params for a clean URL
        clean_href = href.split("?")[0]
        url = OLX_ORIGIN + clean_href if clean_href.startswith("/") else clean_href

        # --- Title ---
        title_el = card.find(attrs={"data-cy": "ad-card-title"})
        title = ""
        if title_el:
            h_tag = title_el.find(re.compile(r"^h\d$"))
            title = _clean(h_tag.get_text(" ") if h_tag else title_el.get_text(" "))

        # --- Price ---
        price_el = card.find(attrs={"data-testid": "ad-price"})
        price_raw = price_el.get_text(" ") if price_el else ""
        price, currency = parse_price(price_raw)

        # --- Location & Date ---
        loc_el = card.find(attrs={"data-testid": "location-date"})
        location, date = "", ""
        if loc_el:
            parts = [_clean(p) for p in loc_el.get_text(" - ").split(" - ") if _clean(p)]
            location = parts[0] if parts else ""
            date = parts[1] if len(parts) > 1 else ""

        # --- Image ---
        img_tag = card.find("img")
        image = ""
        if img_tag:
            image = img_tag.get("src") or img_tag.get("data-src") or ""

        results.append({
            "id": card_id,
            "title": title,
            "price": price,
            "currency": currency,
            "location": location,
            "date": date,
            "url": url,
            "image": image,
        })

    return results


# ---------------------------------------------------------------------------
# Async fetching
# ---------------------------------------------------------------------------

async def fetch_page(session: AsyncSession, page: int) -> tuple[int, str]:
    url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
    resp = await session.get(url, headers=HEADERS)
    resp.raise_for_status()
    return page, resp.text


async def scrape(pages: int = TOTAL_PAGES) -> list[dict]:
    page_results: list[tuple[int, str]] = []

    async with AsyncSession(impersonate="chrome120") as session:
        # Page 1 first to warm up cookies
        page_results.append(await fetch_page(session, 1))
        print(f"[page 1] fetched")

        # Remaining pages in batches to avoid rate limiting
        remaining = list(range(2, pages + 1))
        for batch_start in range(0, len(remaining), BATCH_SIZE):
            batch = remaining[batch_start : batch_start + BATCH_SIZE]
            results = await asyncio.gather(
                *[fetch_page(session, p) for p in batch],
                return_exceptions=True,
            )
            for p, r in zip(batch, results):
                if isinstance(r, Exception):
                    print(f"[page {p}] error: {r}")
                else:
                    page_results.append(r)
                    print(f"[page {p}] fetched")

    all_listings: list[dict] = []
    seen_ids: set[str] = set()

    for page_num, html in sorted(page_results):
        listings = extract_listings(html)
        new = [l for l in listings if l["id"] not in seen_ids]
        seen_ids.update(l["id"] for l in new)
        print(f"[page {page_num}] found {len(listings)} cards, {len(new)} unique")
        all_listings.extend(new)

    return all_listings


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_csv(listings: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(listings)
    print(f"Saved {len(listings)} rows -> {path}")


async def main():
    listings = await scrape()
    if listings:
        save_csv(listings, OUTPUT_PATH)
    else:
        print("No listings found.")


if __name__ == "__main__":
    asyncio.run(main())
