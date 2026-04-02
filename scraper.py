import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import base64
import csv


def decode_bing_url(encoded_url):
    try:
        if encoded_url.startswith("aHR0"):
            decoded = base64.b64decode(encoded_url).decode("utf-8")
            return decoded
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


def search_company_websites(keyword):
    print("Searching Bing for:", keyword)

    websites = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://www.bing.com/search?q=" + keyword
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("li.b_algo h2 a"):
            href = a.get("href")
            if not href:
                continue

            if "bing.com/ck/a" in href:
                real_url = extract_real_url(href)
                if real_url:
                    websites.append(real_url)
            elif href.startswith("http"):
                websites.append(href)

    except Exception as e:
        print("Search error:", e)

    websites = list(dict.fromkeys(websites))[:5]
    print("Real websites found:", websites)
    return websites


def get_emails_from_page(url):
    emails = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        html = response.text

        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)

        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:
                emails.append(link["href"].replace("mailto:", "").strip())

    except:
        pass

    return list(set(emails))


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


def save_results_to_csv(results, filename="leads.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["website", "email", "contact_page"])

        for row in results:
            writer.writerow([row["website"], row["email"], row["contact_page"]])

    print(f"\nSaved results to {filename}")


if __name__ == "__main__":
    keyword = "glass beads manufacturer"

    websites = search_company_websites(keyword)
    all_results = []

    for site in websites:
        print("\nChecking website:", site)

        # 先查首页
        emails = get_emails_from_page(site)
        for email in emails:
            all_results.append({
                "website": site,
                "email": email,
                "contact_page": site
            })

        # 再查 contact/about 页面
        contact_pages = get_contact_pages(site)
        for page in contact_pages:
            print("Checking contact page:", page)
            page_emails = get_emails_from_page(page)

            for email in page_emails:
                all_results.append({
                    "website": site,
                    "email": email,
                    "contact_page": page
                })

    # 去重
    unique_results = []
    seen = set()
    for row in all_results:
        key = (row["website"], row["email"], row["contact_page"])
        if key not in seen:
            seen.add(key)
            unique_results.append(row)

    print("\nFinal results:")
    for row in unique_results:
        print(row)

    save_results_to_csv(unique_results)
