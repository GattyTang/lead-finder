import random
import re
import time
import urllib.parse
from typing import Dict, Iterable, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup

from config import (
    BLOCKED_EMAIL_PREFIXES,
    COUNTRY_HINTS,
    DISPOSABLE_EMAIL_DOMAINS,
    EMAIL_BLACKLIST_PARTS,
    ENABLE_HOMEPAGE_SCRAPE,
    FREE_EMAIL_DOMAINS,
    GENERIC_EMAIL_PREFIXES,
    MAX_CONTACT_PAGES,
    MAX_LEADS_PER_KEYWORD,
    MAX_RESULTS_PER_ENGINE,
    REQUEST_TIMEOUT,
    SEARCH_ENGINES,
)
from database import normalize_key

BAD_DOMAINS = [
    "bing.com",
    "google.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "wikipedia.org",
    "amazon.com",
    "ebay.com",
    "stackoverflow.com",
    "mozilla.org",
    "microsoft.com",
    "duckduckgo.com",
    "yelp.com",
    "mapquest.com",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

EMAIL_REGEX = r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"


# ------------ helpers ------------
def sleep_briefly(a: float = 0.8, b: float = 1.6) -> None:
    time.sleep(random.uniform(a, b))


def get_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def hostname_only(url_or_domain: str) -> str:
    parsed = urllib.parse.urlparse(url_or_domain if "://" in url_or_domain else f"https://{url_or_domain}")
    return parsed.netloc.lower().removeprefix("www.")


def is_bad_website(url: str) -> bool:
    url_lower = url.lower()
    if url_lower.endswith(".pdf"):
        return True
    return any(bad in url_lower for bad in BAD_DOMAINS)


def fetch_html(url: str) -> Optional[str]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def _parse_ddg_href(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    if "duckduckgo.com/l/?" in href:
        parsed = urllib.parse.urlparse(href)
        q = urllib.parse.parse_qs(parsed.query)
        uddg = q.get("uddg", [""])[0]
        if uddg:
            return urllib.parse.unquote(uddg)
    return href


def dedupe_sites(urls: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    clean: List[str] = []
    for url in urls:
        domain = get_domain(url)
        if not domain or is_bad_website(domain):
            continue
        key = domain.lower().rstrip("/")
        if key not in seen:
            seen.add(key)
            clean.append(domain)
    return clean


# ------------ search engines ------------
def search_duckduckgo(keyword: str) -> List[str]:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(keyword)
    html = fetch_html(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    sites: List[str] = []
    for a in soup.select("a.result__a, a[href]"):
        href = a.get("href")
        if not href:
            continue
        real = _parse_ddg_href(href)
        sites.append(real)
    return dedupe_sites(sites)[:MAX_RESULTS_PER_ENGINE]


def search_bing(keyword: str) -> List[str]:
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(keyword)
    html = fetch_html(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    sites: List[str] = []
    for a in soup.select("li.b_algo h2 a, a[href]"):
        href = a.get("href")
        if href:
            sites.append(href)
    return dedupe_sites(sites)[:MAX_RESULTS_PER_ENGINE]


def search_google(keyword: str) -> List[str]:
    # Note: public Google HTML markup changes frequently and may require proxy/API in production.
    url = "https://www.google.com/search?hl=en&q=" + urllib.parse.quote(keyword)
    html = fetch_html(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    sites: List[str] = []

    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if href.startswith("/url?"):
            parsed = urllib.parse.urlparse(href)
            real = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
            if real:
                sites.append(real)
        elif href.startswith("http"):
            sites.append(href)
    return dedupe_sites(sites)[:MAX_RESULTS_PER_ENGINE]


def search_company_websites(keyword: str) -> Dict[str, Set[str]]:
    searchers = {
        "duckduckgo": search_duckduckgo,
        "bing": search_bing,
        "google": search_google,
    }
    mapping: Dict[str, Set[str]] = {}
    for engine in SEARCH_ENGINES:
        fn = searchers.get(engine)
        if not fn:
            continue
        print(f"\nSearching {engine} for: {keyword}")
        try:
            urls = fn(keyword)
        except Exception as exc:
            print(f"{engine} search error: {exc}")
            urls = []
        print(f"{engine} hits: {urls}")
        for site in urls:
            mapping.setdefault(site, set()).add(engine)
        sleep_briefly()
    return mapping


# ------------ company and email extraction ------------
def clean_email(email: str) -> str:
    email = urllib.parse.unquote(email.strip())
    email = email.replace("mailto:", "")
    email = email.replace(" ", "")
    email = email.replace("(at)", "@").replace("[at]", "@").replace(" at ", "@")
    email = email.replace("(dot)", ".").replace("[dot]", ".").replace(" dot ", ".")

    email_lower = email.lower().strip(".,;:)]")
    bad_endings = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".css", ".js", ".ico", ".pdf", ".mp4",
        ".woff", ".woff2", ".ttf", ".eot",
    ]
    if any(email_lower.endswith(ext) for ext in bad_endings):
        return ""
    if any(part in email_lower for part in EMAIL_BLACKLIST_PARTS):
        return ""
    if email_lower.count("@") != 1:
        return ""
    local, domain = email_lower.split("@")
    if not local or "." not in domain:
        return ""
    if local in BLOCKED_EMAIL_PREFIXES or domain in DISPOSABLE_EMAIL_DOMAINS:
        return ""
    return email_lower


def assess_email_quality(email: str, website: str) -> Tuple[str, str]:
    email = email.lower()
    local, domain = email.split("@")
    site_domain = hostname_only(website)

    reasons: List[str] = []
    score = 0

    if domain == site_domain:
        score += 3
        reasons.append("same_domain")
    elif domain in FREE_EMAIL_DOMAINS:
        score -= 1
        reasons.append("free_mailbox")
    else:
        reasons.append("third_party_domain")

    if local in GENERIC_EMAIL_PREFIXES:
        score += 0
        reasons.append("generic_prefix")
    else:
        score += 2
        reasons.append("person_like_prefix")

    if any(token in local for token in ["sales", "purchase", "procurement", "export", "marketing"]):
        score += 1
        reasons.append("commercial_role")

    if any(token in local for token in ["privacy", "gdpr", "career", "job", "hr"]):
        score -= 2
        reasons.append("non_sales_role")

    if score >= 4:
        return "high", "; ".join(reasons)
    if score >= 2:
        return "medium", "; ".join(reasons)
    return "low", "; ".join(reasons)


def extract_company_name(base_url: str, html: Optional[str] = None) -> str:
    html = html or fetch_html(base_url)
    host = hostname_only(base_url)
    fallback = host.split(".")[0].replace("-", " ").replace("_", " ").title()
    if not html:
        return fallback

    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []

    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    if title:
        candidates.append(title)

    for selector in ["meta[property='og:site_name']", "meta[name='application-name']", "h1", ".logo", ".site-title"]:
        tag = soup.select_one(selector)
        if not tag:
            continue
        if tag.name == "meta":
            text = (tag.get("content") or "").strip()
        else:
            text = tag.get_text(" ", strip=True)
        if text:
            candidates.append(text)

    cleaned_candidates: List[str] = []
    for value in candidates:
        value = re.sub(r"\s+", " ", value)
        value = re.split(r"\||-|::|/", value)[0].strip()
        if 2 <= len(value) <= 80 and not any(bad in value.lower() for bad in ["contact", "welcome", "home"]):
            cleaned_candidates.append(value)

    return cleaned_candidates[0] if cleaned_candidates else fallback


def get_emails_from_page(url: str) -> List[str]:
    emails: List[str] = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = urllib.parse.unquote(soup.get_text(" ", strip=True))
        html = urllib.parse.unquote(response.text)

        emails += re.findall(EMAIL_REGEX, text)
        emails += re.findall(EMAIL_REGEX, html)

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("mailto:"):
                emails.append(href)
    except Exception:
        return []

    cleaned: List[str] = []
    seen = set()
    for email in emails:
        e = clean_email(email)
        if e and e not in seen:
            seen.add(e)
            cleaned.append(e)
    return cleaned


def get_contact_pages(base_url: str) -> List[str]:
    pages: List[str] = []
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            href_lower = href.lower()
            if any(token in href_lower for token in [
                "contact", "about", "enquiry", "inquiry", "company", "team", "sales", "support",
            ]):
                if href.startswith("http"):
                    pages.append(href)
                else:
                    pages.append(base_url.rstrip("/") + "/" + href.lstrip("/"))
    except Exception:
        return []

    seen = set()
    out: List[str] = []
    for page in pages:
        if page not in seen:
            seen.add(page)
            out.append(page)
    return out[:MAX_CONTACT_PAGES]


def _country_from_keyword(keyword: str) -> str:
    keyword_lower = keyword.lower()
    for c in COUNTRY_HINTS:
        if c in keyword_lower:
            return c.title()
    return ""


def _lead_row(keyword: str, site: str, email: str, country: str, contact_page: str, company_name: str, engines: Set[str]) -> Dict[str, str]:
    quality, quality_reason = assess_email_quality(email, site)
    return {
        "company_name": company_name,
        "keyword": keyword,
        "website": site,
        "email": email,
        "email_quality": quality,
        "email_quality_reason": quality_reason,
        "phone": "",
        "country": country,
        "contact_page": contact_page,
        "search_source": ", ".join(sorted(engines)),
        "source_count": str(len(engines)),
    }


def collect_leads(
    keywords: List[str],
    existing_keys: Optional[Set[Tuple[str, str]]] = None,
) -> List[Dict[str, str]]:
    all_results: List[Dict[str, str]] = []
    existing_keys = existing_keys or set()
    seen_run: Set[Tuple[str, str]] = set()

    for keyword in keywords:
        site_map = search_company_websites(keyword)
        country = _country_from_keyword(keyword)
        added_for_keyword = 0

        for site, engines in site_map.items():
            if added_for_keyword >= MAX_LEADS_PER_KEYWORD:
                break

            print("\nChecking website:", site)
            homepage_html = fetch_html(site) if ENABLE_HOMEPAGE_SCRAPE else None
            company_name = extract_company_name(site, homepage_html)

            homepage_emails = get_emails_from_page(site) if ENABLE_HOMEPAGE_SCRAPE else []
            for email in homepage_emails:
                key = normalize_key(site, email)
                if key in existing_keys or key in seen_run:
                    continue
                seen_run.add(key)
                all_results.append(_lead_row(keyword, site, email, country, site, company_name, engines))
                added_for_keyword += 1
                if added_for_keyword >= MAX_LEADS_PER_KEYWORD:
                    break

            if added_for_keyword >= MAX_LEADS_PER_KEYWORD:
                continue

            for page in get_contact_pages(site):
                print("Checking contact page:", page)
                for email in get_emails_from_page(page):
                    key = normalize_key(site, email)
                    if key in existing_keys or key in seen_run:
                        continue
                    seen_run.add(key)
                    all_results.append(_lead_row(keyword, site, email, country, page, company_name, engines))
                    added_for_keyword += 1
                    if added_for_keyword >= MAX_LEADS_PER_KEYWORD:
                        break
                sleep_briefly(0.5, 1.0)
                if added_for_keyword >= MAX_LEADS_PER_KEYWORD:
                    break

    unique_results: List[Dict[str, str]] = []
    seen = set()
    for row in all_results:
        key = (
            row["keyword"], row["website"], row["email"], row["contact_page"], row.get("search_source", "")
        )
        if key not in seen:
            seen.add(key)
            unique_results.append(row)

    unique_results.sort(key=lambda r: (int(r.get("source_count", "0") or 0), r.get("email_quality", "")), reverse=True)

    print("\nFinal new results:")
    for row in unique_results:
        print(row)
    return unique_results
