import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import base64


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
    "espn.com",
    "hearst.com",
    "countryliving.com",
    "foxnews.com",
    "foxweather.com"
]

GOOD_HINTS = [
    "glass beads",
    "glass bead",
    "reflective",
    "road marking",
    "traffic safety",
    "thermoplastic",
    "abrasive",
    "blasting",
    "microsphere",
    "highway",
    "marking paint"
]


def get_domain(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme + "://" + parsed.netloc


def decode_bing_url(encoded_url):
    try:
        if encoded_url.startswith("aHR0"):
            return base64.b64decode(encoded_url).decode("utf-8")
    except:
        pass
    return None


def extract_real_url(bing_url):
    try:
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(bing_url).query)
        if "u" in parsed:
            encoded = parsed["u"][0]
            if encoded.startswith("a1"):
                encoded = encoded[2:]
            real = decode_bing_url(encoded)
            if real:
                return real
    except:
        pass
    return None


def is_bad_website(url):
    url_lower = url.lower()

    if url_lower.endswith(".pdf"):
        return True

    for bad in BAD_DOMAINS:
        if bad in url_lower:
            return True

    return False


def homepage_looks_relevant(domain):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(domain, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()
        html = response.text.lower()

        combined = text + " " + html

        for hint in GOOD_HINTS:
            if hint in combined:
                return True
    except:
        pass

    return False


def clean_email(email):
    email = email.strip()
    email = email.replace("mailto:", "")
    email = urllib.parse.unquote(email)
    email = email.replace(" ", "")
    email = email.replace("(at)", "@").replace("[at]", "@").replace(" at ", "@")
    email = email.replace("(dot)", ".").replace("[dot]", ".").replace(" dot ", ".")
    return email


def search_company_websites(keyword):
    print(f"\nSearching Bing for: {keyword}")

    websites = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://www.bing.com/search?q=" + urllib.parse.quote(keyword)
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("li.b_algo h2 a"):
            href = a.get("href")
            if not href:
                continue

            real_url = None

            if "bing.com/ck/a" in href:
                real_url = extract_real_url(href)
            elif href.startswith("http"):
                real_url = href

            if real_url and not is_bad_website(real_url):
                domain = get_domain(real_url)
                websites.append(domain)

    except Exception as e:
        print("Search error:", e)

    clean_sites = []
    seen = set()
    for site in websites:
        if site not in seen:
            seen.add(site)
            clean_sites.append(site)

    relevant_sites = []
    for site in clean_sites:
        print("Checking relevance:", site)
        if homepage_looks_relevant(site):
            relevant_sites.append(site)

    relevant_sites = relevant_sites[:6]
    print("Relevant company domains:", relevant_sites)
    return relevant_sites


def get_emails_from_page(url):
    emails = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        html = response.text

        text = urllib.parse.unquote(text)
        html = urllib.parse.unquote(html)

        emails += re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)
        emails += re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", html)

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "mailto:" in href:
                emails.append(href)

    except:
        pass

    cleaned = []
    seen = set()
    for email in emails:
        e = clean_email(email)
        if "@" in e and "." in e and e not in seen:
            seen.add(e)
            cleaned.append(e)

    return cleaned


def get_contact_pages(base_url):
    pages = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            href_lower = href.lower()

            if "contact" in href_lower or "about" in href_lower:
                if href.startswith("http"):
                    pages.append(href)
                else:
                    pages.append(base_url.rstrip("/") + "/" + href.lstrip("/"))
    except:
        pass

    return list(set(pages))


def collect_leads(keywords):
    all_results = []

    for keyword in keywords:
        websites = search_company_websites(keyword)

        for site in websites:
            print("\nChecking website:", site)

            homepage_emails = get_emails_from_page(site)
            for email in homepage_emails:
                all_results.append({
                    "keyword": keyword,
                    "website": site,
                    "email": email,
                    "contact_page": site
                })

            contact_pages = get_contact_pages(site)
            for page in contact_pages:
                print("Checking contact page:", page)
                page_emails = get_emails_from_page(page)

                for email in page_emails:
                    all_results.append({
                        "keyword": keyword,
                        "website": site,
                        "email": email,
                        "contact_page": page
                    })

    unique_results = []
    seen = set()
    for row in all_results:
        key = (row["keyword"], row["website"], row["email"], row["contact_page"])
        if key not in seen:
            seen.add(key)
            unique_results.append(row)

    print("\nFinal results:")
    for row in unique_results:
        print(row)

    return unique_results
