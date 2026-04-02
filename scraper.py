def search_company_websites(keyword):
    print(f"\nSearching Bing for: {keyword}")

    websites = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(keyword)

    response = requests.get(url, headers=headers, timeout=10)
    print("Status:", response.status_code)
    print("HTML length:", len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")

    # 先找 li.b_algo
    results = soup.find_all("li", {"class": "b_algo"})
    print("b_algo count:", len(results))

    for result in results:
        a = result.find("a")
        if not a:
            continue
        href = a.get("href")
        if href and href.startswith("http") and not is_bad_website(href):
            websites.append(get_domain(href))

    # 如果没抓到，再退一步：打印前20个http链接看看
    if not websites:
        print("\nFallback: first 20 http links found on page:")
        count = 0
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if href.startswith("http"):
                print(href)
                count += 1
                if count >= 20:
                    break

    clean_sites = []
    seen = set()
    for site in websites:
        if site not in seen:
            seen.add(site)
            clean_sites.append(site)

    relevant_sites = clean_sites[:5]
    print("Relevant company domains:", relevant_sites)
    return relevant_sites
