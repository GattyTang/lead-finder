import requests
from bs4 import BeautifulSoup
import re


def get_emails_from_page(url):
    emails = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(" ", strip=True)
        html = response.text

        # 普通邮箱
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)

        # mailto 邮箱
        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:
                emails.append(link["href"].replace("mailto:", "").strip())

        # 处理 [at] 写法
        text_fixed = text.replace(" [at] ", "@").replace("(at)", "@").replace(" at ", "@")
        emails += re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text_fixed)

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


def search_company_websites(keyword):
    print("Searching Bing for:", keyword)

    websites = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://www.bing.com/search?q=" + keyword
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("http") and "bing.com" not in href:
                websites.append(href)

    except Exception as e:
        print("Search error:", e)

    websites = list(set(websites))[:5]
    print("Websites found:", websites)
    return websites


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
