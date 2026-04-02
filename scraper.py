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

        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)

        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:
                emails.append(link["href"].replace("mailto:", "").strip())

        text_fixed = text.replace(" [at] ", "@").replace("(at)", "@").replace(" at ", "@")
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text_fixed)

    except:
        pass

    return list(set(emails))


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
    print("Searching Google for:", keyword)

    websites = []
    try:
        url = "https://www.bing.com/search?q=" + keyword
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "http" in href and "bing" not in href:
                websites.append(href)

    except:
        pass

    return list(set(websites))[:5]


if __name__ == "__main__":
    keyword = "glass beads manufacturer"

    websites = search_company_websites(keyword)

    for site in websites:
        print("\nChecking website:", site)

        emails = get_emails_from_page(site)

        contact_pages = get_contact_pages(site)
        for page in contact_pages:
            print("Checking contact page:", page)
            emails += get_emails_from_page(page)

        emails = list(set(emails))
        print("Emails found:", emails)
