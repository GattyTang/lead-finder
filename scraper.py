import requests
from bs4 import BeautifulSoup


def search_company_websites(keyword):
    print("Searching Bing for:", keyword)

    websites = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://www.bing.com/search?q=" + keyword
        response = requests.get(url, headers=headers, timeout=10)

        print("Status code:", response.status_code)
        print("Page length:", len(response.text))

        soup = BeautifulSoup(response.text, "html.parser")

        for li in soup.select("li.b_algo h2 a"):
            href = li.get("href")
            if href and href.startswith("http"):
                websites.append(href)

    except Exception as e:
        print("Search error:", e)

    websites = list(dict.fromkeys(websites))[:10]
    print("Websites found:", websites)
    return websites


if __name__ == "__main__":
    keyword = "glass beads manufacturer"
    search_company_websites(keyword)
