"""
Scrape IndiGo campaign pages via sitemap.
Avoids bot detection by fetching XML sitemap first, then individual pages.
"""
import sys
import re
import time
import httpx
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.database import init_db, upsert_campaign

SITEMAP_URLS = [
    "https://www.goindigo.in/sitemap.xml",
    "https://www.goindigo.in/campaigns/sitemap.xml",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Known campaign URLs from search results as fallback
KNOWN_CAMPAIGNS = [
    "https://www.goindigo.in/campaigns/indigo-offers.html",
    "https://www.goindigo.in/campaigns/destinations-of-the-week-offers.html",
    "https://www.goindigo.in/campaigns/family-and-friends-offer.html",
    "https://www.goindigo.in/campaigns/indigo-stretch-offers.html",
    "https://www.goindigo.in/campaigns/indigo-offers/payzapp-offer.html",
    "https://www.goindigo.in/campaigns/6e-social-offer-terms-and-conditions.html",
    "https://www.goindigo.in/campaigns/indigo-citi.html",
]


def get_campaign_urls_from_sitemap(client: httpx.Client) -> list[str]:
    """Try to find campaign URLs from IndiGo's sitemap."""
    urls = []
    for sitemap_url in SITEMAP_URLS:
        try:
            print(f"Trying sitemap: {sitemap_url}")
            r = client.get(sitemap_url, timeout=15)
            if r.status_code != 200:
                print(f"  got {r.status_code}, skipping")
                continue
            root = ET.fromstring(r.text)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            # Handle both sitemap index and regular sitemap
            for loc in root.findall(".//sm:loc", ns):
                url = loc.text.strip()
                if "/campaigns/" in url and url.endswith(".html"):
                    urls.append(url)
                # If it's a sitemap index, fetch sub-sitemaps
                elif "sitemap" in url.lower() and "campaign" in url.lower():
                    try:
                        r2 = client.get(url, timeout=15)
                        root2 = ET.fromstring(r2.text)
                        for loc2 in root2.findall(".//sm:loc", ns):
                            u = loc2.text.strip()
                            if "/campaigns/" in u and u.endswith(".html"):
                                urls.append(u)
                    except Exception as e:
                        print(f"  sub-sitemap error: {e}")
        except Exception as e:
            print(f"  error: {e}")
    return list(set(urls))


def extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML without BeautifulSoup."""
    # Remove script and style blocks
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL)
    # Remove HTML tags
    html = re.sub(r"<[^>]+>", " ", html)
    # Decode common entities
    html = html.replace("&amp;", "&").replace("&nbsp;", " ") \
               .replace("&lt;", "<").replace("&gt;", ">") \
               .replace("&#39;", "'").replace("&quot;", '"')
    # Collapse whitespace
    html = re.sub(r"\s+", " ", html).strip()
    return html


def extract_title(html: str) -> str:
    """Extract page title from HTML."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        # Remove " | IndiGo" suffix
        title = re.sub(r"\s*\|\s*IndiGo.*$", "", title).strip()
        return title
    return ""


def extract_promo_codes(text: str) -> str:
    """Pull promo codes from text."""
    patterns = [
        r"promo code[:\s'\"]+([A-Z0-9]{4,15})",
        r"coupon code[:\s'\"]+([A-Z0-9]{4,15})",
        r"code[:\s'\"]+([A-Z0-9]{4,15})",
        r"'([A-Z0-9]{4,15})'",
    ]
    codes = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            code = match.group(1).upper()
            if len(code) >= 4:
                codes.add(code)
    return ",".join(codes)


def scrape_url(client: httpx.Client, url: str, slug: str) -> dict | None:
    """Fetch and parse a single campaign page."""
    try:
        r = client.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} — skipping")
            return None

        html = r.text
        title = extract_title(html)
        body_text = extract_text_from_html(html)

        # Filter to meaningful content (skip navigation/footer noise)
        # Keep sentences with offer-related keywords
        offer_keywords = ["offer", "discount", "cashback", "promo", "deal",
                          "save", "off", "booking", "flight", "fare", "coupon"]
        sentences = [s.strip() for s in body_text.split(".") if len(s.strip()) > 30]
        relevant = [s for s in sentences
                    if any(kw in s.lower() for kw in offer_keywords)]
        offer_text = ". ".join(relevant[:30])  # cap at 30 sentences

        if not offer_text:
            offer_text = body_text[:1000]

        promo_codes = extract_promo_codes(body_text)

        return {
            "id": slug,
            "name": title or slug.replace("-", " ").title(),
            "url": url,
            "offer_text": offer_text[:3000],
            "promo_codes": promo_codes,
        }
    except Exception as e:
        print(f"  error: {e}")
        return None


def main():
    print("Initialising database...")
    init_db()

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        # Try sitemap first
        print("\nLooking for campaign URLs in sitemap...")
        campaign_urls = get_campaign_urls_from_sitemap(client)

        # Fall back to known URLs if sitemap yields nothing
        if not campaign_urls:
            print("  sitemap yielded no campaign URLs, using known list")
            campaign_urls = KNOWN_CAMPAIGNS
        else:
            print(f"  found {len(campaign_urls)} campaign URLs in sitemap")
            # Merge with known ones
            all_urls = set(campaign_urls) | set(KNOWN_CAMPAIGNS)
            campaign_urls = list(all_urls)

        print(f"\nScraping {len(campaign_urls)} campaign pages...")
        saved = 0
        for i, url in enumerate(campaign_urls):
            slug = url.rstrip("/").split("/")[-1].replace(".html", "")
            # skip the index page itself
            if slug in ("indigo-offers", "campaigns"):
                continue
            print(f"[{i+1}/{len(campaign_urls)}] {slug}")
            data = scrape_url(client, url, slug)
            if data:
                upsert_campaign(data)
                print(f"  saved: {data['name'][:60]}")
                saved += 1
            time.sleep(0.5)  # polite delay

    print(f"\nDone. Saved {saved} campaigns.")
    print("Run scripts/embed_campaigns.py next.")


if __name__ == "__main__":
    main()