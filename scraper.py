import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import base64


BAD_DOMAINS = [
    "bing.com","google.com","youtube.com","facebook.com","instagram.com",
    "linkedin.com","twitter.com","x.com","wikipedia.org","amazon.com",
    "ebay.com","stackoverflow.com","mozilla.org","microsoft.com",
    "espn.com","hearst.com","countryliving.com","foxnews.com","foxweather.com",
    "tripadvisor.com","opentable.com","footlocker.com","timesofindia.com",
    "geeksforgeeks.org","beebom.com","howtogeek.com","androidauthority.com",
    "sammobile.com"
]

BAD_EMAILS = [
    "example.com",
    "yourname@",
    "name@company",
    "test@",
    "demo@",
    "sample@"
]


def get_domain(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme + "://" + parsed.netloc


def is_bad_website(url):
    url_lower = url.lower()
    for bad in BAD_DOMAINS:
        if bad in url_lower:
            return True
    return False


def clean_email(email):
    email = email.strip()
    email = email.replace("mailto:", "")
    email = urllib.parse.unquote(email)
    email = email.replace(" ", "")
    email = email.replace("(at)", "@").replace("[at]", "@").replace(" at ", "@")
    email = email.replace("(dot)", ".").replace("[dot]", ".").replace(" dot ", ".")

    email_lower = email.lower()

    # 过滤图片资源
    bad_endings = [".jpg",".jpeg",".png",".webp",".gif",".svg",".avif",".css",".js",".ico",".pdf",".mp4"]
    for ending in bad_endings:
        if email_lower.endswith(ending):
            return ""

    # 过滤假邮箱
    for bad in BAD_EMAILS:
        if bad in email_lower:
            return ""

    if email.count("@") != 1:
        return ""

    if "." not in email.split("@")[1]:
        return ""

    return email


def search_company_websites(keyword):
    print(f"\nSearching Bing for: {keyword}")

    websites = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(keyword)
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.select("li.b_algo h2 a"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("http") and not is_bad_website(href):
            websites.append(get_domain(href))

    clean_sites = []
    seen = set()
    for site in websites:
        if site not in seen:
            seen.add(site)
            clean_sites.append(site)

    relevant_sites = clean_sites[:5]
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
        if e and e not in seen:
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
            href = link["href"].lower()
            if "contact" in href or "about" in href:
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
                    "phone": "",
                    "country": "",
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
                        "phone": "",
                        "country": "",
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
