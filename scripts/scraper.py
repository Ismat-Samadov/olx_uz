import asyncio
import aiohttp
import json
import csv
import re
from pathlib import Path

BASE_URL = "https://www.olx.uz/nedvizhimost/"
TOTAL_PAGES = 3
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "data.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
}

CSV_FIELDS = ["title", "price", "currency", "location", "url", "image", "valid_until"]


def extract_listings(html: str) -> list[dict]:
    """Parse all application/ld+json blocks and extract Offer items."""
    listings = []
    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    for raw in scripts:
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue

        # Flatten: data may be a single object or a list
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            offers = _collect_offers(node)
            listings.extend(offers)

    return listings


def _collect_offers(node) -> list[dict]:
    """Recursively collect Offer objects from a JSON-LD node."""
    results = []
    if not isinstance(node, dict):
        return results

    node_type = node.get("@type", "")

    if node_type == "Offer":
        results.append(_parse_offer(node))
    elif node_type in ("Product", "ItemList"):
        # Product may wrap an Offer inside 'offers'
        offers_field = node.get("offers")
        if offers_field:
            for o in (offers_field if isinstance(offers_field, list) else [offers_field]):
                results.extend(_collect_offers(o))
        # ItemList has 'itemListElement'
        for element in node.get("itemListElement", []):
            results.extend(_collect_offers(element.get("item", element)))
    else:
        # Walk all dict values
        for value in node.values():
            if isinstance(value, (dict, list)):
                items = value if isinstance(value, list) else [value]
                for item in items:
                    results.extend(_collect_offers(item))

    return results


def _parse_offer(offer: dict) -> dict:
    area = offer.get("areaServed", {})
    location = area.get("name", "") if isinstance(area, dict) else str(area)

    images = offer.get("image", [])
    image = images[0] if isinstance(images, list) and images else (images or "")

    return {
        "title": offer.get("name", "").strip(),
        "price": offer.get("price", ""),
        "currency": offer.get("priceCurrency", "UZS"),
        "location": location,
        "url": offer.get("url", ""),
        "image": image,
        "valid_until": offer.get("priceValidUntil", ""),
    }


async def fetch_page(session: aiohttp.ClientSession, page: int) -> str:
    url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"
    async with session.get(url, headers=HEADERS, allow_redirects=True) as resp:
        resp.raise_for_status()
        return await resp.text()


async def scrape(pages: int = TOTAL_PAGES) -> list[dict]:
    connector = aiohttp.TCPConnector(limit=5)
    timeout = aiohttp.ClientTimeout(total=30)
    cookie_jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, cookie_jar=cookie_jar
    ) as session:
        tasks = [fetch_page(session, p) for p in range(1, pages + 1)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_listings = []
    for page_num, result in enumerate(results, start=1):
        if isinstance(result, Exception):
            print(f"[page {page_num}] error: {result}")
            continue
        listings = extract_listings(result)
        print(f"[page {page_num}] found {len(listings)} listings")
        all_listings.extend(listings)

    return all_listings


def save_csv(listings: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(listings)
    print(f"Saved {len(listings)} rows → {path}")


async def main():
    listings = await scrape(TOTAL_PAGES)
    if listings:
        save_csv(listings, OUTPUT_PATH)
    else:
        print("No listings found.")


if __name__ == "__main__":
    asyncio.run(main())
