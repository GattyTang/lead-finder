import requests
from bs4 import BeautifulSoup
import re


def get_emails_from_page(url):
    emails = []
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        html = response.text

        emails_from_text = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )
        emails_from_html = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            html
        )

        emails = list(set(emails_from_text + emails_from_html))
    except:
        pass

    return emails


def get_contact_pages(base_url):
    pages = []
    try:
        response = requests.get(base_url, timeout=5)
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


def search_company_websites(keyword):
    print("Searching companies for:", keyword)

    websites = [
        "https://www.3m.com",
        "https://www.swarco.com",
        "https://www.pqcorp.com"
    ]

    return websites


if __name__ == "__main__":
    keyword = "glass beads manufacturer"

    websites = search_company_websites(keyword)

    for site in websites:
        print("\nChecking website:", site)

        # 首页邮箱
        emails = get_emails_from_page(site)

        # Contact页面邮箱
        contact_pages = get_contact_pages(site)
        for page in contact_pages:
            print("Checking contact page:", page)
            emails += get_emails_from_page(page)

        emails = list(set(emails))
        print("Emails found:", emails)
