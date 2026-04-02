import requests
from bs4 import BeautifulSoup
import re


def get_emails_from_website(url):
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

    return list(set(emails))


def search_company_websites(keyword):
    print("Searching companies for:", keyword)

    # 模拟一些公司网站（后面我们再做真正搜索）
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
        print("Checking:", site)
        emails = get_emails_from_website(site)
        print("Emails found:", emails)
